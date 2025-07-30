from app.services.building_service import building_service
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
buildings_bp = Blueprint("buildings", __name__)


# Building management routes
@buildings_bp.route("/", methods=["GET"])
@login_required
@admin_required
def list_buildings():
    """Display list of all buildings"""
    try:
        response = building_service.get_buildings()
        print(f"Response from get_buildings: {json.dumps(response, indent=2)}")

        # Check if we got a successful response
        if response.get("success") == False:
            flash(
                f'Lỗi khi tải danh sách tòa nhà: {response.get("message", "")}',
                "danger",
            )
            buildings = []
        else:
            buildings_data = response.get("data", {})
            buildings = buildings_data.get("buildings", [])
    except Exception as e:
        print(f"Error loading buildings: {str(e)}")
        flash(f"Lỗi khi tải danh sách tòa nhà: {str(e)}", "danger")
        buildings = []

    return render_template(
        "buildings/list.html", buildings=buildings, title="Quản lý tòa nhà"
    )


@buildings_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_building():
    """Create new building"""
    # Handle form data
    building_data = {
        "building_name": request.form.get("building_name"),
    }

    # Basic validation
    errors = []
    if (
        not building_data.get("building_name")
        or not building_data.get("building_name").strip()
    ):
        errors.append("Tên tòa nhà là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        # Clean the data
        building_data["building_name"] = building_data["building_name"].strip()

        response = building_service.create_building(building_data)

        if response.get("success"):
            return APIResponse.success(message="Tạo tòa nhà mới thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi tạo tòa nhà: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi tạo tòa nhà: {str(e)}", 500)


@buildings_bp.route("/<int:building_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_building(building_id):
    """Edit existing building"""
    # Handle form data
    building_data = {
        "building_name": request.form.get("building_name"),
    }

    # Basic validation
    errors = []
    if (
        not building_data.get("building_name")
        or not building_data.get("building_name").strip()
    ):
        errors.append("Tên tòa nhà là bắt buộc")

    if errors:
        return APIResponse.error("; ".join(errors), 400)

    try:
        # Clean the data
        building_data["building_name"] = building_data["building_name"].strip()

        response = building_service.update_building(building_id, building_data)
        print(f"Response from edit_building: {json.dumps(response, indent=2)}")

        if response.get("success"):
            return APIResponse.success(message="Cập nhật tòa nhà thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi cập nhật tòa nhà: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi cập nhật tòa nhà: {str(e)}", 500)


@buildings_bp.route("/<int:building_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_building(building_id):
    """Delete building"""
    try:
        response = building_service.delete_building(building_id)

        if response.get("success"):
            return APIResponse.success(message="Xóa tòa nhà thành công")
        else:
            return APIResponse.error(
                f'Lỗi khi xóa tòa nhà: {response.get("message", "")}', 400
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi xóa tòa nhà: {str(e)}", 500)


@buildings_bp.route("/<int:building_id>", methods=["GET"])
@login_required
@admin_required
def get_building(building_id):
    try:
        response = building_service.get_building(building_id)

        print(f"Response from get_building: {json.dumps(response, indent=2)}")

        if response.get("success"):
            building = response.get("data")
            return APIResponse.success(
                data=building, message="Lấy thông tin tòa nhà thành công"
            )
        else:
            return APIResponse.error(
                f'Lỗi khi lấy thông tin tòa nhà: {response.get("message", "")}', 404
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tải thông tin tòa nhà: {str(e)}", 500)


@buildings_bp.route("/api", methods=["GET"])
@login_required
@admin_required
def get_buildings_api():
    """Get buildings for dropdown - AJAX only"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('buildings.list_buildings'))

    try:
        response = building_service.get_buildings()

        if response.get("success"):
            return APIResponse.success(
                data=response.get("data"), message="Lấy danh sách tòa nhà thành công"
            )
        else:
            return APIResponse.error(
                f'Lỗi khi lấy danh sách tòa nhà: {response.get("message", "")}', 400
            )
    except Exception as e:
        return APIResponse.error(f"Lỗi khi tải danh sách tòa nhà: {str(e)}", 500)
