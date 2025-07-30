from flask import (
    Blueprint,
    json,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from ..forms.user_forms import UserSearchForm
from ..services.user_service import user_service
from ..services.auth_service import auth_service
from flask_login import login_required, current_user
from ..utils.decorators import admin_required
from ..utils.api_response import APIResponse

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

    data = response.get("data", {})

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
    """Create new user - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        # Non-AJAX requests should redirect to list
        return redirect(url_for("users.list_users"))

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
    try:
        response = user_service.create_user(user_data)
        if response.get("success") != False:  # Success if no explicit failure
            return APIResponse.success(message="Tạo người dùng thành công!")
        else:
            return APIResponse.error(
                f'Lỗi khi tạo người dùng: {response.get("error", "")}', 400
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tạo người dùng: {str(e)}", 500)


@users_bp.route("/<int:user_id>")
@login_required
@admin_required
def get_user(user_id):
    """Get user details - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        # Non-AJAX requests should redirect to list
        return redirect(url_for("users.list_users"))

    response = user_service.get_user(user_id)

    print(
        f"Response from get_user: {json.dumps(response, indent=2, ensure_ascii=False)}"
    )  # Debugging output

    return_value = APIResponse.success(
        data={"user": response}, message="Lấy thông tin người dùng thành công"
    )

    print(f"Return value from get_user: {return_value}")  # Debugging output
    # Check if we got an error response
    if response.get("success") == False:
        return APIResponse.error(response.get("error", "Lỗi không xác định"), 404)
    else:
        # Handle successful response (server data directly)
        return APIResponse.success(
            data={"user": response}, message="Lấy thông tin người dùng thành công"
        )


@users_bp.route("/<int:user_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        # Non-AJAX requests should redirect to list
        return redirect(url_for("users.list_users"))

    # Handle form data
    user_data = {
        "full_name": request.form.get("full_name"),
        "email": request.form.get("email"),
        "phone_number": request.form.get("phone_number"),
        "student_id": request.form.get("student_id"),
        "role_name": request.form.get("role_name"),
        "is_active": request.form.get("is_active") == "true",
    }

    # Only include password if provided
    password = request.form.get("password")
    if password and password.strip():
        if len(password) < 6:
            return APIResponse.error("Mật khẩu phải có ít nhất 6 ký tự", 400)
        user_data["password"] = password

    # Basic validation
    errors = []
    if not user_data.get("full_name"):
        errors.append("Họ và tên là bắt buộc")
    if not user_data.get("email"):
        errors.append("Email là bắt buộc")
    if not user_data.get("role_name"):
        errors.append("Vai trò là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        response = user_service.update_user(user_id, user_data)

        if response.get("success") != False:  # Success if no explicit failure
            return APIResponse.success(message="Cập nhật người dùng thành công!")
        else:
            return APIResponse.error(
                f'Lỗi khi cập nhật người dùng: {response.get("error", "")}', 400
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi cập nhật người dùng: {str(e)}", 500)


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user - AJAX only"""
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        # Non-AJAX requests should redirect to list
        return redirect(url_for("users.list_users"))

    current_user_obj = auth_service.get_current_user()

    # Check if trying to delete self
    if (
        current_user_obj
        and hasattr(current_user_obj, "id")
        and current_user_obj.id == user_id
    ):
        return APIResponse.error("Không thể xóa chính mình", 400)

    try:
        response = user_service.delete_user(user_id)

        if response.get("success") != False:  # Success if no explicit failure
            return APIResponse.success(message="Xóa người dùng thành công")
        else:
            return APIResponse.error(response.get("error", "Lỗi không xác định"), 400)
    except Exception as e:
        return APIResponse.error(f"Lỗi khi xóa người dùng: {str(e)}", 500)
