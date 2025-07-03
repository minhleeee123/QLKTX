from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Registration, Room, Contract
from datetime import datetime, date

registrations_bp = Blueprint('registrations', __name__)

def require_role(allowed_roles):
    """Decorator để kiểm tra quyền truy cập"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role.role_name not in allowed_roles:
                return jsonify('Không có quyền truy cập'), 403
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@registrations_bp.route('/', methods=['GET'])
@jwt_required()
def get_registrations():
    """Lấy danh sách đơn đăng ký"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        # Student chỉ xem được đơn của mình
        if current_user.role.role_name == 'student':
            query = Registration.query.filter_by(student_id=current_user_id)
        else:
            # Admin/Management xem tất cả
            query = Registration.query
        
        if status:
            query = query.filter_by(status=status)
        
        registrations = query.order_by(Registration.registration_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'registrations': [{
                'registration_id': reg.registration_id,
                'student': {
                    'user_id': reg.student.user_id,
                    'full_name': reg.student.full_name,
                    'student_id': reg.student.student_id,
                    'email': reg.student.email
                },
                'room': {
                    'room_id': reg.room.room_id,
                    'room_number': reg.room.room_number,
                    'building_name': reg.room.building.building_name,
                    'room_type': reg.room.room_type.type_name,
                    'price': float(reg.room.room_type.price)
                },
                'status': reg.status,
                'registration_date': reg.registration_date.isoformat(),
                'has_contract': reg.contract is not None
            } for reg in registrations.items],
            'pagination': {
                'page': registrations.page,
                'pages': registrations.pages,
                'per_page': registrations.per_page,
                'total': registrations.total,
                'has_next': registrations.has_next,
                'has_prev': registrations.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@registrations_bp.route('/', methods=['POST'])
@jwt_required()
def create_registration():
    """Tạo đơn đăng ký mới (sinh viên)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Chỉ sinh viên mới được đăng ký
        if current_user.role.role_name != 'student':
            return jsonify('Chỉ sinh viên mới được đăng ký phòng'), 403
        
        data = request.get_json()
        room_id = data.get('room_id')
        
        if not room_id:
            return jsonify('room_id là bắt buộc'), 400
        
        # Kiểm tra phòng tồn tại
        room = Room.query.get(room_id)
        if not room:
            return jsonify('Phòng không tồn tại'), 404
        
        # Kiểm tra phòng còn chỗ trống
        if not room.is_available:
            return jsonify('Phòng đã đầy hoặc không khả dụng'), 400
        
        # Kiểm tra sinh viên đã có đơn đăng ký pending/approved chưa
        existing_registration = Registration.query.filter_by(
            student_id=current_user_id,
            status=['pending', 'approved']
        ).first()
        if existing_registration:
            return jsonify('Bạn đã có đơn đăng ký đang chờ xử lý hoặc đã được duyệt'), 400
        
        # Tạo đơn đăng ký mới
        registration = Registration(
            student_id=current_user_id,
            room_id=room_id,
            status='pending',
            registration_date=datetime.utcnow()
        )
        
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            'message': 'Đăng ký phòng thành công',
            'registration': {
                'registration_id': registration.registration_id,
                'room_number': registration.room.room_number,
                'building_name': registration.room.building.building_name,
                'status': registration.status,
                'registration_date': registration.registration_date.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@registrations_bp.route('/<int:registration_id>/approve', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def approve_registration(registration_id):
    """Duyệt đơn đăng ký"""
    try:
        registration = Registration.query.get(registration_id)
        if not registration:
            return jsonify('Đơn đăng ký không tồn tại'), 404
        
        if registration.status != 'pending':
            return jsonify('Chỉ có thể duyệt đơn đang chờ xử lý'), 400
        
        # Kiểm tra phòng còn chỗ trống
        room = registration.room
        if not room.is_available:
            return jsonify('Phòng đã đầy, không thể duyệt đơn'), 400
        
        # Cập nhật trạng thái đơn đăng ký
        registration.status = 'approved'
        
        # Cập nhật số người trong phòng
        room.current_occupancy += 1
        if room.current_occupancy >= room.room_type.capacity:
            room.status = 'occupied'
        
        # Tạo hợp đồng tự động
        contract_code = f"HD{registration.registration_id:04d}"
        start_date = date.today()
        end_date = date(start_date.year + 1, start_date.month, start_date.day)  # 1 năm
        
        contract = Contract(
            registration_id=registration.registration_id,
            contract_code=contract_code,
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(contract)
        db.session.commit()
        
        return jsonify({
            'message': 'Duyệt đơn đăng ký thành công',
            'registration': {
                'registration_id': registration.registration_id,
                'status': registration.status,
                'contract_code': contract.contract_code
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@registrations_bp.route('/<int:registration_id>/reject', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def reject_registration(registration_id):
    """Từ chối đơn đăng ký"""
    try:
        registration = Registration.query.get(registration_id)
        if not registration:
            return jsonify('Đơn đăng ký không tồn tại'), 404
        
        if registration.status != 'pending':
            return jsonify('Chỉ có thể từ chối đơn đang chờ xử lý'), 400
        
        registration.status = 'rejected'
        db.session.commit()
        
        return jsonify({
            'message': 'Từ chối đơn đăng ký thành công',
            'registration': {
                'registration_id': registration.registration_id,
                'status': registration.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@registrations_bp.route('/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    """Hủy đơn đăng ký (sinh viên chỉ hủy được đơn pending của mình)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        registration = Registration.query.get(registration_id)
        if not registration:
            return jsonify('Đơn đăng ký không tồn tại'), 404
        
        # Sinh viên chỉ hủy được đơn của mình
        if (current_user.role.role_name == 'student' and 
            registration.student_id != current_user_id):
            return jsonify('Không có quyền hủy đơn này'), 403
        
        # Chỉ có thể hủy đơn pending
        if registration.status != 'pending':
            return jsonify('Chỉ có thể hủy đơn đang chờ xử lý'), 400
        
        db.session.delete(registration)
        db.session.commit()
        
        return jsonify('Hủy đơn đăng ký thành công'), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500
