from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

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

@users_bp.route('/', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_users():
    """Lấy danh sách users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search')
        
        query = User.query.join(Role)
        
        # Filter by role
        if role_filter:
            query = query.filter(Role.role_name == role_filter)
        
        # Search by name or email
        if search:
            query = query.filter(
                db.or_(
                    User.full_name.contains(search),
                    User.email.contains(search),
                    User.student_id.contains(search)
                )
            )
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [{
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'student_id': user.student_id,
                'role': user.role.role_name,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active
            } for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Lấy thông tin chi tiết một user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Chỉ cho phép xem thông tin của chính mình hoặc Admin/Management
        if (current_user_id != user_id and 
            current_user.role.role_name not in ['admin', 'management']):
            return jsonify('Không có quyền truy cập'), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify('User không tồn tại'), 404
        
        return jsonify({
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'student_id': user.student_id,
                'role': user.role.role_name,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def create_user():
    """Tạo user mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'password', 'role_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=data['email']).first():
            return jsonify('Email đã được sử dụng'), 400
        
        # Kiểm tra student_id nếu có
        if data.get('student_id'):
            if User.query.filter_by(student_id=data['student_id']).first():
                return jsonify('Mã sinh viên đã được sử dụng'), 400
        
        # Lấy role
        role = Role.query.filter_by(role_name=data['role_name']).first()
        if not role:
            return jsonify('Role không tồn tại'), 400
        
        # Tạo user mới
        user = User(
            role_id=role.role_id,
            full_name=data['full_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone_number=data.get('phone_number'),
            student_id=data.get('student_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Tạo user thành công',
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role.role_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Cập nhật thông tin user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Chỉ cho phép cập nhật thông tin của chính mình hoặc Admin/Management
        if (current_user_id != user_id and 
            current_user.role.role_name not in ['admin', 'management']):
            return jsonify('Không có quyền truy cập'), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify('User không tồn tại'), 404
        
        data = request.get_json()
        
        # Cập nhật các trường cho phép
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        
        # Chỉ Admin/Management mới được cập nhật role và is_active
        if current_user.role.role_name in ['admin', 'management']:
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'role_name' in data:
                role = Role.query.filter_by(role_name=data['role_name']).first()
                if role:
                    user.role_id = role.role_id
        
        # Cập nhật password nếu có
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật thành công',
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'role': user.role.role_name,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role(['admin'])
def delete_user(user_id):
    """Xóa user (chỉ Admin)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify('User không tồn tại'), 404
        
        # Không cho phép xóa chính mình
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            return jsonify('Không thể xóa chính mình'), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify('Xóa user thành công'), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500
