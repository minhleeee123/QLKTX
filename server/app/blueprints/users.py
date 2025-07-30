from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash
from app.utils.decorators import require_role
from app.utils.api_response import APIResponse

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
# @jwt_required()
# # @require_role(['admin', 'management'])
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

        user_data = {
            "users": [
                {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "student_id": user.student_id,
                    "role": user.role.role_name,
                    "created_at": user.created_at.isoformat(),
                    "is_active": user.is_active,
                }
                for user in users.items
            ],
            "pagination": {
                "page": users.page,
                "pages": users.pages,
                "per_page": users.per_page,
                "total": users.total,
                "has_next": users.has_next,
                "has_prev": users.has_prev,
            },
        }

        return APIResponse.success(
            data=user_data, message="Lấy danh sách users thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

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
            return APIResponse.error(message="Không có quyền truy cập", status_code=403)

        user = User.query.get(user_id)
        if not user:
            return APIResponse.error(message="User không tồn tại", status_code=404)

        user_data = {
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "student_id": user.student_id,
                "role": user.role.role_name,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active,
            }
        }

        return APIResponse.success(
            data=user_data, message="Lấy thông tin user thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

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
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=data['email']).first():
            return APIResponse.error(message="Email đã được sử dụng", status_code=400)

        # Kiểm tra student_id nếu có
        if data.get('student_id'):
            if User.query.filter_by(student_id=data['student_id']).first():
                return APIResponse.error(
                    message="Mã sinh viên đã được sử dụng", status_code=400
                )

        # Lấy role
        role = Role.query.filter_by(role_name=data['role_name']).first()
        if not role:
            return APIResponse.error(message="Role không tồn tại", status_code=400)

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

        user_data = {
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role.role_name,
            }
        }

        return APIResponse.success(
            data=user_data, message="Tạo user thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

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
            return APIResponse.error(message="Không có quyền truy cập", status_code=403)

        user = User.query.get(user_id)
        if not user:
            return APIResponse.error(message="User không tồn tại", status_code=404)

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

        user_data = {
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role.role_name,
                "is_active": user.is_active,
            }
        }

        return APIResponse.success(data=user_data, message="Cập nhật thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role(['admin'])
def delete_user(user_id):
    """Xóa user (chỉ Admin)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return APIResponse.error(message="User không tồn tại", status_code=404)

        # Không cho phép xóa chính mình
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            return APIResponse.error(
                message="Không thể xóa chính mình", status_code=400
            )

        # Kiểm tra xem user có dữ liệu liên quan không
        from app.models import Registration, Contract, Payment, MaintenanceRequest

        # Kiểm tra registrations
        registrations = Registration.query.filter_by(student_id=user_id).first()
        if registrations:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn đăng ký phòng. Vui lòng xóa các đăng ký phòng trước.",
                status_code=400,
            )

        # Kiểm tra contracts (thông qua registrations)
        contracts = Contract.query.join(Registration).filter(Registration.student_id == user_id).first()
        if contracts:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn hợp đồng. Vui lòng xóa các hợp đồng trước.",
                status_code=400,
            )

        # Kiểm tra payments (thông qua contracts)
        payments = Payment.query.join(Contract).join(Registration).filter(Registration.student_id == user_id).first()
        if payments:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn thanh toán. Vui lòng xóa các thanh toán trước.",
                status_code=400,
            )

        # Kiểm tra maintenance requests
        maintenance_requests = MaintenanceRequest.query.filter_by(student_id=user_id).first()
        if maintenance_requests:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn yêu cầu bảo trì. Vui lòng xóa các yêu cầu bảo trì trước.",
                status_code=400,
            )

        db.session.delete(user)
        db.session.commit()

        return APIResponse.success(message="Xóa user thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)
