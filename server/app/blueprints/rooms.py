from app.extensions import db
from app.models import Building, Room, RoomType, User
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, json, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/', methods=['GET'])
# @jwt_required()
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

@rooms_bp.route('/<int:room_id>', methods=['GET'])
# @jwt_required()
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

@rooms_bp.route('/', methods=['POST'])
# @jwt_required()
# @require_role(['admin', 'management'])
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

@rooms_bp.route('/buildings', methods=['GET'])
# @jwt_required()
def get_buildings():
    """Lấy danh sách tòa nhà"""
    try:
        buildings = Building.query.all()

        buildings_data = {
            "buildings": [
                {
                    "building_id": building.building_id,
                    "building_name": building.building_name,
                    "total_rooms": len(building.rooms),
                    "available_rooms": len(
                        [r for r in building.rooms if r.status == "available"]
                    ),
                }
                for building in buildings
            ]
        }

        return APIResponse.success(
            data=buildings_data, message="Lấy danh sách tòa nhà thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/buildings', methods=['POST'])
# @jwt_required()
# @require_role(['admin', 'management'])
def create_building():
    """Tạo tòa nhà mới"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('building_name'):
            return APIResponse.error(message="Tên tòa nhà là bắt buộc", status_code=400)

        # Kiểm tra tòa nhà đã tồn tại
        existing_building = Building.query.filter_by(building_name=data['building_name']).first()
        if existing_building:
            return APIResponse.error(message="Tòa nhà đã tồn tại", status_code=400)

        # Tạo tòa nhà mới
        building = Building(building_name=data['building_name'])

        db.session.add(building)
        db.session.commit()

        building_data = {
            "building": {
                "building_id": building.building_id,
                "building_name": building.building_name,
            }
        }

        return APIResponse.success(
            data=building_data, message="Tạo tòa nhà thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/buildings/<int:building_id>', methods=['GET'])
# @jwt_required()
def get_building(building_id):
    """Lấy thông tin chi tiết một tòa nhà"""
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error(message="Tòa nhà không tồn tại", status_code=404)

        building_data = {
            "building": {
                "building_id": building.building_id,
                "building_name": building.building_name,
                "total_rooms": len(building.rooms),
                "available_rooms": len(
                    [r for r in building.rooms if r.status == "available"]
                ),
            }
        }

        return APIResponse.success(
            data=building_data, message="Lấy thông tin tòa nhà thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/buildings/<int:building_id>', methods=['PUT'])
# @jwt_required()
# @require_role(['admin', 'management'])
def update_building(building_id):
    """Cập nhật thông tin tòa nhà"""
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error(message="Tòa nhà không tồn tại", status_code=404)

        data = request.get_json()

        if not data.get('building_name'):
            return APIResponse.error(message="Tên tòa nhà là bắt buộc", status_code=400)

        # Kiểm tra tên tòa nhà đã tồn tại (trừ chính nó)
        existing_building = Building.query.filter(
            Building.building_name == data['building_name'],
            Building.building_id != building_id
        ).first()
        if existing_building:
            return APIResponse.error(message="Tên tòa nhà đã tồn tại", status_code=400)

        # Cập nhật thông tin
        building.building_name = data['building_name']

        db.session.commit()

        building_data = {
            "building": {
                "building_id": building.building_id,
                "building_name": building.building_name,
            }
        }

        return APIResponse.success(
            data=building_data, message="Cập nhật tòa nhà thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/buildings/<int:building_id>', methods=['DELETE', 'POST'])
# @jwt_required()
# @require_role(['admin'])
def delete_building(building_id):
    """Xóa tòa nhà (chỉ Admin)"""
    print(f"[SERVER DEBUG] delete_building called with building_id: {building_id}")
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error(message="Tòa nhà không tồn tại", status_code=404)

        # Kiểm tra tòa nhà có phòng không
        if building.rooms:
            return APIResponse.error(
                message=f"Không thể xóa tòa nhà này vì đang có {len(building.rooms)} phòng.",
                status_code=400,
            )

        db.session.delete(building)
        db.session.commit()

        return APIResponse.success(message="Xóa tòa nhà thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/room-types', methods=['GET'])
# @jwt_required()
def get_room_types():
    """Lấy danh sách loại phòng"""
    try:
        room_types = RoomType.query.all()

        room_types_data = {
            "room_types": [
                {
                    "room_type_id": rt.room_type_id,
                    "type_name": rt.type_name,
                    "capacity": rt.capacity,
                    "price": float(rt.price),
                    "total_rooms": len(rt.rooms),
                    "available_rooms": len(
                        [r for r in rt.rooms if r.status == "available"]
                    ),
                }
                for rt in room_types
            ]
        }

        return APIResponse.success(
            data=room_types_data, message="Lấy danh sách loại phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/room-types', methods=['POST'])
# @jwt_required()
# @require_role(['admin', 'management'])
def create_room_type():
    """Tạo loại phòng mới"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['type_name', 'capacity', 'price']
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Validate data types and values
        try:
            capacity = int(data['capacity'])
            price = float(data['price'])
        except ValueError:
            return APIResponse.error(
                message="Sức chứa và giá phòng phải là số", status_code=400
            )

        if capacity <= 0:
            return APIResponse.error(message="Sức chứa phải lớn hơn 0", status_code=400)
        if price < 0:
            return APIResponse.error(message="Giá phòng không được âm", status_code=400)

        # Kiểm tra loại phòng đã tồn tại
        existing_room_type = RoomType.query.filter_by(type_name=data['type_name']).first()
        if existing_room_type:
            return APIResponse.error(message="Loại phòng đã tồn tại", status_code=400)

        # Tạo loại phòng mới
        room_type = RoomType(
            type_name=data['type_name'],
            capacity=capacity,
            price=price
        )

        db.session.add(room_type)
        db.session.commit()

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Tạo loại phòng thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/room-types/<int:room_type_id>', methods=['GET'])
# @jwt_required()
def get_room_type(room_type_id):
    """Lấy thông tin chi tiết một loại phòng"""
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return APIResponse.error(
                message="Loại phòng không tồn tại", status_code=404
            )

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
                "total_rooms": len(room_type.rooms),
                "available_rooms": len(
                    [r for r in room_type.rooms if r.status == "available"]
                ),
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Lấy thông tin loại phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/room-types/<int:room_type_id>', methods=['PUT'])
# @jwt_required()
# @require_role(['admin', 'management'])
def update_room_type(room_type_id):
    """Cập nhật thông tin loại phòng"""
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return APIResponse.error(
                message="Loại phòng không tồn tại", status_code=404
            )

        data = request.get_json()

        # Validate required fields
        required_fields = ['type_name', 'capacity', 'price']
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Validate data types and values
        try:
            capacity = int(data['capacity'])
            price = float(data['price'])
        except ValueError:
            return APIResponse.error(
                message="Sức chứa và giá phòng phải là số", status_code=400
            )

        if capacity <= 0:
            return APIResponse.error(message="Sức chứa phải lớn hơn 0", status_code=400)
        if price < 0:
            return APIResponse.error(message="Giá phòng không được âm", status_code=400)

        # Kiểm tra tên loại phòng đã tồn tại (trừ chính nó)
        existing_room_type = RoomType.query.filter(
            RoomType.type_name == data['type_name'],
            RoomType.room_type_id != room_type_id
        ).first()
        if existing_room_type:
            return APIResponse.error(
                message="Tên loại phòng đã tồn tại", status_code=400
            )

        # Cập nhật thông tin
        room_type.type_name = data['type_name']
        room_type.capacity = capacity
        room_type.price = price

        db.session.commit()

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Cập nhật loại phòng thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@rooms_bp.route('/room-types/<int:room_type_id>', methods=['DELETE', 'POST'])
# @jwt_required()
# @require_role(['admin'])
def delete_room_type(room_type_id):
    """Xóa loại phòng (chỉ Admin)"""
    print(f"[SERVER DEBUG] delete_room_type called with room_type_id: {room_type_id}")
    try:
        room_type = RoomType.query.get(room_type_id)
        print(f"[SERVER DEBUG] Found room_type: {room_type}")
        if not room_type:
            print(f"[SERVER DEBUG] Room type not found with id: {room_type_id}")
            return APIResponse.error(
                message="Loại phòng không tồn tại", status_code=404
            )

        # Kiểm tra loại phòng có đang được sử dụng không
        print(f"[SERVER DEBUG] Checking rooms using this room_type: {len(room_type.rooms) if room_type.rooms else 0}")
        if room_type.rooms:
            print(f"[SERVER DEBUG] Cannot delete - room_type has {len(room_type.rooms)} rooms")
            return APIResponse.error(
                message=f"Không thể xóa loại phòng này vì đang có {len(room_type.rooms)} phòng sử dụng.",
                status_code=400,
            )

        print(f"[SERVER DEBUG] Proceeding to delete room_type: {room_type.type_name}")
        db.session.delete(room_type)
        db.session.commit()
        print(f"[SERVER DEBUG] Successfully deleted room_type")

        return APIResponse.success(message="Xóa loại phòng thành công")

    except Exception as e:
        print(f"[SERVER DEBUG] Exception in delete_room_type: {str(e)}")
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

# Reading rooms blueprint
