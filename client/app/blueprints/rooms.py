from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, management_required
from app.services.room_service import room_service
from app.forms.room_forms import RoomForm, RoomSearchForm, BuildingForm, RoomTypeForm
from app.utils.pagination import Pagination
from app.utils.form_helpers import (
    populate_room_form_choices,
    populate_room_search_form_choices,
)
from app.utils.api_response import APIResponse

# Blueprint registration
rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


@rooms_bp.route("/", methods=["GET"])
@login_required
@management_required
def list_rooms():
    """Display list of all rooms with search and filters"""
    search_form = RoomSearchForm()

    # Get filter parameters from request
    page = request.args.get("page", 1, type=int)
    building_id = request.args.get("building_id", type=int)
    room_type_id = request.args.get("room_type_id", type=int)
    status = request.args.get("status")
    search = request.args.get("search")

    # Populate filter dropdowns using helper function
    populate_room_search_form_choices(search_form)

    # Set form values from request args
    if building_id:
        search_form.building_id.data = building_id
    if room_type_id:
        search_form.room_type_id.data = room_type_id
    if status:
        search_form.status.data = status
    if search:
        search_form.search.data = search

    # Get rooms with filters
    try:
        result = room_service.get_rooms(
            page=page,
            building_id=building_id if building_id and building_id > 0 else None,
            room_type_id=room_type_id if room_type_id and room_type_id > 0 else None,
            status=status if status else None,
            search=search,
        )
        rooms = result.get("rooms", [])

        # Create a Pagination object from the API response
        pagination_data = result.get("pagination", {})

        # If pagination from API doesn't have 'pages', calculate it
        if (
            "pages" not in pagination_data
            and "total" in pagination_data
            and "per_page" in pagination_data
        ):
            total = pagination_data.get("total", 0)
            per_page = pagination_data.get("per_page", 10)
            pagination_data["pages"] = (
                (total + per_page - 1) // per_page if per_page > 0 else 1
            )

        # Convert dictionary to Pagination object for attribute access in template
        pagination = Pagination.from_dict(pagination_data)
    except Exception as e:
        flash(f"Lỗi khi tải danh sách phòng: {str(e)}", "danger")
        rooms = []
        pagination = Pagination.create_empty()

    return render_template(
        "rooms/list.html",
        rooms=rooms,
        pagination=pagination,
        form=search_form,
        title="Quản lý phòng",
    )


@rooms_bp.route("/<int:room_id>")
@login_required
@management_required
def get_room(room_id):
    """Get room details - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        # Non-AJAX requests should redirect to list
        return redirect(url_for('rooms.list_rooms'))

    try:
        room_data = room_service.get_room(room_id)

        if room_data.get('success'):
            return APIResponse.success(
                data={"room": room_data.get("room")},
                message="Lấy thông tin phòng thành công",
            )
        else:
            return APIResponse.error(room_data.get("error", "Lỗi không xác định"), 404)
    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy thông tin phòng: {str(e)}", 500)


@rooms_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_room():
    # Handle form data
    room_data = {
        "room_number": request.form.get("room_number"),
        "building_id": (
            int(request.form.get("building_id"))
            if request.form.get("building_id")
            else None
        ),
        "room_type_id": (
            int(request.form.get("room_type_id"))
            if request.form.get("room_type_id")
            else None
        ),
        "status": request.form.get("status", "available"),
        "description": request.form.get("description"),
    }

    # Basic validation
    errors = []
    if not room_data.get("room_number"):
        errors.append("Số phòng là bắt buộc")
    if not room_data.get("building_id"):
        errors.append("Tòa nhà là bắt buộc")
    if not room_data.get("room_type_id"):
        errors.append("Loại phòng là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        response = room_service.create_room(room_data)

        if response.get("success"):
            return APIResponse.success(message="Tạo phòng thành công!")
        else:
            return APIResponse.error(
                f'Lỗi khi tạo phòng: {response.get("error", "")}', 400
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tạo phòng: {str(e)}", 500)


@rooms_bp.route("/<int:room_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room_ajax(room_id):
    """Edit room - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        # Non-AJAX requests should use the original edit route
        return redirect(url_for('rooms.edit_room', room_id=room_id))

    # Handle form data
    room_data = {
        "room_number": request.form.get("room_number"),
        "building_id": (
            int(request.form.get("building_id"))
            if request.form.get("building_id")
            else None
        ),
        "room_type_id": (
            int(request.form.get("room_type_id"))
            if request.form.get("room_type_id")
            else None
        ),
        "status": request.form.get("status", "available"),
        "description": request.form.get("description"),
    }

    # Basic validation
    errors = []
    if not room_data.get("room_number"):
        errors.append("Số phòng là bắt buộc")
    if not room_data.get("building_id"):
        errors.append("Tòa nhà là bắt buộc")
    if not room_data.get("room_type_id"):
        errors.append("Loại phòng là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        response = room_service.update_room(room_id, room_data)

        if response.get("success"):
            return APIResponse.success(message="Cập nhật phòng thành công!")
        else:
            return APIResponse.error(
                f'Lỗi khi cập nhật phòng: {response.get("error", "")}', 400
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi cập nhật phòng: {str(e)}", 500)


@rooms_bp.route("/buildings")
@login_required
@management_required
def get_buildings():
    """Get buildings for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for("buildings.list_buildings"))

    try:
        response = room_service.get_buildings()
        return jsonify(response)
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tải danh sách tòa nhà: {str(e)}", 500)


@rooms_bp.route("/room-types")
@login_required
@management_required
def get_room_types():
    """Get room types for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for("room_types.list_room_types"))

    try:
        response = room_service.get_room_types()
        return jsonify(response)
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tải danh sách loại phòng: {str(e)}", 500)


@rooms_bp.route("/<int:room_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room(room_id):
    """Delete room"""
    # Check if it's an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            result = room_service.delete_room(room_id)
            if result.get("success"):
                return APIResponse.success(message="Xóa phòng thành công")
            else:
                return APIResponse.error(result.get("error", "Lỗi không xác định"), 400)
        except Exception as e:
            return APIResponse.error(f"Lỗi khi xóa phòng: {str(e)}", 500)
    else:
        # Regular form submission
        try:
            result = room_service.delete_room(room_id)
            flash("Xóa phòng thành công", "success")
        except Exception as e:
            error_msg = str(e)
            flash(f"Lỗi khi xóa phòng: {error_msg}", "danger")
        return redirect(url_for("rooms.list_rooms"))
