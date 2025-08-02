from app.services.room_type_service import room_type_service
from app.utils.api_response import APIResponse
from app.utils.decorators import admin_required
from flask import (
    Blueprint,
    flash,
    json,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

# Blueprint registration
room_types_bp = Blueprint("room_types", __name__)


@room_types_bp.route("/", methods=["GET"])
@login_required
@admin_required
def list_room_types():
    """Display list of all room types or return JSON for AJAX requests"""
    try:
        response = room_type_service.get_room_types()

        print(f"Response from get_room_types: {json.dumps(response, indent=2)}")

        # Check if we got a successful response
        if response.get("success") == False:
            # For AJAX requests, return JSON error
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return APIResponse.error(
                    f'Lỗi khi lấy danh sách loại phòng: {response.get("message", "")}',
                    400,
                )

            flash(
                f'Lỗi khi tải danh sách loại phòng: {response.get("message", "")}',
                "danger",
            )
            room_types = []
        else:
            room_types_data = response.get("data", {})
            room_types = room_types_data.get("room_types", [])

            # For AJAX requests, return JSON success
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return APIResponse.success(
                    data={"room_types": room_types},
                    message="Lấy danh sách loại phòng thành công",
                )

    except Exception as e:
        print(f"Error loading room types: {str(e)}")

        # For AJAX requests, return JSON error
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return APIResponse.error(f"Lỗi khi tải danh sách loại phòng: {str(e)}", 500)

        flash(f"Lỗi khi tải danh sách loại phòng: {str(e)}", "danger")
        room_types = []

    # Return HTML template for regular page requests
    return render_template(
        "room_types/list.html", room_types=room_types, title="Quản lý loại phòng"
    )


@room_types_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_room_type():
    """Create new room type"""
    # Handle form data
    room_type_data = {
        "type_name": request.form.get("type_name"),
        "capacity": request.form.get("capacity", type=int),
        "price": request.form.get("price", type=float),
    }

    # Basic validation
    errors = []
    if (
        not room_type_data.get("type_name")
        or not room_type_data.get("type_name").strip()
    ):
        errors.append("Tên loại phòng là bắt buộc")

    if not room_type_data.get("capacity") or room_type_data.get("capacity") <= 0:
        errors.append("Sức chứa phải là số dương")

    if not room_type_data.get("price") or room_type_data.get("price") <= 0:
        errors.append("Giá phòng phải là số dương")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        # Clean the data
        room_type_data["type_name"] = room_type_data["type_name"].strip()

        response = room_type_service.create_room_type(room_type_data)
        print(f"Response from create_room_type: {json.dumps(response, indent=2)}")

        if response.get("success"):
            return APIResponse.success(message="Tạo loại phòng mới thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi tạo loại phòng: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi tạo loại phòng: {str(e)}", 500)


@room_types_bp.route("/<int:room_type_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room_type(room_type_id):
    """Edit existing room type"""
    # Handle form data
    room_type_data = {
        "type_name": request.form.get("type_name"),
        "capacity": request.form.get("capacity", type=int),
        "price": request.form.get("price", type=float),
    }

    # Basic validation
    errors = []
    if (
        not room_type_data.get("type_name")
        or not room_type_data.get("type_name").strip()
    ):
        errors.append("Tên loại phòng là bắt buộc")

    if not room_type_data.get("capacity") or room_type_data.get("capacity") <= 0:
        errors.append("Sức chứa phải là số dương")

    if not room_type_data.get("price") or room_type_data.get("price") <= 0:
        errors.append("Giá phòng phải là số dương")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        # Clean the data
        room_type_data["type_name"] = room_type_data["type_name"].strip()

        response = room_type_service.update_room_type(room_type_id, room_type_data)
        print(f"Response from edit_room_type: {json.dumps(response, indent=2)}")

        if response.get("success"):
            return APIResponse.success(message="Cập nhật loại phòng thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi cập nhật loại phòng: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi cập nhật loại phòng: {str(e)}", 500)


@room_types_bp.route("/<int:room_type_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room_type(room_type_id):
    """Delete room type"""
    try:
        response = room_type_service.delete_room_type(room_type_id)

        if response.get("success"):
            return APIResponse.success(message="Xóa loại phòng thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi xóa loại phòng: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi xóa loại phòng: {str(e)}", 500)


@room_types_bp.route("/<int:room_type_id>", methods=["GET"])
@login_required
@admin_required
def get_room_type(room_type_id):
    try:
        response = room_type_service.get_room_type(room_type_id)

        print(f"Response from get_room_type: {json.dumps(response, indent=2)}")

        if response.get("success"):
            room_type = response.get("data")
            return APIResponse.success(
                data=room_type, message="Lấy thông tin loại phòng thành công"
            )
        else:
            return APIResponse.error(
                f'Lỗi khi lấy thông tin loại phòng: {response.get("message", "")}', 404
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tải thông tin loại phòng: {str(e)}", 500)
