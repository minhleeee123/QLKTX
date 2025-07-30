from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from app.forms.contract_forms import ContractSearchForm, ContractUpdateForm
from app.services.contract_service import ContractService
from app.utils.decorators import admin_required, management_required
from app.utils.pagination import Pagination

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')

@contracts_bp.route('/')
@login_required
@management_required
def list_contracts():
    """Display contracts list page"""
    search_form = ContractSearchForm()
    
    # Get parameters
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # Pre-fill form
    if status:
        search_form.status.data = status
    if search:
        search_form.search.data = search

    # Get contracts with filters
    try:
        result = ContractService.get_contracts(
            page=page,
            status=status if status else None
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
def get_contract(contract_id):
    """Get contract details - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        # Non-AJAX requests should redirect to list
        return redirect(url_for('contracts.list_contracts'))
    
    try:
        contract_data = ContractService.get_contract(contract_id)
        
        if contract_data.get('success'):
            return jsonify({
                'success': True, 
                'contract': contract_data.get('contract')
            })
        else:
            return jsonify({
                'success': False,
                'message': contract_data.get('error', 'Lỗi không xác định')
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy thông tin hợp đồng: {str(e)}'
        }), 500


@contracts_bp.route("/<int:contract_id>/edit", methods=["POST"])
@login_required
@admin_required
def update_contract_ajax(contract_id):
    """Update contract - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('contracts.list_contracts'))
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('end_date'):
            return jsonify({
                'success': False,
                'message': 'Ngày kết thúc là bắt buộc'
            }), 400
        
        update_data = {
            'end_date': data['end_date']
        }
        
        result = ContractService.update_contract(contract_id, update_data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'Cập nhật hợp đồng thành công'),
                'contract': result.get('contract')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Lỗi không xác định')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi cập nhật hợp đồng: {str(e)}'
        }), 500


@contracts_bp.route("/statistics")
@login_required
@management_required
def get_statistics_ajax():
    """Get contract statistics - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('contracts.list_contracts'))
    
    try:
        result = ContractService.get_contract_statistics()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'statistics': result.get('statistics')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Lỗi không xác định')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy thống kê: {str(e)}'
        }), 500
