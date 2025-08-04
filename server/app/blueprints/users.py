from app.extensions import db
from app.models import (
    Building,
    Contract,
    MaintenanceRequest,
    Payment,
    Registration,
    Role,
    Room,
    User,
)
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
@jwt_required()
@require_role(["admin", "management"])
def get_users():
    """
    Lấy danh sách users với phân trang và tìm kiếm

    Method: GET
    Query Parameters:
        page: int = 1              # Trang hiện tại (optional)
        per_page: int = 10         # Số users mỗi trang (optional)
        role: string               # Lọc theo role: 'admin', 'management', 'student', 'staff' (optional)
        search: string             # Tìm kiếm theo tên, email, hoặc student_id (optional)

    Example URL: GET /users?page=1&per_page=10&role=student&search=Nguyen

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách users thành công",
        "data": {
            "users": [
                {
                    "user_id": 1,
                    "full_name": "Nguyễn Văn A",
                    "email": "user@example.com",
                    "phone_number": "0123456789",
                    "student_id": "SV001",
                    "role": "student",
                    "created_at": "2024-01-01T00:00:00",
                    "is_active": true
                }
            ],
            "pagination": {
                "page": 1,
                "pages": 5,
                "per_page": 10,
                "total": 50,
                "has_next": true,
                "has_prev": false
            }
        },
        "status_code": 200
    }
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        role_filter = request.args.get("role")
        search = request.args.get("search")

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
                    User.student_id.contains(search),
                )
            )

        users = query.paginate(page=page, per_page=per_page, error_out=False)

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


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """
    Lấy thông tin chi tiết một user

    Method: GET
    Headers:
        Authorization: Bearer <access_token>
    URL Parameters:
        user_id: int               # ID của user cần lấy thông tin

    Example URL: GET /users/123

    Permissions:
        - User chỉ có thể xem thông tin của chính mình
        - Admin/Management có thể xem thông tin của bất kỳ user nào

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy thông tin user thành công",
        "data": {
            "user": {
                "user_id": 1,
                "full_name": "Nguyễn Văn A",
                "email": "user@example.com",
                "phone_number": "0123456789",
                "student_id": "SV001",
                "role": "student",
                "created_at": "2024-01-01T00:00:00",
                "is_active": true
            }
        },
        "status_code": 200
    }

    Response JSON (Error - 403/404):
    {
        "success": false,
        "message": "Không có quyền truy cập" | "User không tồn tại",
        "data": null,
        "status_code": 403 | 404
    }
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Chỉ cho phép xem thông tin của chính mình hoặc Admin/Management
        if current_user_id != user_id and current_user.role.role_name not in [
            "admin",
            "management",
        ]:
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


