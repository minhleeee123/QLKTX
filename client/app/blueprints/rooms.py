from app.forms.room_forms import BuildingForm, RoomForm, RoomSearchForm, RoomTypeForm
from app.services.building_service import building_service
from app.services.room_service import room_service
from app.services.room_type_service import room_type_service
from app.utils.api_response import APIResponse
from app.utils.decorators import admin_required, management_required
from app.utils.form_helpers import (
    populate_room_form_choices,
    populate_room_search_form_choices,
)
from app.utils.pagination import Pagination
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
rooms_bp = Blueprint("rooms", __name__)


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
    response = room_service.get_rooms(
        page=page,
        building_id=building_id if building_id and building_id > 0 else None,
        room_type_id=room_type_id if room_type_id and room_type_id > 0 else None,
        status=status if status else None,
        search=search,
    )

    # Check if we got a successful response
    if response.get("success") == False:
        # Handle error response
        flash(f'Lỗi khi tải danh sách phòng: {response.get("message", "")}', "danger")
        return render_template(
            "rooms/list.html",
            rooms=[],
            pagination=Pagination.create_empty(),
            form=search_form,
            title="Quản lý phòng",
        )
    else:
        # Handle successful response
        data = response.get("data", {})
        rooms = data.get("rooms", [])
        pagination_data = data.get("pagination", {})

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
    response = room_service.get_room(room_id)

    if response.get("success"):
        room = response.get("data")
        return APIResponse.success(
            data=room,
            message="Lấy thông tin phòng thành công",
        )
    else:
        return APIResponse.error(
            f'Lỗi khi lấy thông tin phòng: {response.get("message", "")}', 404
        )


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

    response = room_service.create_room(room_data)
    print(response)  # Debugging line to check response structure

    if response.get("success"):
        return APIResponse.success(message="Tạo phòng thành công!")
    else:
        return APIResponse.error(
            f'Lỗi khi tạo phòng: {response.get("message", "")}', 400
        )


@rooms_bp.route("/<int:room_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room(room_id):
    # Handle form data
    room_data = {
        "room_type_id": (
            int(request.form.get("room_type_id"))
            if request.form.get("room_type_id")
            else None
        ),
        "status": request.form.get("status", "available"),
        "description": request.form.get("description"),
    }

    print("Room data to update:", room_data)  # Debugging line to check room data

    # Basic validation
    errors = []
    if not room_data.get("room_type_id"):
        errors.append("Loại phòng là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    response = room_service.update_room(room_id, room_data)

    if response.get("success"):
        return APIResponse.success(message="Cập nhật phòng thành công!")
    else:
        return APIResponse.error(
            f'Lỗi khi cập nhật phòng: {response.get("message", "")}', 400
        )


@rooms_bp.route("/buildings")
@login_required
@management_required
def get_buildings():
    response = building_service.get_buildings()
    return jsonify(response)


@rooms_bp.route("/room-types")
@login_required
@management_required
def get_room_types():
    response = room_type_service.get_room_types()
    return jsonify(response)


@rooms_bp.route("/<int:room_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room(room_id):
    response = room_service.delete_room(room_id)

    if response.get("success"):
        return APIResponse.success(message="Xóa phòng thành công")
    else:
        return APIResponse.error(
            f'Lỗi khi xóa phòng: {response.get("message", "")}', 400
        )
