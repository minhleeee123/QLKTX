from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Đăng nhập và lấy JWT token"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify('Email và password là bắt buộc'), 400
        
        # Tìm user
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify('Email hoặc password không đúng'), 401

        # Tạo access token
        access_token = create_access_token(identity=str(user.user_id))
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role.role_name,
                'student_id': user.student_id
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Lấy thông tin user hiện tại"""
    try:
        user_id = get_jwt_identity()
        
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
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

@auth_bp.route('/register', methods=['POST'])
def register():
    """Đăng ký tài khoản sinh viên"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'password', 'student_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=data['email']).first():
            return jsonify('Email đã được sử dụng'), 400
        
        # Kiểm tra student_id đã tồn tại
        if User.query.filter_by(student_id=data['student_id']).first():
            return jsonify('Mã sinh viên đã được sử dụng'), 400
        
        # Lấy role Student
        student_role = Role.query.filter_by(role_name='student').first()
        if not student_role:
            return jsonify('Role Student không tồn tại'), 500
        
        # Tạo user mới
        user = User(
            role_id=student_role.role_id,
            full_name=data['full_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone_number=data.get('phone_number'),
            student_id=data['student_id'],
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Đăng ký thành công',
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'student_id': user.student_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    print("Change Password Endpoint")
    """Đổi mật khẩu cho user hiện tại"""
    try:
        user_id = get_jwt_identity()
        print(f"JWT Identity: {user_id}, type: {type(user_id)}")  # Debug
        
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        user = User.query.get(user_id)
        print(f"User found: {user}")  # Debug
        if not user:
            return jsonify('User không tồn tại'), 404
        
        data = request.get_json()
        
        print(data)
        
        # Validate required fields
        required_fields = ['current_password', 'new_password', 'confirm_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Kiểm tra mật khẩu hiện tại
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify('Mật khẩu hiện tại không đúng'), 400
        
        # Kiểm tra mật khẩu mới và xác nhận
        if data['new_password'] != data['confirm_password']:
            return jsonify('Mật khẩu mới và xác nhận không khớp'), 400
        
        # Kiểm tra độ dài mật khẩu mới
        if len(data['new_password']) < 6:
            return jsonify('Mật khẩu mới phải có ít nhất 6 ký tự'), 400
        
        # Kiểm tra mật khẩu mới không giống mật khẩu cũ
        if check_password_hash(user.password_hash, data['new_password']):
            return jsonify('Mật khẩu mới phải khác mật khẩu hiện tại'), 400
        
        # Cập nhật mật khẩu
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(data['new_password'])
        user.updated_at = db.func.now()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Đổi mật khẩu thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

