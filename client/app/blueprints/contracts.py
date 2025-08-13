from app.forms.contract_forms import (
    ContractRenewalForm,
    ContractSearchForm,
    ContractTerminationForm,
    ContractUpdateForm,
)
from app.services.contract_service import ContractService
from app.utils.decorators import admin_required, management_required, student_required
from app.utils.pagination import Pagination
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

contracts_bp = Blueprint("contracts", __name__)


@contracts_bp.route("/my-contract")
@login_required
@student_required
def my_contract():
    """Display student's contract"""
    try:
        result = ContractService.get_contracts(page=1)

        if result.get("success") and result.get("data", {}).get("contracts"):
            contract = result["data"]["contracts"][
                0
            ]  # Student should only have one active contract
            return render_template(
                "contracts/student_contract.html",
                contract=contract,
                title="Hợp đồng của tôi",
            )
        else:
            flash("Bạn chưa có hợp đồng nào.", "info")
            return render_template(
                "contracts/student_contract.html",
                contract=None,
                title="Hợp đồng của tôi",
            )
    except Exception as e:
        flash(f"Lỗi khi tải thông tin hợp đồng: {str(e)}", "error")
        return redirect(url_for("dashboard.index"))


@contracts_bp.route("/")
@login_required
@management_required
def list_contracts():
    """Display contracts list page"""
    search_form = ContractSearchForm()

    # Get parameters
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    search = request.args.get("search", "")

    # Pre-fill form
    if status:
        search_form.status.data = status
    if search:
        search_form.search.data = search

    # Get contracts with filters
    try:
        result = ContractService.get_contracts(
            page=page, status=status if status else None
        )

        print(f"Contracts API response: {result}")  # Debugging line

        contracts = result.get("data", []).get("contracts", [])

        # Create pagination object from API response
        pagination_data = result.get("pagination", {})
        if (
            "pages" not in pagination_data
            and "total" in pagination_data
            and "per_page" in pagination_data
        ):
            total = pagination_data.get("total", 0)
            per_page = pagination_data.get("per_page", 10)
            pagination_data["pages"] = (
                (total + per_page - 1) // per_page if per_page > 0 else 1
            )

        pagination = Pagination.from_dict(pagination_data)
    except Exception as e:
        flash(f"Lỗi khi tải danh sách hợp đồng: {str(e)}", "danger")
        contracts = []
        pagination = Pagination.create_empty()

    return render_template(
        "contracts/list.html",
        contracts=contracts,
        pagination=pagination,
        form=search_form,
        title="Quản lý hợp đồng",
    )


@contracts_bp.route("/<int:contract_id>")
@login_required
@management_required
def view_contract(contract_id):
    """View contract details page"""
    try:
        contract_data = ContractService.get_contract(contract_id)

        if contract_data.get("success"):
            contract = contract_data.get("data", {}).get("contract")
            if not contract:
                flash("Không tìm thấy thông tin hợp đồng", "danger")
                return redirect(url_for("contracts.list_contracts"))

            return render_template(
                "contracts/detail.html",
                contract=contract,
                title=f"Hợp đồng {contract.get('contract_code', '#'+str(contract_id))}",
            )
        else:
            flash(
                f"Lỗi khi lấy thông tin hợp đồng: {contract_data.get('message', 'Lỗi không xác định')}",
                "danger",
            )
            return redirect(url_for("contracts.list_contracts"))

    except Exception as e:
        flash(f"Lỗi khi lấy thông tin hợp đồng: {str(e)}", "danger")
        return redirect(url_for("contracts.list_contracts"))


@contracts_bp.route("/<int:contract_id>/ajax")
@login_required
@management_required
def get_contract(contract_id):
    """Get contract details - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        # Non-AJAX requests should redirect to detail page
        return redirect(url_for("contracts.view_contract", contract_id=contract_id))

    try:
        contract_data = ContractService.get_contract(contract_id)

        if contract_data.get("success"):
            return jsonify({"success": True, "contract": contract_data.get("contract")})
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": contract_data.get("error", "Lỗi không xác định"),
                    }
                ),
                404,
            )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Lỗi khi lấy thông tin hợp đồng: {str(e)}",
                }
            ),
            500,
        )


@contracts_bp.route("/<int:contract_id>/edit", methods=["POST"])
@login_required
@admin_required
def update_contract_ajax(contract_id):
    """Update contract - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return redirect(url_for("contracts.list_contracts"))

    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("end_date"):
            return (
                jsonify({"success": False, "message": "Ngày kết thúc là bắt buộc"}),
                400,
            )

        update_data = {"end_date": data["end_date"]}

        result = ContractService.update_contract(contract_id, update_data)

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": result.get("message", "Cập nhật hợp đồng thành công"),
                    "contract": result.get("contract"),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("error", "Lỗi không xác định"),
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Lỗi khi cập nhật hợp đồng: {str(e)}"}
            ),
            500,
        )


