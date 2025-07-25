from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.services.room_service import room_service

# Blueprint registration
room_types_bp = Blueprint("room_types", __name__, url_prefix="/room-types")


# Room types management routes
@room_types_bp.route("/", methods=["GET"])
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
        "room_types/list.html", room_types=room_types, title="Quản lý loại phòng"
    )


@room_types_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_room_type():
    """Create new room type"""
    type_name = request.form.get("type_name")
    capacity = request.form.get("capacity", type=int)
    price = request.form.get("price", type=float)

    if not all([type_name, capacity, price]):
        flash("Vui lòng điền đầy đủ thông tin", "danger")
        return redirect(url_for("room_types.list_room_types"))

    try:
        room_type_data = {"type_name": type_name, "capacity": capacity, "price": price}
        result = room_service.create_room_type(room_type_data)
        flash("Tạo loại phòng mới thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi tạo loại phòng: {str(e)}", "danger")

    return redirect(url_for("room_types.list_room_types"))


@room_types_bp.route("/<int:room_type_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room_type(room_type_id):
    """Edit existing room type"""
    type_name = request.form.get("type_name")
    capacity = request.form.get("capacity", type=int)
    price = request.form.get("price", type=float)

    if not all([type_name, capacity, price]):
        flash("Vui lòng điền đầy đủ thông tin", "danger")
        return redirect(url_for("room_types.list_room_types"))

    try:
        room_type_data = {"type_name": type_name, "capacity": capacity, "price": price}
        result = room_service.update_room_type(room_type_id, room_type_data)
        flash("Cập nhật loại phòng thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật loại phòng: {str(e)}", "danger")

    return redirect(url_for("room_types.list_room_types"))


@room_types_bp.route("/<int:room_type_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room_type(room_type_id):
    """Delete room type"""
    try:
        result = room_service.delete_room_type(room_type_id)
        flash("Xóa loại phòng thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa loại phòng: {str(e)}", "danger")

    return redirect(url_for("room_types.list_room_types"))


@room_types_bp.route("/api", methods=["GET"])
@login_required
@admin_required
def get_room_types_api():
    """Get room types for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('room_types.list_room_types'))
    
    try:
        response = room_service.get_room_types()
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi tải danh sách loại phòng: {str(e)}'
        }), 500
