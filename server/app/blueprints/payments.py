from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Payment, Contract, Registration

payments_bp = Blueprint('payments', __name__)

def require_role(allowed_roles):
    """Decorator để kiểm tra quyền truy cập"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role.role_name not in allowed_roles:
                return jsonify({'error': 'Không có quyền truy cập'}), 403
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

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
        
        return jsonify({
            'payments': [{
                'payment_id': payment.payment_id,
                'contract': {
                    'contract_id': payment.contract.contract_id,
                    'contract_code': payment.contract.contract_code,
                    'student_name': payment.contract.registration.student.full_name,
                    'student_code': payment.contract.registration.student.student_code,
                    'room_number': payment.contract.registration.room.room_number,
                    'building_name': payment.contract.registration.room.building.building_name
                },
                'amount': float(payment.amount),
                'payment_date': payment.payment_date.isoformat(),
                'payment_method': payment.payment_method,
                'payment_method_display': payment.payment_method_display,
                'status': payment.status,
                'proof_image_url': payment.proof_image_url,
                'confirmed_by': {
                    'user_id': payment.confirmed_by.user_id,
                    'full_name': payment.confirmed_by.full_name
                } if payment.confirmed_by else None
            } for payment in payments.items],
            'pagination': {
                'page': payments.page,
                'pages': payments.pages,
                'per_page': payments.per_page,
                'total': payments.total,
                'has_next': payments.has_next,
                'has_prev': payments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/', methods=['POST'])
@jwt_required()
def create_payment():
    """Tạo thanh toán mới (sinh viên)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Chỉ sinh viên mới được tạo payment
        if current_user.role.role_name != 'student':
            return jsonify({'error': 'Chỉ sinh viên mới được tạo thanh toán'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['contract_id', 'amount', 'payment_method']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} là bắt buộc'}), 400
        
        # Kiểm tra hợp đồng tồn tại và thuộc về sinh viên này
        contract = Contract.query.get(data['contract_id'])
        if not contract:
            return jsonify({'error': 'Hợp đồng không tồn tại'}), 404
        
        if contract.registration.student_id != current_user_id:
            return jsonify({'error': 'Hợp đồng không thuộc về bạn'}), 403
        
        # Validate payment method
        if data['payment_method'] not in ['bank_transfer', 'cash']:
            return jsonify({'error': 'Phương thức thanh toán không hợp lệ'}), 400
        
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
        
        return jsonify({
            'message': 'Tạo thanh toán thành công',
            'payment': {
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'payment_method': payment.payment_method,
                'status': payment.status,
                'contract_code': payment.contract.contract_code
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>/confirm', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def confirm_payment(payment_id):
    """Xác nhận thanh toán"""
    try:
        current_user_id = get_jwt_identity()
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Thanh toán không tồn tại'}), 404
        
        if payment.status != 'pending':
            return jsonify({'error': 'Chỉ có thể xác nhận thanh toán đang chờ xử lý'}), 400
        
        payment.status = 'confirmed'
        payment.confirmed_by_user_id = current_user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Xác nhận thanh toán thành công',
            'payment': {
                'payment_id': payment.payment_id,
                'status': payment.status,
                'confirmed_by': payment.confirmed_by.full_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>/reject', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def reject_payment(payment_id):
    """Từ chối thanh toán"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Thanh toán không tồn tại'}), 404
        
        if payment.status != 'pending':
            return jsonify({'error': 'Chỉ có thể từ chối thanh toán đang chờ xử lý'}), 400
        
        payment.status = 'failed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Từ chối thanh toán thành công',
            'payment': {
                'payment_id': payment.payment_id,
                'status': payment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    """Cập nhật thanh toán (sinh viên chỉ cập nhật được payment pending của mình)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Thanh toán không tồn tại'}), 404
        
        # Student chỉ cập nhật được payment của mình và phải ở trạng thái pending
        if current_user.role.role_name == 'student':
            if payment.contract.registration.student_id != current_user_id:
                return jsonify({'error': 'Không có quyền cập nhật thanh toán này'}), 403
            if payment.status != 'pending':
                return jsonify({'error': 'Chỉ có thể cập nhật thanh toán đang chờ xử lý'}), 400
        
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
        
        return jsonify({
            'message': 'Cập nhật thanh toán thành công',
            'payment': {
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'payment_method': payment.payment_method,
                'proof_image_url': payment.proof_image_url
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
        
        return jsonify({
            'statistics': {
                'total_payments': total_payments,
                'confirmed_payments': confirmed_payments,
                'pending_payments': pending_payments,
                'failed_payments': failed_payments,
                'total_confirmed_amount': float(total_confirmed_amount),
                'total_pending_amount': float(total_pending_amount)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
