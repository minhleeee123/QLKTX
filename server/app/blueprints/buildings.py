from app.extensions import db
from app.models import Building, Room
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

buildings_bp = Blueprint('buildings', __name__)


@buildings_bp.route('/', methods=['GET'])
@jwt_required()
def get_buildings():
    """
    Lấy danh sách tòa nhà với phân trang và tìm kiếm

    Method: GET
    Query Parameters:
        page: int = 1              # Trang hiện tại (optional)
        per_page: int = 20         # Số tòa nhà mỗi trang (optional)
        search: string             # Tìm kiếm theo tên tòa nhà (optional)

    Example URL: GET /buildings?page=1&per_page=20&search=Tòa A

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách tòa nhà thành công",
        "data": {
            "buildings": [
                {
                    "building_id": 1,
                    "building_name": "Tòa A",
                    "description": "Tòa nhà dành cho sinh viên năm nhất",
                    "total_rooms": 50,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 5,
                "pages": 1
            }
        }
    }

    Response JSON (Error - 400/500):
    {
        "success": false,
        "message": "Lỗi khi lấy danh sách tòa nhà"
    }
    """
    try:
        # Lấy query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Giới hạn tối đa 100
        search = request.args.get('search', '').strip()

        # Tạo query cơ bản
        query = Building.query

        # Áp dụng tìm kiếm nếu có
        if search:
            query = query.filter(Building.building_name.ilike(f'%{search}%'))

        # Phân trang
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Chuyển đổi dữ liệu
        buildings = [building.to_dict() for building in pagination.items]

        return APIResponse.success(
            data={
                'buildings': buildings,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            },
            message="Lấy danh sách tòa nhà thành công"
        )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy danh sách tòa nhà: {str(e)}")


@buildings_bp.route('/<int:building_id>', methods=['GET'])
@jwt_required()
def get_building(building_id):
    """
    Lấy thông tin chi tiết một tòa nhà

    Method: GET
    Path Parameters:
        building_id: int           # ID của tòa nhà

    Example URL: GET /buildings/1

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy thông tin tòa nhà thành công",
        "data": {
            "building_id": 1,
            "building_name": "Tòa A",
            "description": "Tòa nhà dành cho sinh viên năm nhất",
            "total_rooms": 50,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy tòa nhà"
    }
    """
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error("Không tìm thấy tòa nhà", 404)

        return APIResponse.success(
            data={"building": building.to_dict()},
            message="Lấy thông tin tòa nhà thành công"
        )

    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy thông tin tòa nhà: {str(e)}")


