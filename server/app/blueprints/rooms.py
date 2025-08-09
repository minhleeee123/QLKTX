from app.extensions import db
from app.models import Building, Room, RoomType, User
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route("/", methods=["GET"])
@jwt_required()
def get_rooms():
    """
    Lấy danh sách phòng với phân trang và tìm kiếm

    Method: GET
    Query Parameters:
        page: int = 1              # Trang hiện tại (optional)
        per_page: int = 20         # Số phòng mỗi trang (optional)
        building_id: int           # Lọc theo ID tòa nhà (optional)
        room_type_id: int          # Lọc theo ID loại phòng (optional)
        status: string             # Lọc theo trạng thái phòng: 'available', 'occupied', 'maintenance' (optional)
        search: string             # Tìm kiếm theo số phòng (optional)

    Example URL: GET /rooms?page=1&per_page=20&building_id=1&status=available&search=101

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách phòng thành công",
        "data": {
            "rooms": [
                {
                    "room_id": 1,
                    "room_number": "101",
                    "building": {
                        "building_id": 1,
                        "building_name": "Tòa A"
                    },
                    "room_type": {
                        "room_type_id": 1,
                        "type_name": "Phòng đơn",
                        "capacity": 2,
                        "price_per_month": 1000000
                    },
                    "status": "available",
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "pagination": {
                "page": 1,
                "pages": 5,
                "per_page": 20,
                "total": 100,
                "has_next": true,
                "has_prev": false
            }
        },
        "status_code": 200
    }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        building_id = request.args.get('building_id', type=int)
        room_type_id = request.args.get('room_type_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')

        query = Room.query.join(Building).join(RoomType)

        # Filters
        if building_id:
            query = query.filter(Room.building_id == building_id)
        if room_type_id:
            query = query.filter(Room.room_type_id == room_type_id)
        if status:
            query = query.filter(Room.status == status)
        if search:
            query = query.filter(Room.room_number.contains(search))

        rooms = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        rooms_data = {
            "rooms": [
                {
                    "room_id": room.room_id,
                    "room_number": room.room_number,
                    "building": {
                        "building_id": room.building.building_id,
                        "building_name": room.building.building_name,
                    },
                    "room_type": {
                        "room_type_id": room.room_type.room_type_id,
                        "type_name": room.room_type.type_name,
                        "capacity": room.room_type.capacity,
                        "price": float(room.room_type.price),
                    },
                    "status": room.status,
                    "current_occupancy": room.current_occupancy,
                    "available_slots": room.remaining_capacity,
                    "is_available": room.is_available,
                }
                for room in rooms.items
            ],
            "pagination": {
                "page": rooms.page,
                "pages": rooms.pages,
                "per_page": rooms.per_page,
                "total": rooms.total,
                "has_next": rooms.has_next,
                "has_prev": rooms.has_prev,
            },
        }

        return APIResponse.success(
            data=rooms_data, message="Lấy danh sách phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@rooms_bp.route("/<int:room_id>", methods=["GET"])
@jwt_required()
def get_room(room_id):
    """
    Lấy thông tin chi tiết một phòng

    Method: GET
    URL Parameters:
        room_id: int               # ID của phòng cần lấy thông tin

    Example URL: GET /rooms/123

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy thông tin phòng thành công",
        "data": {
            "room": {
                "room_id": 1,
                "room_number": "101",
                "building": {
                    "building_id": 1,
                    "building_name": "Tòa A"
                },
                "room_type": {
                    "room_type_id": 1,
                    "type_name": "Phòng đơn",
                    "capacity": 2,
                    "price_per_month": 1000000
                },
                "status": "available",
                "created_at": "2024-01-01T00:00:00"
            }
        },
        "status_code": 200
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Phòng không tồn tại",
        "data": null,
        "status_code": 404
    }
    """
    try:
        room = Room.query.get(room_id)
        if not room:
            return APIResponse.error(message="Phòng không tồn tại", status_code=404)

        room_data = {
            "room": {
                "room_id": room.room_id,
                "room_number": room.room_number,
                "building_id": room.building_id,  # Add building_id for forms
                "room_type_id": room.room_type_id,  # Add room_type_id for forms
                "building": {
                    "building_id": room.building.building_id,
                    "building_name": room.building.building_name,
                },
                "room_type": {
                    "room_type_id": room.room_type.room_type_id,
                    "type_name": room.room_type.type_name,
                    "capacity": room.room_type.capacity,
                    "price": float(room.room_type.price),
                },
                "status": room.status,
                "current_occupancy": room.current_occupancy,
                "available_slots": room.remaining_capacity,
                "is_available": room.is_available,
                "description": getattr(
                    room, "description", None
                ),  # Add description field
                "created_at": (
                    room.created_at.isoformat()
                    if hasattr(room, "created_at") and room.created_at
                    else None
                ),
            }
        }

        return APIResponse.success(
            data=room_data, message="Lấy thông tin phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@rooms_bp.route("/", methods=["POST"])
@jwt_required()
@require_role(["admin", "management"])
def create_room():
    """
    Tạo phòng mới

    Method: POST
    Headers:
        Authorization: Bearer <access_token> (nếu bật JWT)
        Content-Type: application/json

    Permissions: Admin và management có thể tạo phòng mới

    Request JSON:
    {
        "room_number": "101",          # Required: Số phòng (unique trong cùng tòa nhà)
        "building_id": 1,              # Required: ID tòa nhà
        "room_type_id": 1,            # Required: ID loại phòng
        "status": "available",         # Optional: Trạng thái phòng (default: 'available')
        "description": "Mô tả phòng"  # Optional: Mô tả phòng
    }

    Response JSON (Success - 201):
    {
        "success": true,
        "message": "Tạo phòng thành công",
        "data": {
            "room": {
                "room_id": 1,
                "room_number": "101",
                "building": {
                    "building_id": 1,
                    "building_name": "Tòa A"
                },
                "room_type": {
                    "room_type_id": 1,
                    "type_name": "Phòng đơn",
                    "capacity": 2,
                    "price_per_month": 1000000
                },
                "status": "available",
                "created_at": "2024-01-01T00:00:00"
            }
        },
        "status_code": 201
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Số phòng đã tồn tại trong tòa nhà này" | "Building không tồn tại" | "Room type không tồn tại",
        "data": null,
        "status_code": 400
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['room_number', 'building_id', 'room_type_id']
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Kiểm tra phòng đã tồn tại
        existing_room = Room.query.filter_by(
            room_number=data['room_number'],
            building_id=data['building_id']
        ).first()
        if existing_room:
            return APIResponse.error(
                message="Phòng đã tồn tại trong tòa nhà này", status_code=400
            )

        # Kiểm tra building và room_type tồn tại
        building = Building.query.get(data['building_id'])
        if not building:
            return APIResponse.error(message="Tòa nhà không tồn tại", status_code=400)

        room_type = RoomType.query.get(data['room_type_id'])
        if not room_type:
            return APIResponse.error(
                message="Loại phòng không tồn tại", status_code=400
            )

        # Tạo phòng mới
        room = Room(
            room_number=data['room_number'],
            building_id=data['building_id'],
            room_type_id=data['room_type_id'],
            status=data.get('status', 'available'),
            current_occupancy=data.get('current_occupancy', 0)
        )

        db.session.add(room)
        db.session.commit()

        room_data = {
            "room": {
                "room_id": room.room_id,
                "room_number": room.room_number,
                "building_name": room.building.building_name,
                "room_type_name": room.room_type.type_name,
            }
        }

        return APIResponse.success(
            data=room_data, message="Tạo phòng thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@rooms_bp.route("/<int:room_id>", methods=["PUT"])
@jwt_required()
@require_role(["admin", "management"])
def update_room(room_id):
    """Cập nhật thông tin phòng"""
    try:
        room = Room.query.get(room_id)
        if not room:
            return APIResponse.error(message="Phòng không tồn tại", status_code=404)

        data = request.get_json()

        # Cập nhật các trường cho phép
        if 'status' in data:
            room.status = data['status']
        if 'current_occupancy' in data:
            room.current_occupancy = data['current_occupancy']
        if 'room_type_id' in data:
            room_type = RoomType.query.get(data['room_type_id'])
            if room_type:
                room.room_type_id = data['room_type_id']

        db.session.commit()

        room_data = {
            "room": {
                "room_id": room.room_id,
                "room_number": room.room_number,
                "status": room.status,
                "current_occupancy": room.current_occupancy,
            }
        }

        return APIResponse.success(data=room_data, message="Cập nhật phòng thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
@jwt_required()
@require_role(["admin"])
def delete_room(room_id):
    """
    Xóa phòng

    Method: DELETE
    URL: /rooms/{room_id}
    Headers: Authorization: Bearer <token>

    Example: DELETE /rooms/1

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Xóa phòng thành công",
        "data": null,
        "status_code": 200
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Phòng không tồn tại",
        "data": null,
        "status_code": 404
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Không thể xóa phòng đang được sử dụng",
        "data": null,
        "status_code": 400
    }
    """

    try:
        room = Room.query.get(room_id)
        if not room:
            return APIResponse.error(message="Phòng không tồn tại", status_code=404)

        # Check if room is currently occupied
        if room.current_occupancy > 0:
            return APIResponse.error(
                message="Không thể xóa phòng đang được sử dụng", status_code=400
            )

        # Check if room has any registrations (pending, approved, rejected)
        from app.models import Registration

        registrations_count = Registration.query.filter_by(room_id=room_id).count()
        if registrations_count > 0:
            return APIResponse.error(
                message="Không thể xóa phòng có đơn đăng ký liên quan", status_code=400
            )

        # Check if room has any active contracts through registrations
        from app.models import Contract

        active_contracts = (
            db.session.query(Contract)
            .join(Registration)
            .filter(
                Registration.room_id == room_id,
                Contract.start_date <= db.func.current_date(),
                Contract.end_date >= db.func.current_date(),
            )
            .count()
        )

        if active_contracts > 0:
            return APIResponse.error(
                message="Không thể xóa phòng có hợp đồng đang hoạt động",
                status_code=400,
            )

        # Check if room has any pending maintenance requests
        from app.models import MaintenanceRequest

        pending_maintenance = MaintenanceRequest.query.filter(
            MaintenanceRequest.room_id == room_id,
            MaintenanceRequest.status.in_(["pending", "assigned", "in_progress"]),
        ).count()

        if pending_maintenance > 0:
            return APIResponse.error(
                message="Không thể xóa phòng có yêu cầu bảo trì đang xử lý",
                status_code=400,
            )

        # Safe to delete room - all related data has been checked
        db.session.delete(room)
        db.session.commit()

        return APIResponse.success(message="Xóa phòng thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)
