from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..forms.user_forms import UserSearchForm
from ..services.user_service import user_service
from ..services.auth_service import auth_service
from flask_login import login_required, current_user
from ..utils.decorators import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@admin_required
def list_users():
    """List all users with pagination and search"""
    search_form = UserSearchForm()

    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')

    # Call API to get users
    response = user_service.get_users(
        page=page,
        per_page=per_page,
        search=search if search else None,
        role=role if role else None
    )

    if response['success']:
        users_data = response['data']
        users = users_data.get('users', [])
        pagination = users_data.get('pagination', {})

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
    else:
        flash(f'Lỗi khi tải danh sách người dùng: {response.get("error", "")}', 'error')
        return render_template(
            "users/list.html",
            users=[],
            pagination={},
            search_form=search_form,
        )


@users_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_user():
    """Create new user - AJAX only"""
    # Handle regular form data
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
        return jsonify({"success": False, "message": "; ".join(errors)})

    response = user_service.create_user(user_data)

    if response["success"]:
        return jsonify({"success": True, "message": "Tạo người dùng thành công!"})
    else:
        return jsonify(
            {
                "success": False,
                "message": f'Lỗi khi tạo người dùng: {response.get("error", "")}',
            }
        )


@users_bp.route('/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    response = user_service.get_user(user_id)

    if response['success']:
        user = response['data']['user']

        # Check if it's an AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "user": user})

        # Regular request - return HTML
        return render_template('users/view.html', user=user)
    else:
        # Check if it's an AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {
                    "success": False,
                    "message": f'Lỗi khi tải thông tin người dùng: {response.get("error", "")}',
                }
            )

        # Regular request - flash and redirect
        flash(f'Lỗi khi tải thông tin người dùng: {response.get("error", "")}', 'error')
        return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    # Get user data first
    response = user_service.get_user(user_id)

    if not response['success']:
        flash(f'Lỗi khi tải thông tin người dùng: {response.get("error", "")}', 'error')
        return redirect(url_for('users.list_users'))

    user = response['data']['user']

    if request.method == "POST":
        # Handle form submission (both regular and AJAX)
        errors = []

        # Manual validation
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        role_name = request.form.get("role_name", "").strip()
        is_active = request.form.get("is_active")
        password = request.form.get("password", "").strip()

        if not full_name:
            errors.append("Họ và tên không được để trống")
        if phone_number and (len(phone_number) < 10 or not phone_number.isdigit()):
            errors.append("Số điện thoại phải có ít nhất 10 chữ số")
        if not role_name:
            errors.append("Vai trò không được để trống")

        # Check if it's an AJAX request
        is_ajax = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.content_type == "application/json"
        )

        if errors:
            if is_ajax:
                return jsonify({"success": False, "message": "; ".join(errors)})
            else:
                for error in errors:
                    flash(error, "error")
                return render_template(
                    "users/form.html",
                    user=user,
                    title="Chỉnh sửa người dùng",
                    is_create=False,
                )

        # Prepare user data
        user_data = {
            "full_name": full_name,
            "phone_number": phone_number,
            "role_name": role_name,
            "is_active": is_active == "on" or is_active == "true",
        }

        # Add password if provided
        if password:
            user_data["password"] = password

        response = user_service.update_user(user_id, user_data)

        if is_ajax:
            if response["success"]:
                return jsonify(
                    {"success": True, "message": "Cập nhật người dùng thành công!"}
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": f'Lỗi khi cập nhật người dùng: {response.get("error", "")}',
                    }
                )

        # Regular form submission
        if response['success']:
            flash('Cập nhật người dùng thành công!', 'success')
            return redirect(url_for('users.view_user', user_id=user_id))
        else:
            flash(f'Lỗi khi cập nhật người dùng: {response.get("error", "")}', 'error')

    return render_template(
        "users/form.html", user=user, title="Chỉnh sửa người dùng", is_create=False
    )


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    current_user_obj = auth_service.get_current_user()

    # Check if trying to delete self
    if (
        current_user_obj
        and hasattr(current_user_obj, "id")
        and current_user_obj.id == user_id
    ):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return (
                jsonify({"success": False, "message": "Không thể xóa chính mình"}),
                400,
            )
        else:
            flash("Không thể xóa chính mình", "error")
            return redirect(url_for("users.list_users"))

    response = user_service.delete_user(user_id)

    # Check if it's an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if response["success"]:
            return jsonify({"success": True, "message": "Xóa người dùng thành công"})
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": response.get("error", "Lỗi không xác định"),
                    }
                ),
                400,
            )
    else:
        # Regular form submission
        if response["success"]:
            flash("Xóa người dùng thành công", "success")
        else:
            flash(
                f'Lỗi khi xóa người dùng: {response.get("error", "Lỗi không xác định")}',
                "error",
            )
        return redirect(url_for("users.list_users"))
