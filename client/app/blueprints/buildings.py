from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.services.room_service import room_service

# Blueprint registration
buildings_bp = Blueprint("buildings", __name__, url_prefix="/buildings")


# Building management routes
@buildings_bp.route("/", methods=["GET"])
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
        "buildings/buildings.html", buildings=buildings, title="Quản lý tòa nhà"
    )


@buildings_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_building():
    """Create new building"""
    building_name = request.form.get("building_name")

    if not building_name:
        flash("Tên tòa nhà là bắt buộc", "danger")
        return redirect(url_for("buildings.list_buildings"))

    try:
        building_data = {"building_name": building_name}
        result = room_service.create_building(building_data)
        flash("Tạo tòa nhà mới thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi tạo tòa nhà: {str(e)}", "danger")

    return redirect(url_for("buildings.list_buildings"))


@buildings_bp.route("/<int:building_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_building(building_id):
    """Edit existing building"""
    building_name = request.form.get("building_name")

    if not building_name:
        flash("Tên tòa nhà là bắt buộc", "danger")
        return redirect(url_for("buildings.list_buildings"))

    try:
        building_data = {"building_name": building_name}
        result = room_service.update_building(building_id, building_data)
        flash("Cập nhật tòa nhà thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật tòa nhà: {str(e)}", "danger")

    return redirect(url_for("buildings.list_buildings"))


@buildings_bp.route("/<int:building_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_building(building_id):
    """Delete building"""
    try:
        result = room_service.delete_building(building_id)
        flash("Xóa tòa nhà thành công", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa tòa nhà: {str(e)}", "danger")

    return redirect(url_for("buildings.list_buildings"))


@buildings_bp.route("/api", methods=["GET"])
@login_required
@admin_required
def get_buildings_api():
    """Get buildings for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('buildings.list_buildings'))
    
    try:
        response = room_service.get_buildings()
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi khi tải danh sách tòa nhà: {str(e)}'
        }), 500
