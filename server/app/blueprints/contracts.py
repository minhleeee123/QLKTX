from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Contract, Registration
from app.utils.decorators import require_role
from app.utils.api_response import APIResponse

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
            try:
                contract.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
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

@contracts_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_contract_statistics():
    """Thống kê hợp đồng"""
    try:
        from datetime import date

        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(
            Contract.start_date <= date.today(),
            Contract.end_date >= date.today()
        ).count()
        expired_contracts = Contract.query.filter(
            Contract.end_date < date.today()
        ).count()

        # Tính tổng doanh thu
        total_revenue = db.session.query(db.func.sum(Contract.total_paid)).scalar() or 0

        statistics_data = {
            "statistics": {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "expired_contracts": expired_contracts,
                "total_revenue": float(total_revenue),
            }
        }

        return APIResponse.success(
            data=statistics_data, message="Lấy thống kê hợp đồng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)