@contracts_bp.route("/<int:contract_id>/renew", methods=["POST"])
@login_required
@admin_required
def renew_contract_ajax(contract_id):
    """Renew contract - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return redirect(url_for("contracts.list_contracts"))

    try:
        data = request.get_json()

        # Validate required fields
        renewal_months = data.get("renewal_months", 12)
        if not isinstance(renewal_months, int) or renewal_months <= 0:
            return (
                jsonify({"success": False, "message": "Số tháng gia hạn không hợp lệ"}),
                400,
            )

        result = ContractService.renew_contract(contract_id, renewal_months)

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": result.get("message", "Gia hạn hợp đồng thành công"),
                    "contract": result.get("contract"),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("error", "Lỗi không xác định"),
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Lỗi khi gia hạn hợp đồng: {str(e)}"}
            ),
            500,
        )


@contracts_bp.route("/<int:contract_id>/terminate", methods=["POST"])
@login_required
@admin_required
def terminate_contract_ajax(contract_id):
    """Terminate contract - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return redirect(url_for("contracts.list_contracts"))

    try:
        data = request.get_json()

        # Validate required fields
        reason = data.get("reason", "").strip()
        if not reason:
            return (
                jsonify({"success": False, "message": "Lý do chấm dứt là bắt buộc"}),
                400,
            )

        result = ContractService.terminate_contract(contract_id, reason)

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": result.get("message", "Chấm dứt hợp đồng thành công"),
                    "contract": result.get("contract"),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("error", "Lỗi không xác định"),
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Lỗi khi chấm dứt hợp đồng: {str(e)}"}
            ),
            500,
        )


@contracts_bp.route("/expiring-soon")
@login_required
@management_required
def list_expiring_contracts():
    """Display expiring contracts page"""
    try:
        days = request.args.get("days", 30, type=int)
        result = ContractService.get_expiring_contracts(days)

        if result.get("success"):
            data = result.get("data", {})
            contracts = data.get("contracts", [])
            total_count = data.get("total_count", 0)
            return render_template(
                "contracts/expiring.html",
                contracts=contracts,
                total_count=total_count,
                days_threshold=days,
                title="Hợp đồng sắp hết hạn",
            )
        else:
            flash(f"Lỗi khi tải danh sách hợp đồng sắp hết hạn: {result.get('message', 'Lỗi không xác định')}", "danger")
            contracts = []
            return render_template(
                "contracts/expiring.html",
                contracts=contracts,
                total_count=0,
                days_threshold=days,
                title="Hợp đồng sắp hết hạn",
            )

    except Exception as e:
        flash(f"Lỗi khi tải danh sách hợp đồng sắp hết hạn: {str(e)}", "danger")
        return render_template(
            "contracts/expiring.html",
            contracts=[],
            total_count=0,
            days_threshold=30,
            title="Hợp đồng sắp hết hạn",
        )


@contracts_bp.route("/<int:contract_id>/pay", methods=["POST"])
@login_required
@student_required
def pay_contract(contract_id):
    """Process contract payment"""
    try:
        print(f"Paying contract {contract_id}")
        result = ContractService.pay_contract(contract_id)

        if result.get("success"):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    {
                        "success": True,
                        "message": result.get("message", "Thanh toán thành công"),
                    }
                )
            else:
                flash(result.get("message", "Thanh toán thành công"), "success")
                return redirect(url_for("contracts.my_contract"))
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": result.get("error", "Thanh toán thất bại"),
                        }
                    ),
                    400,
                )
            else:
                flash(result.get("error", "Thanh toán thất bại"), "error")
                return redirect(url_for("contracts.my_contract"))

    except Exception as e:
        error_message = f"Lỗi khi thanh toán: {str(e)}"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": error_message}), 500
        else:
            flash(error_message, "error")
            return redirect(url_for("contracts.my_contract"))


@contracts_bp.route("/statistics")
@login_required
@management_required
def get_statistics_ajax():
    """Get contract statistics - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return redirect(url_for("contracts.list_contracts"))

    try:
        result = ContractService.get_contract_statistics()

        if result.get("success"):
            return jsonify({"success": True, "statistics": result.get("data", {}).get("statistics", {})})
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("message", "Lỗi không xác định"),
                    }
                ),
                500,
            )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Lỗi khi lấy thống kê: {str(e)}"}
            ),
            500,
        )