@users_bp.route("/", methods=["POST"])
@jwt_required()
@require_role(["admin", "management"])
def create_user():
    """
    Tạo user mới

    Method: POST
    Headers:
        Authorization: Bearer <access_token>
        Content-Type: application/json

    Permissions: Chỉ admin và management có thể tạo user mới

    Request JSON:
    {
        "full_name": "Nguyễn Văn A",       # Required: Họ và tên
        "email": "user@example.com",       # Required: Email (unique)
        "password": "password123",         # Required: Mật khẩu
        "role_name": "student",            # Required: Role - 'admin', 'management', 'student', 'staff'
        "phone_number": "0123456789",      # Optional: Số điện thoại
        "student_id": "SV001",            # Optional: Mã sinh viên (unique nếu có)
        "is_active": true                  # Optional: Trạng thái active (default: true)
    }

    Response JSON (Success - 201):
    {
        "success": true,
        "message": "Tạo user thành công",
        "data": {
            "user": {
                "user_id": 1,
                "full_name": "Nguyễn Văn A",
                "email": "user@example.com",
                "phone_number": "0123456789",
                "student_id": "SV001",
                "role": "student",
                "created_at": "2024-01-01T00:00:00",
                "is_active": true
            }
        },
        "status_code": 201
    }

    Response JSON (Error - 400/403):
    {
        "success": false,
        "message": "Email đã tồn tại" | "Student ID đã tồn tại" | "Role không hợp lệ" | "full_name là bắt buộc",
        "data": null,
        "status_code": 400 | 403
    }
    """
    try:
        data = request.get_json()
        print("Server received data:", data)
        print("Content-Type:", request.content_type)

        # Validate required fields
        required_fields = ["full_name", "email", "password", "role_name"]
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=data["email"]).first():
            return APIResponse.error(message="Email đã được sử dụng", status_code=400)

        # Kiểm tra student_id nếu có
        if data.get("student_id"):
            if User.query.filter_by(student_id=data["student_id"]).first():
                return APIResponse.error(
                    message="Mã sinh viên đã được sử dụng", status_code=400
                )

        # Lấy role
        role = Role.query.filter_by(role_name=data["role_name"]).first()
        if not role:
            return APIResponse.error(message="Role không tồn tại", status_code=400)

        # Tạo user mới
        user = User(
            role_id=role.role_id,
            full_name=data["full_name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            phone_number=data.get("phone_number"),
            student_id=data.get("student_id"),
            is_active=data.get("is_active", True),
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


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Cập nhật thông tin user

    Method: PUT
    Headers:
        Authorization: Bearer <access_token>
        Content-Type: application/json
    URL Parameters:
        user_id: int               # ID của user cần cập nhật

    Permissions:
        - User có thể cập nhật thông tin của chính mình (trừ role và is_active)
        - Admin/Management có thể cập nhật thông tin của bất kỳ user nào

    Request JSON:
    {
        "full_name": "Nguyễn Văn A",       # Optional: Họ và tên
        "phone_number": "0123456789",      # Optional: Số điện thoại
        "role_name": "student",            # Optional: Role (chỉ admin/management mới được đổi)
        "is_active": true                  # Optional: Trạng thái (chỉ admin/management mới được đổi)
    }

    Note: Email và student_id không thể được cập nhật

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Cập nhật user thành công",
        "data": {
            "user": {
                "user_id": 1,
                "full_name": "Nguyễn Văn A",
                "email": "user@example.com",
                "phone_number": "0123456789",
                "student_id": "SV001",
                "role": "student",
                "created_at": "2024-01-01T00:00:00",
                "is_active": true
            }
        },
        "status_code": 200
    }

    Response JSON (Error - 403/404):
    {
        "success": false,
        "message": "Không có quyền truy cập" | "User không tồn tại" | "Role không hợp lệ",
        "data": null,
        "status_code": 403 | 404 | 400
    }
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Chỉ cho phép cập nhật thông tin của chính mình hoặc Admin/Management
        if current_user_id != user_id and current_user.role.role_name not in [
            "admin",
            "management",
        ]:
            return APIResponse.error(message="Không có quyền truy cập", status_code=403)

        user = User.query.get(user_id)
        if not user:
            return APIResponse.error(message="User không tồn tại", status_code=404)

        data = request.get_json()

        # Cập nhật các trường cho phép
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "phone_number" in data:
            user.phone_number = data["phone_number"]

        # Chỉ Admin/Management mới được cập nhật role và is_active
        if current_user.role.role_name in ["admin", "management"]:
            if "is_active" in data:
                user.is_active = data["is_active"]
            if "role_name" in data:
                role = Role.query.filter_by(role_name=data["role_name"]).first()
                if role:
                    user.role_id = role.role_id

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


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@require_role(["admin"])
def delete_user(user_id):
    """
    Xóa user (chỉ Admin có quyền)

    Method: DELETE
    Headers:
        Authorization: Bearer <access_token>
    URL Parameters:
        user_id: int               # ID của user cần xóa

    Permissions: Chỉ admin mới có thể xóa user

    Request: No request body needed

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Xóa user thành công",
        "data": null,
        "status_code": 200
    }

    Response JSON (Error - 400/403/404):
    {
        "success": false,
        "message": "User không tồn tại" | "Không thể xóa chính mình" | "Không có quyền truy cập",
        "data": null,
        "status_code": 404 | 400 | 403
    }
    """
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
        # Kiểm tra registrations
        registrations = Registration.query.filter_by(student_id=user_id).first()
        # Lấy thông tin phòng thông qua registrations
        if registrations:
            room = Room.query.filter_by(room_id=registrations.room_id).first()
            print(f"Room for user {user_id}: {room}")
            building = Building.query.filter_by(building_id=room.building_id).first()
            if room:
                return APIResponse.error(
                    message=f"Không thể xóa sinh viên này vì còn đăng ký phòng {room.room_number} thuộc tòa nhà {building.building_name}. Vui lòng xóa các đăng ký phòng trước.",
                    status_code=400,
                )

        # Kiểm tra contracts (thông qua registrations)
        contracts = (
            Contract.query.join(Registration)
            .filter(Registration.student_id == user_id)
            .first()
        )
        if contracts:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn hợp đồng. Vui lòng xóa các hợp đồng trước.",
                status_code=400,
            )

        # Kiểm tra payments (thông qua contracts)
        payments = (
            Payment.query.join(Contract)
            .join(Registration)
            .filter(Registration.student_id == user_id)
            .first()
        )
        if payments:
            return APIResponse.error(
                message="Không thể xóa sinh viên này vì còn thanh toán. Vui lòng xóa các thanh toán trước.",
                status_code=400,
            )

        # Kiểm tra maintenance requests
        maintenance_requests = MaintenanceRequest.query.filter_by(
            student_id=user_id
        ).first()
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
        return APIResponse.success(message="Xóa user thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)
