from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Payment, Contract, Registration
from app.utils.decorators import require_role
from app.utils.api_response import APIResponse

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    """Lấy danh sách thanh toán"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        # Student chỉ xem được payment của mình
        if current_user.role.role_name == 'student':
            query = Payment.query.join(Contract).join(Registration).filter_by(student_id=current_user_id)
        else:
            # Admin/Management xem tất cả
            query = Payment.query

        if status:
            query = query.filter_by(status=status)

        payments = query.order_by(Payment.payment_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        payments_data = {
            "payments": [
                {
                    "payment_id": payment.payment_id,
                    "contract": {
                        "contract_id": payment.contract.contract_id,
                        "contract_code": payment.contract.contract_code,
                        "student_name": payment.contract.registration.student.full_name,
                        "student_id": payment.contract.registration.student.student_id,
                        "room_number": payment.contract.registration.room.room_number,
                        "building_name": payment.contract.registration.room.building.building_name,
                    },
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
                for payment in payments.items
            ],
            "pagination": {
                "page": payments.page,
                "pages": payments.pages,
                "per_page": payments.per_page,
                "total": payments.total,
                "has_next": payments.has_next,
                "has_prev": payments.has_prev,
            },
        }

        return APIResponse.success(
            data=payments_data, message="Lấy danh sách thanh toán thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@payments_bp.route('/', methods=['POST'])
@jwt_required()
def create_payment():
    """Tạo thanh toán mới (sinh viên)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Chỉ sinh viên mới được tạo payment
        if current_user.role.role_name != 'student':
            return APIResponse.error(
                message="Chỉ sinh viên mới được tạo thanh toán", status_code=403
            )

        data = request.get_json()

        # Validate required fields
        required_fields = ['contract_id', 'amount', 'payment_method']
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Kiểm tra hợp đồng tồn tại và thuộc về sinh viên này
        contract = Contract.query.get(data['contract_id'])
        if not contract:
            return APIResponse.error(message="Hợp đồng không tồn tại", status_code=404)

        if contract.registration.student_id != current_user_id:
            return APIResponse.error(
                message="Hợp đồng không thuộc về bạn", status_code=403
            )

        # Validate payment method
        if data['payment_method'] not in ['bank_transfer', 'cash']:
            return APIResponse.error(
                message="Phương thức thanh toán không hợp lệ", status_code=400
            )

        # Tạo payment mới
        payment = Payment(
            contract_id=data['contract_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            status='pending',
            proof_image_url=data.get('proof_image_url')
        )

        db.session.add(payment)
        db.session.commit()

        payment_data = {
            "payment_id": payment.payment_id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method,
            "status": payment.status,
            "contract_code": payment.contract.contract_code,
        }

        return APIResponse.success(
            data={"payment": payment_data},
            message="Tạo thanh toán thành công",
            status_code=201,
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@payments_bp.route('/<int:payment_id>/confirm', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def confirm_payment(payment_id):
    """Xác nhận thanh toán"""
    try:
        current_user_id = get_jwt_identity()

        payment = Payment.query.get(payment_id)
        if not payment:
            return APIResponse.error(
                message="Thanh toán không tồn tại", status_code=404
            )

        if payment.status != 'pending':
            return APIResponse.error(
                message="Chỉ có thể xác nhận thanh toán đang chờ xử lý", status_code=400
            )

        payment.status = 'confirmed'
        payment.confirmed_by_user_id = current_user_id

        db.session.commit()

        payment_data = {
            "payment_id": payment.payment_id,
            "status": payment.status,
            "confirmed_by": payment.confirmed_by.full_name,
        }

        return APIResponse.success(
            data={"payment": payment_data}, message="Xác nhận thanh toán thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@payments_bp.route('/<int:payment_id>/reject', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def reject_payment(payment_id):
    """Từ chối thanh toán"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return APIResponse.error(
                message="Thanh toán không tồn tại", status_code=404
            )

        if payment.status != 'pending':
            return APIResponse.error(
                message="Chỉ có thể từ chối thanh toán đang chờ xử lý", status_code=400
            )

        payment.status = 'failed'

        db.session.commit()

        payment_data = {"payment_id": payment.payment_id, "status": payment.status}

        return APIResponse.success(
            data={"payment": payment_data}, message="Từ chối thanh toán thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    """Cập nhật thanh toán (sinh viên chỉ cập nhật được payment pending của mình)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        payment = Payment.query.get(payment_id)
        if not payment:
            return APIResponse.error(
                message="Thanh toán không tồn tại", status_code=404
            )

        # Student chỉ cập nhật được payment của mình và phải ở trạng thái pending
        if current_user.role.role_name == 'student':
            if payment.contract.registration.student_id != current_user_id:
                return APIResponse.error(
                    message="Không có quyền cập nhật thanh toán này", status_code=403
                )
            if payment.status != 'pending':
                return APIResponse.error(
                    message="Chỉ có thể cập nhật thanh toán đang chờ xử lý",
                    status_code=400,
                )

        data = request.get_json()

        # Các trường cho phép cập nhật
        if 'proof_image_url' in data:
            payment.proof_image_url = data['proof_image_url']

        # Admin/Management có thể cập nhật thêm các trường khác
        if current_user.role.role_name in ['admin', 'management']:
            if 'amount' in data:
                payment.amount = data['amount']
            if 'payment_method' in data and data['payment_method'] in ['bank_transfer', 'cash']:
                payment.payment_method = data['payment_method']

        db.session.commit()

        payment_data = {
            "payment_id": payment.payment_id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method,
            "proof_image_url": payment.proof_image_url,
        }

        return APIResponse.success(
            data={"payment": payment_data}, message="Cập nhật thanh toán thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@payments_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_payment_statistics():
    """Thống kê thanh toán"""
    try:
        total_payments = Payment.query.count()
        confirmed_payments = Payment.query.filter_by(status='confirmed').count()
        pending_payments = Payment.query.filter_by(status='pending').count()
        failed_payments = Payment.query.filter_by(status='failed').count()

        # Tổng tiền đã xác nhận
        total_confirmed_amount = db.session.query(
            db.func.sum(Payment.amount)
        ).filter_by(status='confirmed').scalar() or 0

        # Tổng tiền đang chờ
        total_pending_amount = db.session.query(
            db.func.sum(Payment.amount)
        ).filter_by(status='pending').scalar() or 0

        statistics_data = {
            "statistics": {
                "total_payments": total_payments,
                "confirmed_payments": confirmed_payments,
                "pending_payments": pending_payments,
                "failed_payments": failed_payments,
                "total_confirmed_amount": float(total_confirmed_amount),
                "total_pending_amount": float(total_pending_amount),
            }
        }

        return APIResponse.success(
            data=statistics_data, message="Lấy thống kê thanh toán thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)
