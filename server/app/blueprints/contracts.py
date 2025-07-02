from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Contract, Registration

contracts_bp = Blueprint('contracts', __name__)

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
        if current_user.role.role_name == 'Student':
            query = Contract.query.join(Registration).filter_by(student_id=current_user_id)
        else:
            # Admin/Management xem tất cả
            query = Contract.query
        
        contracts = query.order_by(Contract.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'contracts': [{
                'contract_id': contract.contract_id,
                'contract_code': contract.contract_code,
                'student': {
                    'user_id': contract.registration.student.user_id,
                    'full_name': contract.registration.student.full_name,
                    'student_code': contract.registration.student.student_code,
                    'email': contract.registration.student.email
                },
                'room': {
                    'room_id': contract.registration.room.room_id,
                    'room_number': contract.registration.room.room_number,
                    'building_name': contract.registration.room.building.building_name,
                    'room_type': contract.registration.room.room_type.type_name,
                    'price': float(contract.registration.room.room_type.price)
                },
                'start_date': contract.start_date.isoformat(),
                'end_date': contract.end_date.isoformat(),
                'created_at': contract.created_at.isoformat(),
                'is_active': contract.is_active,
                'is_expired': contract.is_expired,
                'days_remaining': contract.days_remaining,
                'duration_months': contract.duration_months,
                'total_paid': float(contract.total_paid),
                'payment_count': len(contract.payments),
                'pending_payments_count': len(contract.pending_payments)
            } for contract in contracts.items],
            'pagination': {
                'page': contracts.page,
                'pages': contracts.pages,
                'per_page': contracts.per_page,
                'total': contracts.total,
                'has_next': contracts.has_next,
                'has_prev': contracts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id):
    """Lấy thông tin chi tiết hợp đồng"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        contract = Contract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Hợp đồng không tồn tại'}), 404
        
        # Student chỉ xem được hợp đồng của mình
        if (current_user.role.role_name == 'Student' and 
            contract.registration.student_id != current_user_id):
            return jsonify({'error': 'Không có quyền truy cập'}), 403
        
        return jsonify({
            'contract': {
                'contract_id': contract.contract_id,
                'contract_code': contract.contract_code,
                'registration_id': contract.registration_id,
                'student': {
                    'user_id': contract.registration.student.user_id,
                    'full_name': contract.registration.student.full_name,
                    'student_code': contract.registration.student.student_code,
                    'email': contract.registration.student.email,
                    'phone_number': contract.registration.student.phone_number
                },
                'room': {
                    'room_id': contract.registration.room.room_id,
                    'room_number': contract.registration.room.room_number,
                    'building_name': contract.registration.room.building.building_name,
                    'room_type': contract.registration.room.room_type.type_name,
                    'capacity': contract.registration.room.room_type.capacity,
                    'price': float(contract.registration.room.room_type.price)
                },
                'start_date': contract.start_date.isoformat(),
                'end_date': contract.end_date.isoformat(),
                'created_at': contract.created_at.isoformat(),
                'is_active': contract.is_active,
                'is_expired': contract.is_expired,
                'days_remaining': contract.days_remaining,
                'duration_months': contract.duration_months,
                'total_paid': float(contract.total_paid),
                'payments': [{
                    'payment_id': payment.payment_id,
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
                } for payment in contract.payments]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/<int:contract_id>', methods=['PUT'])
@jwt_required()
@require_role(['Admin', 'Management'])
def update_contract(contract_id):
    """Cập nhật hợp đồng"""
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return jsonify({'error': 'Hợp đồng không tồn tại'}), 404
        
        data = request.get_json()
        
        # Cập nhật ngày kết thúc
        if 'end_date' in data:
            from datetime import datetime
            try:
                contract.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Định dạng ngày không hợp lệ (YYYY-MM-DD)'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật hợp đồng thành công',
            'contract': {
                'contract_id': contract.contract_id,
                'contract_code': contract.contract_code,
                'end_date': contract.end_date.isoformat(),
                'is_active': contract.is_active,
                'days_remaining': contract.days_remaining
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['Admin', 'Management'])
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
        
        return jsonify({
            'statistics': {
                'total_contracts': total_contracts,
                'active_contracts': active_contracts,
                'expired_contracts': expired_contracts,
                'total_revenue': float(total_revenue)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