@buildings_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['admin'])
def create_building():
    """
    Tạo tòa nhà mới

    Method: POST
    Request Body JSON:
    {
        "building_name": "Tòa A",
        "description": "Tòa nhà dành cho sinh viên năm nhất"
    }

    Response JSON (Success - 201):
    {
        "success": true,
        "message": "Tạo tòa nhà thành công",
        "data": {
            "building_id": 1,
            "building_name": "Tòa A",
            "description": "Tòa nhà dành cho sinh viên năm nhất",
            "total_rooms": 0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Tên tòa nhà là bắt buộc"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return APIResponse.error("Dữ liệu không hợp lệ", 400)
        
        building_name = data.get('building_name', '').strip()
        if not building_name:
            return APIResponse.error("Tên tòa nhà là bắt buộc", 400)
        
        # Kiểm tra tên tòa nhà đã tồn tại
        existing_building = Building.query.filter_by(building_name=building_name).first()
        if existing_building:
            return APIResponse.error("Tên tòa nhà đã tồn tại", 400)
        
        # Tạo tòa nhà mới
        building = Building.create_building(data)
        
        return APIResponse.success(
            data={"building": building.to_dict()},
            message="Tạo tòa nhà thành công",
            status_code=201
        )
        
    except IntegrityError:
        db.session.rollback()
        return APIResponse.error("Tên tòa nhà đã tồn tại", 400)
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"Lỗi khi tạo tòa nhà: {str(e)}")


@buildings_bp.route('/<int:building_id>', methods=['PUT'])
@jwt_required()
@require_role(['admin'])
def update_building(building_id):
    """
    Cập nhật thông tin tòa nhà

    Method: PUT
    Path Parameters:
        building_id: int           # ID của tòa nhà
    Request Body JSON:
    {
        "building_name": "Tòa A (Updated)",
        "description": "Mô tả mới"
    }

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Cập nhật tòa nhà thành công",
        "data": {
            "building_id": 1,
            "building_name": "Tòa A (Updated)",
            "description": "Mô tả mới",
            "total_rooms": 50,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T12:00:00"
        }
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy tòa nhà"
    }
    """
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error("Không tìm thấy tòa nhà", 404)
        
        data = request.get_json()
        if not data:
            return APIResponse.error("Dữ liệu không hợp lệ", 400)
        
        # Validation
        building_name = data.get('building_name', '').strip()
        if building_name and building_name != building.building_name:
            # Kiểm tra tên tòa nhà đã tồn tại
            existing_building = Building.query.filter_by(building_name=building_name).first()
            if existing_building:
                return APIResponse.error("Tên tòa nhà đã tồn tại", 400)
        
        # Cập nhật thông tin
        building.update_building(data)
        
        return APIResponse.success(
            data={"building": building.to_dict()},
            message="Cập nhật tòa nhà thành công"
        )
        
    except IntegrityError:
        db.session.rollback()
        return APIResponse.error("Tên tòa nhà đã tồn tại", 400)
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"Lỗi khi cập nhật tòa nhà: {str(e)}")


@buildings_bp.route('/<int:building_id>', methods=['DELETE'])
@jwt_required()
@require_role(['admin'])
def delete_building(building_id):
    """
    Xóa tòa nhà

    Method: DELETE
    Path Parameters:
        building_id: int           # ID của tòa nhà

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Xóa tòa nhà thành công"
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy tòa nhà"
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Không thể xóa tòa nhà vì vẫn còn phòng"
    }
    """
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error("Không tìm thấy tòa nhà", 404)
        
        # Kiểm tra xem tòa nhà có còn phòng không
        if building.rooms:
            return APIResponse.error("Không thể xóa tòa nhà vì vẫn còn phòng", 400)
        
        # Xóa tòa nhà
        building.delete_building()
        
        return APIResponse.success(message="Xóa tòa nhà thành công")
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"Lỗi khi xóa tòa nhà: {str(e)}")


@buildings_bp.route('/dropdown', methods=['GET'])
@jwt_required()
def get_buildings_dropdown():
    """
    Lấy danh sách tòa nhà cho dropdown (chỉ ID và tên)

    Method: GET

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách tòa nhà thành công",
        "data": {
            "buildings": [
                {
                    "building_id": 1,
                    "building_name": "Tòa A"
                },
                {
                    "building_id": 2,
                    "building_name": "Tòa B"
                }
            ]
        }
    }
    """
    try:
        buildings = Building.query.order_by(Building.building_name).all()
        buildings_data = [building.to_dict_simple() for building in buildings]
        
        return APIResponse.success(
            data={'buildings': buildings_data},
            message="Lấy danh sách tòa nhà thành công"
        )
        
    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy danh sách tòa nhà: {str(e)}")


@buildings_bp.route('/<int:building_id>/rooms', methods=['GET'])
@jwt_required()
def get_building_rooms(building_id):
    """
    Lấy danh sách phòng của một tòa nhà

    Method: GET
    Path Parameters:
        building_id: int           # ID của tòa nhà
    Query Parameters:
        status: string             # Lọc theo trạng thái phòng (optional)

    Example URL: GET /buildings/1/rooms?status=available

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách phòng thành công",
        "data": {
            "building": {
                "building_id": 1,
                "building_name": "Tòa A"
            },
            "rooms": [
                {
                    "room_id": 1,
                    "room_number": "101",
                    "status": "available",
                    "room_type": {
                        "room_type_id": 1,
                        "type_name": "Phòng đơn",
                        "capacity": 2
                    }
                }
            ]
        }
    }
    """
    try:
        building = Building.query.get(building_id)
        if not building:
            return APIResponse.error("Không tìm thấy tòa nhà", 404)
        
        # Lấy rooms của building
        rooms_query = Room.query.filter_by(building_id=building_id)
        
        # Lọc theo status nếu có
        status = request.args.get('status')
        if status:
            rooms_query = rooms_query.filter_by(status=status)
        
        rooms = rooms_query.order_by(Room.room_number).all()
        
        # Convert to dict (assuming Room model has to_dict method)
        rooms_data = []
        for room in rooms:
            room_data = {
                'room_id': room.room_id,
                'room_number': room.room_number,
                'status': room.status,
                'current_occupancy': room.current_occupancy,
                'room_type': {
                    'room_type_id': room.room_type.room_type_id,
                    'type_name': room.room_type.type_name,
                    'capacity': room.room_type.capacity,
                    'price': float(room.room_type.price)
                } if room.room_type else None
            }
            rooms_data.append(room_data)
        
        return APIResponse.success(
            data={
                'building': building.to_dict_simple(),
                'rooms': rooms_data
            },
            message="Lấy danh sách phòng thành công"
        )
        
    except Exception as e:
        return APIResponse.error(f"Lỗi khi lấy danh sách phòng: {str(e)}")
