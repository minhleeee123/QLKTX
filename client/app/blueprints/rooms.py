from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, management_required
from app.services.room_service import room_service
from app.forms.room_forms import RoomForm, RoomSearchForm, BuildingForm, RoomTypeForm
from app.utils.pagination import Pagination

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

    # Populate filter dropdowns
    buildings_data = room_service.get_buildings()
    buildings = buildings_data.get("buildings", [])
    building_choices = [(0, "Tất cả")] + [
        (b["building_id"], b["building_name"]) for b in buildings
    ]
    search_form.building_id.choices = building_choices

    room_types_data = room_service.get_room_types()
    room_types = room_types_data.get("room_types", [])
    room_type_choices = [(0, "Tất cả")] + [
        (rt["room_type_id"], rt["type_name"]) for rt in room_types
    ]
    search_form.room_type_id.choices = room_type_choices

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
            return jsonify({
                'success': True, 
                'room': room_data.get('room')
            })
        else:
            return jsonify({
                'success': False,
                'message': room_data.get('error', 'Lỗi không xác định')
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy thông tin phòng: {str(e)}'
        }), 500


@rooms_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_room_ajax():
    """Create new room - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        # Non-AJAX requests should use the original create route
        return redirect(url_for('rooms.create_room'))
    
    # Handle form data
    room_data = {
        "room_number": request.form.get("room_number"),
        "building_id": int(request.form.get("building_id")) if request.form.get("building_id") else None,
        "room_type_id": int(request.form.get("room_type_id")) if request.form.get("room_type_id") else None,
        "capacity": int(request.form.get("capacity")) if request.form.get("capacity") else None,
        "monthly_price": float(request.form.get("monthly_price")) if request.form.get("monthly_price") else None,
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
    if not room_data.get("capacity") or room_data["capacity"] < 1:
        errors.append("Sức chứa phải là số nguyên dương")
    if room_data.get("monthly_price") is None or room_data["monthly_price"] < 0:
        errors.append("Giá hàng tháng phải là số không âm")

    if errors:
        return jsonify({"success": False, "message": "; ".join(errors)}), 400

    try:
        response = room_service.create_room(room_data)
        
        if response.get("success"):
            return jsonify({"success": True, "message": "Tạo phòng thành công!"})
        else:
            return jsonify({
                "success": False,
                "message": f'Lỗi khi tạo phòng: {response.get("error", "")}'
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f'Lỗi khi tạo phòng: {str(e)}'
        }), 500


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
        "building_id": int(request.form.get("building_id")) if request.form.get("building_id") else None,
        "room_type_id": int(request.form.get("room_type_id")) if request.form.get("room_type_id") else None,
        "capacity": int(request.form.get("capacity")) if request.form.get("capacity") else None,
        "monthly_price": float(request.form.get("monthly_price")) if request.form.get("monthly_price") else None,
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
    if not room_data.get("capacity") or room_data["capacity"] < 1:
        errors.append("Sức chứa phải là số nguyên dương")
    if room_data.get("monthly_price") is None or room_data["monthly_price"] < 0:
        errors.append("Giá hàng tháng phải là số không âm")

    if errors:
        return jsonify({"success": False, "message": "; ".join(errors)}), 400

    try:
        response = room_service.update_room(room_id, room_data)
        
        if response.get("success"):
            return jsonify({"success": True, "message": "Cập nhật phòng thành công!"})
        else:
            return jsonify({
                "success": False,
                "message": f'Lỗi khi cập nhật phòng: {response.get("error", "")}'
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f'Lỗi khi cập nhật phòng: {str(e)}'
        }), 500


@rooms_bp.route("/buildings")
@login_required
@management_required
def get_buildings():
    """Get buildings for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('rooms.list_buildings'))
    
    try:
        response = room_service.get_buildings()
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi tải danh sách tòa nhà: {str(e)}'
        }), 500


