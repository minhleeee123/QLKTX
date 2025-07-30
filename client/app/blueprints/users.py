from app.forms.user_forms import UserSearchForm
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.utils.api_response import APIResponse
from app.utils.decorators import admin_required
from flask import Blueprint
from flask import flash
from flask import json
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
@login_required
@admin_required
def list_users():
    """List all users with pagination and search"""
    search_form = UserSearchForm()

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("search", "")
    role = request.args.get("role", "")

    # Call API to get users
    response = user_service.get_users(
        page=page,
        per_page=per_page,
        search=search if search else None,
        role=role if role else None,
    )

    # Check if we got a successful response with users data
    if response.get("success") == False:
        # Handle error response
        flash(f'Lỗi khi tải danh sách người dùng: {response.get("error", "")}', "error")
        return render_template(
            "users/list.html",
            users=[],
            pagination={},
            search_form=search_form,
        )
    else:
        data = response.get("data", {})
        # Handle successful response (server data directly)
        users = data.get("users", [])
        pagination = data.get("pagination", {})

        # Populate search form with current values
        search_form.search.data = search
        search_form.role.data = role

        return render_template(
            "users/list.html",
            users=users,
            pagination=pagination,
            search_form=search_form,
            current_search=search,
            current_role=role,
        )


@users_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_user():
    # Handle form data
    user_data = {
        "full_name": request.form.get("full_name"),
        "email": request.form.get("email"),
        "phone_number": request.form.get("phone_number"),
        "student_id": request.form.get("student_id"),
        "role_name": request.form.get("role_name"),
        "is_active": request.form.get("is_active") == "true",
        "password": request.form.get("password"),
    }

    if request.form.get("student_id") == "":
        user_data["student_id"] = None

    # Basic validation
    errors = []
    if not user_data.get("full_name"):
        errors.append("Họ và tên là bắt buộc")
    if not user_data.get("email"):
        errors.append("Email là bắt buộc")
    if not user_data.get("role_name"):
        errors.append("Vai trò là bắt buộc")
    if not user_data.get("password"):
        errors.append("Mật khẩu là bắt buộc")
    elif len(user_data.get("password", "")) < 6:
        errors.append("Mật khẩu phải có ít nhất 6 ký tự")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    response = user_service.create_user(user_data)
    print(f"Response from create_user: {json.dumps(response, indent=2)}")

    if response.get("success"):
        return APIResponse.success(message="Tạo người dùng thành công!")
    else:
        return APIResponse.error(
            f'Lỗi khi tạo người dùng: {response.get("message", "")}', 400
        )


@users_bp.route("/<int:user_id>")
@login_required
@admin_required
def get_user(user_id):
    response = user_service.get_user(user_id)

    if response.get("success"):
        user = response.get("data")
        return APIResponse.success(
            data=user, message="Lấy thông tin người dùng thành công"
        )
    else:
        return APIResponse.error(
            f'Lỗi khi lấy thông tin người dùng: {response.get("message", "")}', 404
        )


@users_bp.route("/<int:user_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_user(user_id):
    # Handle form data - exclude email and password from updatable fields
    user_data = {
        "full_name": request.form.get("full_name"),
        "phone_number": request.form.get("phone_number"),
        "student_id": request.form.get("student_id"),
        "role_name": request.form.get("role_name"),
        "is_active": request.form.get("is_active") == "true",
    }

    # Basic validation
    errors = []
    if not user_data.get("full_name"):
        errors.append("Họ và tên là bắt buộc")
    if not user_data.get("role_name"):
        errors.append("Vai trò là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    response = user_service.update_user(user_id, user_data)

    print(f"Response from edit_user: {json.dumps(response, indent=2)}")

    if response.get("success"):
        return APIResponse.success(message="Cập nhật người dùng thành công!")
    else:
        return APIResponse.error(
            f'Lỗi khi cập nhật người dùng: {response.get("message", "")}', 400
        )


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    print(f"Deleting user with ID: {user_id}")
    current_user_obj = auth_service.get_current_user()

    # Check if trying to delete self
    if (
        current_user_obj
        and hasattr(current_user_obj, "id")
        and current_user_obj.id == user_id
    ):
        return APIResponse.error("Không thể xóa chính mình", 400)

    response = user_service.delete_user(user_id)

    if response.get("success"):
        return APIResponse.success(message="Xóa người dùng thành công")
    else:
        return APIResponse.error(
            f'Lỗi khi xóa người dùng: {response.get("message", "")}', 400
        )
