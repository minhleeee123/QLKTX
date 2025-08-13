from app.extensions import db
from app.models import Contract, Payment, Registration, User
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

contracts_bp = Blueprint('contracts', __name__)


@contracts_bp.route('/', methods=['GET'])
@jwt_required()
def get_contracts():
    """Lấy danh sách hợp đồng"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Student chỉ xem được hợp đồng của mình
        if current_user.role.role_name == 'student':
            query = Contract.query.join(Registration).filter_by(student_id=current_user_id)
        else:
            # Admin/Management xem tất cả
            query = Contract.query

        contracts = query.order_by(Contract.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        contracts_data = {
            "contracts": [
                {
                    "contract_id": contract.contract_id,
                    "contract_code": contract.contract_code,
                    "student": {
                        "user_id": contract.registration.student.user_id,
                        "full_name": contract.registration.student.full_name,
                        "student_id": contract.registration.student.student_id,
                        "email": contract.registration.student.email,
                    },
                    "room": {
                        "room_id": contract.registration.room.room_id,
                        "room_number": contract.registration.room.room_number,
                        "building_name": contract.registration.room.building.building_name,
                        "room_type": contract.registration.room.room_type.type_name,
                        "price": float(contract.registration.room.room_type.price),
                    },
                    "start_date": contract.start_date.isoformat(),
                    "end_date": contract.end_date.isoformat(),
                    "created_at": contract.created_at.isoformat(),
                    "is_active": contract.is_active,
                    "is_expired": contract.is_expired,
                    "days_remaining": contract.days_remaining,
                    "duration_months": contract.duration_months,
                    "total_paid": float(contract.total_paid),
                    "payment_count": len(contract.payments),
                    "pending_payments_count": len(contract.pending_payments),
                }
                for contract in contracts.items
            ],
            "pagination": {
                "page": contracts.page,
                "pages": contracts.pages,
                "per_page": contracts.per_page,
                "total": contracts.total,
                "has_next": contracts.has_next,
                "has_prev": contracts.has_prev,
            },
        }

        return APIResponse.success(
            data=contracts_data, message="Lấy danh sách hợp đồng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id):
    """Lấy thông tin chi tiết hợp đồng"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        contract = Contract.query.get(contract_id)
        if not contract:
            return APIResponse.error(message="Hợp đồng không tồn tại", status_code=404)

        # Student chỉ xem được hợp đồng của mình
        if (current_user.role.role_name == 'student' and 
            contract.registration.student_id != current_user_id):
            return APIResponse.error(message="Không có quyền truy cập", status_code=403)

        contract_data = {
            "contract": {
                "contract_id": contract.contract_id,
                "contract_code": contract.contract_code,
                "registration_id": contract.registration_id,
                "student": {
                    "user_id": contract.registration.student.user_id,
                    "full_name": contract.registration.student.full_name,
                    "student_id": contract.registration.student.student_id,
                    "email": contract.registration.student.email,
                    "phone_number": contract.registration.student.phone_number,
                },
                "room": {
                    "room_id": contract.registration.room.room_id,
                    "room_number": contract.registration.room.room_number,
                    "building_name": contract.registration.room.building.building_name,
                    "room_type": contract.registration.room.room_type.type_name,
                    "capacity": contract.registration.room.room_type.capacity,
                    "price": float(contract.registration.room.room_type.price),
                },
                "start_date": contract.start_date.isoformat(),
                "end_date": contract.end_date.isoformat(),
                "created_at": contract.created_at.isoformat(),
                "is_active": contract.is_active,
                "is_expired": contract.is_expired,
                "days_remaining": contract.days_remaining,
                "duration_months": contract.duration_months,
                "total_paid": float(contract.total_paid),
                "payments": [
                    {
                        "payment_id": payment.payment_id,
                        "amount": float(payment.amount),
                        "payment_date": payment.payment_date.isoformat(),
                        "payment_method": payment.payment_method,
                        "payment_method_display": payment.payment_method_display,
                        "status": payment.status,
                        "proof_image_url": payment.proof_image_url,
                        "confirmed_by": (
                            {
                                "user_id": payment.confirmed_by.user_id,
                                "full_name": payment.confirmed_by.full_name,
                            }
                            if payment.confirmed_by
                            else None
                        ),
                    }
                    for payment in contract.payments
                ],
            }
        }

        return APIResponse.success(
            data=contract_data, message="Lấy thông tin hợp đồng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@contracts_bp.route('/<int:contract_id>', methods=['PUT'])
@jwt_required()
@require_role(['admin', 'management'])
def update_contract(contract_id):
    """Cập nhật hợp đồng"""
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return APIResponse.error(message="Hợp đồng không tồn tại", status_code=404)

        data = request.get_json()

        # Cập nhật ngày kết thúc
        if 'end_date' in data:
            from datetime import datetime
            old_end_date = contract.end_date
            try:
                new_end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
                contract.end_date = new_end_date

            except ValueError:
                return APIResponse.error(
                    message="Định dạng ngày không hợp lệ (YYYY-MM-DD)", status_code=400
                )

        db.session.commit()

        contract_data = {
            "contract": {
                "contract_id": contract.contract_id,
                "contract_code": contract.contract_code,
                "end_date": contract.end_date.isoformat(),
                "is_active": contract.is_active,
                "days_remaining": contract.days_remaining,
            }
        }

        return APIResponse.success(
            data=contract_data, message="Cập nhật hợp đồng thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@contracts_bp.route("/<int:contract_id>/renew", methods=["POST"])
@jwt_required()
@require_role(["admin", "management"])
def renew_contract(contract_id):
    """Gia hạn hợp đồng"""
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return APIResponse.error(message="Hợp đồng không tồn tại", status_code=404)

        data = request.get_json()
        renewal_months = data.get("renewal_months", 12)  # Mặc định 12 tháng

        if not isinstance(renewal_months, int) or renewal_months <= 0:
            return APIResponse.error(
                message="Số tháng gia hạn phải là số nguyên dương", status_code=400
            )

        from calendar import monthrange
        from datetime import datetime, timedelta

        # Tính ngày kết thúc mới bằng cách thêm tháng
        if contract.is_expired:
            # Nếu hợp đồng đã hết hạn, gia hạn từ hôm nay
            current_date = datetime.now().date()
            new_year = current_date.year
            new_month = current_date.month + renewal_months

            # Xử lý khi tháng vượt quá 12
            while new_month > 12:
                new_year += 1
                new_month -= 12

            # Xử lý ngày cuối tháng
            max_day = monthrange(new_year, new_month)[1]
            new_day = min(current_date.day, max_day)
            new_end_date = datetime(new_year, new_month, new_day).date()
        else:
            # Nếu hợp đồng còn hiệu lực, gia hạn từ ngày kết thúc hiện tại
            current_end = contract.end_date
            new_year = current_end.year
            new_month = current_end.month + renewal_months

            # Xử lý khi tháng vượt quá 12
            while new_month > 12:
                new_year += 1
                new_month -= 12

            # Xử lý ngày cuối tháng
            max_day = monthrange(new_year, new_month)[1]
            new_day = min(current_end.day, max_day)
            new_end_date = datetime(new_year, new_month, new_day).date()

        # Cập nhật ngày kết thúc
        old_end_date = contract.end_date
        contract.end_date = new_end_date

        db.session.commit()

        contract_data = {
            "contract": {
                "contract_id": contract.contract_id,
                "contract_code": contract.contract_code,
                "old_end_date": old_end_date.isoformat(),
                "new_end_date": contract.end_date.isoformat(),
                "renewal_months": renewal_months,
                "is_active": contract.is_active,
                "days_remaining": contract.days_remaining,
            }
        }

        return APIResponse.success(
            data=contract_data,
            message=f"Gia hạn hợp đồng thành công thêm {renewal_months} tháng",
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@contracts_bp.route("/<int:contract_id>/terminate", methods=["POST"])
@jwt_required()
@require_role(["admin", "management"])
def terminate_contract(contract_id):
    """Chấm dứt hợp đồng trước thời hạn"""
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return APIResponse.error(message="Hợp đồng không tồn tại", status_code=404)

        if contract.is_expired:
            return APIResponse.error(message="Hợp đồng đã hết hạn", status_code=400)

        data = request.get_json()
        termination_reason = data.get("reason", "")

        from datetime import date

        # Cập nhật ngày kết thúc thành hôm nay
        old_end_date = contract.end_date
        contract.end_date = date.today()

        # Cập nhật trạng thái phòng - giảm số người ở
        room = contract.registration.room
        if room.current_occupancy > 0:
            room.current_occupancy -= 1
            if room.current_occupancy < room.room_type.capacity:
                room.status = "available"

        db.session.commit()

        contract_data = {
            "contract": {
                "contract_id": contract.contract_id,
                "contract_code": contract.contract_code,
                "old_end_date": old_end_date.isoformat(),
                "terminated_date": contract.end_date.isoformat(),
                "termination_reason": termination_reason,
                "is_active": contract.is_active,
            }
        }

        return APIResponse.success(
            data=contract_data, message="Chấm dứt hợp đồng thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@contracts_bp.route("/expiring-soon", methods=["GET"])
@jwt_required()
@require_role(["admin", "management"])
def get_expiring_contracts():
    """Lấy danh sách hợp đồng sắp hết hạn"""
    try:
        from datetime import date, timedelta

        days_threshold = request.args.get("days", 30, type=int)
        threshold_date = date.today() + timedelta(days=days_threshold)

        contracts = (
            Contract.query.filter(
                Contract.end_date <= threshold_date, Contract.end_date >= date.today()
            )
            .order_by(Contract.end_date.asc())
            .all()
        )

        contracts_data = {
            "contracts": [
                {
                    "contract_id": contract.contract_id,
                    "contract_code": contract.contract_code,
                    "student": {
                        "user_id": contract.registration.student.user_id,
                        "full_name": contract.registration.student.full_name,
                        "student_id": contract.registration.student.student_id,
                        "email": contract.registration.student.email,
                        "phone_number": contract.registration.student.phone_number,
                    },
                    "room": {
                        "room_id": contract.registration.room.room_id,
                        "room_number": contract.registration.room.room_number,
                        "building_name": contract.registration.room.building.building_name,
                    },
                    "end_date": contract.end_date.isoformat(),
                    "days_remaining": contract.days_remaining,
                }
                for contract in contracts
            ],
            "total_count": len(contracts),
            "days_threshold": days_threshold,
        }

        return APIResponse.success(
            data=contracts_data,
            message=f"Lấy danh sách {len(contracts)} hợp đồng sắp hết hạn thành công",
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@contracts_bp.route("/export", methods=["GET"])
@jwt_required()
@require_role(["admin", "management"])
def export_contracts():
    """Xuất báo cáo hợp đồng ra Excel"""
    try:
        from app.services.contract_report_service import (
            XLSXWRITER_AVAILABLE,
            ContractReportService,
        )

        if not XLSXWRITER_AVAILABLE:
            return APIResponse.error(
                message="Tính năng xuất Excel chưa được cài đặt. Vui lòng liên hệ quản trị viên.",
                status_code=503,
            )

        return ContractReportService.generate_contracts_excel_report()

    except Exception as e:
        return APIResponse.error(
            message=f"Lỗi khi xuất báo cáo: {str(e)}", status_code=500
        )


@contracts_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_contract_statistics():
    """Thống kê hợp đồng"""
    try:
        from datetime import date, timedelta

        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(
            Contract.start_date <= date.today(),
            Contract.end_date >= date.today()
        ).count()
        expired_contracts = Contract.query.filter(
            Contract.end_date < date.today()
        ).count()

        # Hợp đồng sắp hết hạn (trong 30 ngày)
        expiring_soon = Contract.query.filter(
            Contract.end_date <= date.today() + timedelta(days=30),
            Contract.end_date >= date.today(),
        ).count()

        # Tính tổng doanh thu từ các thanh toán đã xác nhận
        total_revenue = (
            db.session.query(db.func.sum(Payment.amount))
            .filter(Payment.status == "confirmed")
            .scalar()
            or 0
        )

        statistics_data = {
            "statistics": {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "expired_contracts": expired_contracts,
                "expiring_soon": expiring_soon,
                "total_revenue": float(total_revenue),
            }
        }

        return APIResponse.success(
            data=statistics_data, message="Lấy thống kê hợp đồng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)
        return APIResponse.success(
            data=statistics_data, message="Lấy thống kê hợp đồng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)
