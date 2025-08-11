from app.services.building_service import building_service
from app.services.registration_service import registration_service
from app.services.room_service import room_service
from app.services.room_type_service import room_type_service
from app.utils.api_response import APIResponse
from app.utils.decorators import student_required
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
student_rooms_bp = Blueprint("student_rooms", __name__, url_prefix="/student")


@student_rooms_bp.route("/rooms")
@login_required
@student_required
def browse_rooms():
    """Browse available rooms for students"""
    # Get filter parameters from request
    page = request.args.get("page", 1, type=int)
    building_id = request.args.get("building_id", type=int)
    room_type_id = request.args.get("room_type_id", type=int)
    search = request.args.get("search")

    try:
        # Get available rooms only (students should only see available rooms)
        response = room_service.get_rooms(
            page=page,
            per_page=12,  # Show more rooms per page for browsing
            building_id=building_id if building_id and building_id > 0 else None,
            room_type_id=room_type_id if room_type_id and room_type_id > 0 else None,
            status="available",  # Only show available rooms
            search=search,
        )

        if not response.get("success"):
            flash(f'Lỗi khi tải danh sách phòng: {response.get("message", "")}', "danger")
            rooms_data = {"rooms": [], "pagination": {}}
        else:
            rooms_data = response.get("data", {})

        # Get buildings and room types for filters
        buildings_response = building_service.get_buildings()
        buildings = buildings_response.get("data", {}).get("buildings", []) if buildings_response.get("success") else []

        room_types_response = room_type_service.get_room_types()
        room_types = room_types_response.get("data", {}).get("room_types", []) if room_types_response.get("success") else []

        # Get student's current registrations to show status
        registrations_response = registration_service.get_registrations()
        user_registrations = {}
        if registrations_response.get("success"):
            registrations = registrations_response.get("data", {}).get("registrations", [])
            for reg in registrations:
                user_registrations[reg["room"]["room_id"]] = {
                    "registration_id": reg["registration_id"],
                    "status": reg["status"]
                }

        return render_template(
            "student_rooms/browse.html",
            rooms=rooms_data.get("rooms", []),
            pagination=rooms_data.get("pagination", {}),
            buildings=buildings,
            room_types=room_types,
            user_registrations=user_registrations,
            current_page=page,
            filters={
                "building_id": building_id,
                "room_type_id": room_type_id,
                "search": search
            },
            title="Chọn phòng ký túc xá",
        )

    except Exception as e:
        flash(f"Lỗi khi tải danh sách phòng: {str(e)}", "danger")
        return render_template(
            "student_rooms/browse.html",
            rooms=[],
            pagination={},
            buildings=[],
            room_types=[],
            user_registrations={},
            current_page=1,
            filters={},
            title="Chọn phòng ký túc xá",
        )


@student_rooms_bp.route("/rooms/<int:room_id>")
@login_required
@student_required
def room_details(room_id):
    """Get room details for students"""
    try:
        response = room_service.get_room(room_id)

        if response.get("success"):
            room_data = response.get("data")
            return APIResponse.success(
                data=room_data,
                message="Lấy thông tin phòng thành công",
            )
        else:
            return APIResponse.error(
                f'Lỗi khi lấy thông tin phòng: {response.get("message", "")}', 404
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy thông tin phòng: {str(e)}", 500)


@student_rooms_bp.route("/register/<int:room_id>", methods=["POST"])
@login_required
@student_required
def register_room(room_id):
    """Register for a room"""
    try:
        response = registration_service.create_registration(room_id)

        if response.get("success"):
            return APIResponse.success(
                data=response.get("data"),
                message="Đăng ký phòng thành công! Vui lòng chờ admin duyệt.",
            )
        else:
            return APIResponse.error(
                response.get("message", "Có lỗi xảy ra khi đăng ký phòng"), 
                response.get("status_code", 400)
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi đăng ký phòng: {str(e)}", 500)


@student_rooms_bp.route("/registrations")
@login_required
@student_required
def my_registrations():
    """View student's registrations"""
    try:
        page = request.args.get("page", 1, type=int)
        status = request.args.get("status")

        response = registration_service.get_registrations(
            page=page,
            per_page=10,
            status=status
        )

        if not response.get("success"):
            flash(f'Lỗi khi tải danh sách đăng ký: {response.get("message", "")}', "danger")
            registrations_data = {"registrations": [], "pagination": {}}
        else:
            registrations_data = response.get("data", {})

        return render_template(
            "student_rooms/registrations.html",
            registrations=registrations_data.get("registrations", []),
            pagination=registrations_data.get("pagination", {}),
            current_page=page,
            status_filter=status,
            title="Đơn đăng ký của tôi",
        )

    except Exception as e:
        flash(f"Lỗi khi tải danh sách đăng ký: {str(e)}", "danger")
        return render_template(
            "student_rooms/registrations.html",
            registrations=[],
            pagination={},
            current_page=1,
            status_filter=None,
            title="Đơn đăng ký của tôi",
        )


@student_rooms_bp.route("/registrations/<int:registration_id>/cancel", methods=["POST"])
@login_required
@student_required
def cancel_registration(registration_id):
    """Cancel a registration"""
    try:
        response = registration_service.cancel_registration(registration_id)

        if response.get("success"):
            return APIResponse.success(message="Hủy đăng ký thành công!")
        else:
            return APIResponse.error(
                response.get("message", "Có lỗi xảy ra khi hủy đăng ký"), 
                response.get("status_code", 400)
            )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi hủy đăng ký: {str(e)}", 500)