@rooms_bp.route("/room-types")
@login_required
@management_required
def get_room_types():
    """Get room types for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('rooms.list_room_types'))
    
    try:
        response = room_service.get_room_types()
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi tải danh sách loại phòng: {str(e)}'
        }), 500


@rooms_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_room():
    """Create new room"""
    form = RoomForm()

    # Populate dropdown choices
    buildings_data = room_service.get_buildings()
    buildings = buildings_data.get("buildings", [])
    form.building_id.choices = [
        (b["building_id"], b["building_name"]) for b in buildings
    ]

    room_types_data = room_service.get_room_types()
    room_types = room_types_data.get("room_types", [])
    form.room_type_id.choices = [
        (rt["room_type_id"], rt["type_name"]) for rt in room_types
    ]

    if form.validate_on_submit():
        room_data = {
            "room_number": form.room_number.data,
            "building_id": form.building_id.data,
            "room_type_id": form.room_type_id.data,
            "status": form.status.data,
            "current_occupancy": form.current_occupancy.data,
        }

        try:
            result = room_service.create_room(room_data)
            flash("Tạo phòng mới thành công", "success")
            return redirect(url_for("rooms.list_rooms"))
        except Exception as e:
            flash(f"Lỗi khi tạo phòng: {str(e)}", "danger")

    return render_template("rooms/form.html", form=form, title="Tạo phòng mới")


@rooms_bp.route("/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_room(room_id):
    """Edit existing room"""
    # Get room details
    try:
        room_data = room_service.get_room(room_id)
        room = room_data.get("room", {})
    except Exception as e:
        flash(f"Không tìm thấy phòng: {str(e)}", "danger")
        return redirect(url_for("rooms.list_rooms"))

    form = RoomForm()

    # Populate dropdown choices
    buildings_data = room_service.get_buildings()
    buildings = buildings_data.get("buildings", [])
    form.building_id.choices = [
        (b["building_id"], b["building_name"]) for b in buildings
    ]

    room_types_data = room_service.get_room_types()
    room_types = room_types_data.get("room_types", [])
    form.room_type_id.choices = [
        (rt["room_type_id"], rt["type_name"]) for rt in room_types
    ]

    # Fill form with room data
    if request.method == "GET":
        form.room_number.data = room.get("room_number")
        form.building_id.data = room.get("building", {}).get("building_id")
        form.room_type_id.data = room.get("room_type", {}).get("room_type_id")
        form.status.data = room.get("status")
        form.current_occupancy.data = room.get("current_occupancy")

    if form.validate_on_submit():
        room_data = {
            "room_number": form.room_number.data,
            "building_id": form.building_id.data,
            "room_type_id": form.room_type_id.data,
            "status": form.status.data,
            "current_occupancy": form.current_occupancy.data,
        }

        try:
            result = room_service.update_room(room_id, room_data)
            flash("Cập nhật phòng thành công", "success")
            return redirect(url_for("rooms.list_rooms"))
        except Exception as e:
            flash(f"Lỗi khi cập nhật phòng: {str(e)}", "danger")

    return render_template(
        "rooms/form.html", form=form, title="Chỉnh sửa phòng", room=room
    )


@rooms_bp.route("/<int:room_id>/view", methods=["GET"])
@login_required
@management_required
def view_room(room_id):
    """View room details"""
    try:
        room_data = room_service.get_room(room_id)
        room = room_data.get("room", {})
    except Exception as e:
        flash(f"Không tìm thấy phòng: {str(e)}", "danger")
        return redirect(url_for("rooms.list_rooms"))

    return render_template("rooms/view.html", room=room, title="Chi tiết phòng")


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
                return jsonify({"success": True, "message": "Xóa phòng thành công"})
            else:
                return jsonify({
                    "success": False,
                    "message": result.get("error", "Lỗi không xác định")
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi khi xóa phòng: {str(e)}"
            }), 500
    else:
        # Regular form submission
        try:
            result = room_service.delete_room(room_id)
            flash("Xóa phòng thành công", "success")
        except Exception as e:
            error_msg = str(e)
            flash(f"Lỗi khi xóa phòng: {error_msg}", "danger")
        return redirect(url_for("rooms.list_rooms"))


# Building management routes
@rooms_bp.route("/buildings", methods=["GET"])
@login_required
@admin_required
def list_buildings():
    """Display list of all buildings"""
    try:
        buildings_data = room_service.get_buildings()
        buildings = buildings_data.get("buildings", [])
    except Exception as e:
        flash(f"Lỗi khi tải danh sách tòa nhà: {str(e)}", "danger")
        buildings = []

    return render_template(
        "rooms/buildings.html", buildings=buildings, title="Quản lý tòa nhà"
    )


@rooms_bp.route("/buildings/create", methods=["POST"])
@login_required
@admin_required
def create_building():
    """Create new building"""
    building_name = request.form.get("building_name")

    if not building_name:
        flash("Tên tòa nhà là bắt buộc", "danger")
        return redirect(url_for("rooms.list_buildings"))

    try:
        building_data = {"building_name": building_name}
        result = room_service.create_building(building_data)
        flash("Tạo tòa nhà mới thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi tạo tòa nhà: {str(e)}", "danger")

    return redirect(url_for("rooms.list_buildings"))


@rooms_bp.route("/buildings/<int:building_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_building(building_id):
    """Edit existing building"""
    building_name = request.form.get("building_name")

    if not building_name:
        flash("Tên tòa nhà là bắt buộc", "danger")
        return redirect(url_for("rooms.list_buildings"))

    try:
        building_data = {"building_name": building_name}
        result = room_service.update_building(building_id, building_data)
        flash("Cập nhật tòa nhà thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật tòa nhà: {str(e)}", "danger")

    return redirect(url_for("rooms.list_buildings"))


@rooms_bp.route("/buildings/<int:building_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_building(building_id):
    """Delete building"""
    try:
        result = room_service.delete_building(building_id)
        flash("Xóa tòa nhà thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa tòa nhà: {str(e)}", "danger")

    return redirect(url_for("rooms.list_buildings"))


# Room types management routes
@rooms_bp.route("/room-types", methods=["GET"])
@login_required
@admin_required
def list_room_types():
    """Display list of all room types"""
    try:
        room_types_data = room_service.get_room_types()
        room_types = room_types_data.get("room_types", [])
    except Exception as e:
        flash(f"Lỗi khi tải danh sách loại phòng: {str(e)}", "danger")
        room_types = []

    return render_template(
        "rooms/room_types.html", room_types=room_types, title="Quản lý loại phòng"
    )


@rooms_bp.route("/room-types/create", methods=["POST"])
@login_required
@admin_required
def create_room_type():
    """Create new room type"""
    type_name = request.form.get("type_name")
    capacity = request.form.get("capacity", type=int)
    price = request.form.get("price", type=float)

    if not all([type_name, capacity, price]):
        flash("Vui lòng điền đầy đủ thông tin", "danger")
        return redirect(url_for("rooms.list_room_types"))

    try:
        room_type_data = {"type_name": type_name, "capacity": capacity, "price": price}
        result = room_service.create_room_type(room_type_data)
        flash("Tạo loại phòng mới thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi tạo loại phòng: {str(e)}", "danger")

    return redirect(url_for("rooms.list_room_types"))


@rooms_bp.route("/room-types/<int:room_type_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room_type(room_type_id):
    """Edit existing room type"""
    type_name = request.form.get("type_name")
    capacity = request.form.get("capacity", type=int)
    price = request.form.get("price", type=float)

    if not all([type_name, capacity, price]):
        flash("Vui lòng điền đầy đủ thông tin", "danger")
        return redirect(url_for("rooms.list_room_types"))

    try:
        room_type_data = {"type_name": type_name, "capacity": capacity, "price": price}
        result = room_service.update_room_type(room_type_id, room_type_data)
        flash("Cập nhật loại phòng thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật loại phòng: {str(e)}", "danger")

    return redirect(url_for("rooms.list_room_types"))


@rooms_bp.route("/room-types/<int:room_type_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room_type(room_type_id):
    """Delete room type"""
    try:
        result = room_service.delete_room_type(room_type_id)
        flash("Xóa loại phòng thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa loại phòng: {str(e)}", "danger")

    return redirect(url_for("rooms.list_room_types"))
