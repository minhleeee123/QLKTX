from app.extensions import db
from app.models import RoomType
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

room_types_bp = Blueprint('room_types', __name__)

@room_types_bp.route('/', methods=['GET'])
@jwt_required()
def get_room_types():
    """
    Lấy danh sách loại phòng với phân trang và tìm kiếm

    Method: GET
    Query Parameters:
        page: int = 1              # Trang hiện tại (optional)
        per_page: int = 20         # Số loại phòng mỗi trang (optional)
        search: string             # Tìm kiếm theo tên loại phòng (optional)
        min_capacity: int          # Lọc theo sức chứa tối thiểu (optional)
        max_capacity: int          # Lọc theo sức chứa tối đa (optional)
        min_price: float           # Lọc theo giá tối thiểu (optional)
        max_price: float           # Lọc theo giá tối đa (optional)

    Example URL: GET /room-types?page=1&per_page=10&search=single&min_capacity=2

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách loại phòng thành công",
        "data": {
            "room_types": [
                {
                    "room_type_id": 1,
                    "type_name": "Phòng đơn",
                    "capacity": 2,
                    "price": 1000000.0,
                    "total_rooms": 10,
                    "available_rooms": 5,
                    "occupied_rooms": 5
                }
            ],
            "pagination": {
                "page": 1,
                "pages": 1,
                "per_page": 20,
                "total": 1,
                "has_next": false,
                "has_prev": false
            }
        }
    }

    Response JSON (Error - 500):
    {
        "success": false,
        "message": "Lỗi server nội bộ",
        "data": null
    }
    """
    try:
        # Lấy parameters từ query string
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()
        min_capacity = request.args.get('min_capacity', type=int)
        max_capacity = request.args.get('max_capacity', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # Tạo query cơ bản
        query = RoomType.query

        # Thêm điều kiện tìm kiếm theo tên
        if search:
            query = query.filter(RoomType.type_name.ilike(f'%{search}%'))

        # Thêm điều kiện lọc theo sức chứa
        if min_capacity is not None:
            query = query.filter(RoomType.capacity >= min_capacity)
        if max_capacity is not None:
            query = query.filter(RoomType.capacity <= max_capacity)

        # Thêm điều kiện lọc theo giá
        if min_price is not None:
            query = query.filter(RoomType.price >= min_price)
        if max_price is not None:
            query = query.filter(RoomType.price <= max_price)

        # Sắp xếp theo tên
        query = query.order_by(RoomType.type_name)

        # Phân trang
        room_types = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Chuẩn bị dữ liệu trả về
        room_types_data = {
            "room_types": [
                {
                    "room_type_id": rt.room_type_id,
                    "type_name": rt.type_name,
                    "capacity": rt.capacity,
                    "price": float(rt.price),
                    "total_rooms": rt.room_count,
                    "available_rooms": rt.available_rooms_count,
                    "occupied_rooms": rt.occupied_rooms_count,
                }
                for rt in room_types.items
            ],
            "pagination": {
                "page": room_types.page,
                "pages": room_types.pages,
                "per_page": room_types.per_page,
                "total": room_types.total,
                "has_next": room_types.has_next,
                "has_prev": room_types.has_prev,
            },
        }

        return APIResponse.success(
            data=room_types_data, message="Lấy danh sách loại phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@room_types_bp.route('/<int:room_type_id>', methods=['GET'])
@jwt_required()
def get_room_type(room_type_id):
    """
    Lấy thông tin chi tiết một loại phòng

    Method: GET
    URL Parameters:
        room_type_id: int          # ID của loại phòng cần lấy thông tin

    Example URL: GET /room-types/1

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy thông tin loại phòng thành công",
        "data": {
            "room_type": {
                "room_type_id": 1,
                "type_name": "Phòng đơn",
                "capacity": 2,
                "price": 1000000.0,
                "total_rooms": 10,
                "available_rooms": 5,
                "occupied_rooms": 5
            }
        }
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy loại phòng",
        "data": null
    }
    """
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return APIResponse.error(
                message="Không tìm thấy loại phòng", status_code=404
            )

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
                "total_rooms": room_type.room_count,
                "available_rooms": room_type.available_rooms_count,
                "occupied_rooms": room_type.occupied_rooms_count,
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Lấy thông tin loại phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@room_types_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['admin'])
def create_room_type():
    """
    Tạo loại phòng mới

    Method: POST
    Headers:
        Content-Type: application/json
        Authorization: Bearer <token>

    Request Body JSON:
    {
        "type_name": "Phòng VIP",
        "capacity": 4,
        "price": 2000000.0
    }

    Response JSON (Success - 201):
    {
        "success": true,
        "message": "Tạo loại phòng thành công",
        "data": {
            "room_type": {
                "room_type_id": 3,
                "type_name": "Phòng VIP",
                "capacity": 4,
                "price": 2000000.0,
                "total_rooms": 0
            }
        }
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Dữ liệu không hợp lệ",
        "data": null
    }

    Response JSON (Error - 409):
    {
        "success": false,
        "message": "Tên loại phòng đã tồn tại",
        "data": null
    }
    """
    try:
        data = request.get_json()

        # Kiểm tra dữ liệu đầu vào
        if not data:
            return APIResponse.error(
                message="Dữ liệu không hợp lệ", status_code=400
            )

        required_fields = ['type_name', 'capacity', 'price']
        for field in required_fields:
            if field not in data or data[field] is None:
                return APIResponse.error(
                    message=f"Thiếu trường bắt buộc: {field}", status_code=400
                )

        # Validate dữ liệu
        if not isinstance(data['type_name'], str) or not data['type_name'].strip():
            return APIResponse.error(
                message="Tên loại phòng không hợp lệ", status_code=400
            )

        if not isinstance(data['capacity'], int) or data['capacity'] <= 0:
            return APIResponse.error(
                message="Sức chứa phải là số nguyên dương", status_code=400
            )

        if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
            return APIResponse.error(
                message="Giá phải là số dương", status_code=400
            )

        # Kiểm tra tên loại phòng đã tồn tại
        existing_room_type = RoomType.query.filter_by(type_name=data['type_name'].strip()).first()
        if existing_room_type:
            return APIResponse.error(
                message="Tên loại phòng đã tồn tại", status_code=409
            )

        # Tạo loại phòng mới
        room_type = RoomType.create_room_type({
            'type_name': data['type_name'].strip(),
            'capacity': data['capacity'],
            'price': data['price']
        })

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
                "total_rooms": room_type.room_count,
                "available_rooms": room_type.available_rooms_count,
                "occupied_rooms": room_type.occupied_rooms_count,
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Tạo loại phòng thành công", status_code=201
        )

    except IntegrityError:
        db.session.rollback()
        return APIResponse.error(
            message="Tên loại phòng đã tồn tại", status_code=409
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@room_types_bp.route('/<int:room_type_id>', methods=['PUT'])
@jwt_required()
@require_role(['admin'])
def update_room_type(room_type_id):
    """
    Cập nhật thông tin loại phòng

    Method: PUT
    Headers:
        Content-Type: application/json
        Authorization: Bearer <token>

    URL Parameters:
        room_type_id: int          # ID của loại phòng cần cập nhật

    Request Body JSON:
    {
        "type_name": "Phòng VIP Plus",
        "capacity": 6,
        "price": 3000000.0
    }

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Cập nhật loại phòng thành công",
        "data": {
            "room_type": {
                "room_type_id": 1,
                "type_name": "Phòng VIP Plus",
                "capacity": 6,
                "price": 3000000.0,
                "total_rooms": 5,
                "available_rooms": 2,
                "occupied_rooms": 3
            }
        }
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy loại phòng",
        "data": null
    }

    Response JSON (Error - 409):
    {
        "success": false,
        "message": "Tên loại phòng đã tồn tại",
        "data": null
    }
    """
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return APIResponse.error(
                message="Không tìm thấy loại phòng", status_code=404
            )

        data = request.get_json()
        if not data:
            return APIResponse.error(
                message="Dữ liệu không hợp lệ", status_code=400
            )

        # Validate dữ liệu nếu có
        if 'type_name' in data:
            if not isinstance(data['type_name'], str) or not data['type_name'].strip():
                return APIResponse.error(
                    message="Tên loại phòng không hợp lệ", status_code=400
                )
            
            # Kiểm tra tên loại phòng đã tồn tại (trừ loại phòng hiện tại)
            existing_room_type = RoomType.query.filter(
                RoomType.type_name == data['type_name'].strip(),
                RoomType.room_type_id != room_type_id
            ).first()
            if existing_room_type:
                return APIResponse.error(
                    message="Tên loại phòng đã tồn tại", status_code=409
                )
            data['type_name'] = data['type_name'].strip()

        if 'capacity' in data:
            if not isinstance(data['capacity'], int) or data['capacity'] <= 0:
                return APIResponse.error(
                    message="Sức chứa phải là số nguyên dương", status_code=400
                )

        if 'price' in data:
            if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
                return APIResponse.error(
                    message="Giá phải là số dương", status_code=400
                )

        # Cập nhật loại phòng
        room_type.update_room_type(data)

        room_type_data = {
            "room_type": {
                "room_type_id": room_type.room_type_id,
                "type_name": room_type.type_name,
                "capacity": room_type.capacity,
                "price": float(room_type.price),
                "total_rooms": room_type.room_count,
                "available_rooms": room_type.available_rooms_count,
                "occupied_rooms": room_type.occupied_rooms_count,
            }
        }

        return APIResponse.success(
            data=room_type_data, message="Cập nhật loại phòng thành công"
        )

    except IntegrityError:
        db.session.rollback()
        return APIResponse.error(
            message="Tên loại phòng đã tồn tại", status_code=409
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@room_types_bp.route('/<int:room_type_id>', methods=['DELETE'])
@jwt_required()
@require_role(['admin'])
def delete_room_type(room_type_id):
    """
    Xóa loại phòng

    Method: DELETE
    Headers:
        Authorization: Bearer <token>

    URL Parameters:
        room_type_id: int          # ID của loại phòng cần xóa

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Xóa loại phòng thành công",
        "data": null
    }

    Response JSON (Error - 404):
    {
        "success": false,
        "message": "Không tìm thấy loại phòng",
        "data": null
    }

    Response JSON (Error - 400):
    {
        "success": false,
        "message": "Không thể xóa loại phòng này vì đang có phòng sử dụng",
        "data": null
    }
    """
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return APIResponse.error(
                message="Không tìm thấy loại phòng", status_code=404
            )

        # Kiểm tra xem có phòng nào đang sử dụng loại phòng này không
        if room_type.room_count > 0:
            return APIResponse.error(
                message="Không thể xóa loại phòng này vì đang có phòng sử dụng",
                status_code=400
            )

        # Xóa loại phòng
        room_type.delete_room_type()

        return APIResponse.success(
            message="Xóa loại phòng thành công", data=None
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@room_types_bp.route('/simple', methods=['GET'])
@jwt_required()
def get_room_types_simple():
    """
    Lấy danh sách loại phòng đơn giản (cho dropdown, select box)

    Method: GET

    Example URL: GET /room-types/simple

    Response JSON (Success - 200):
    {
        "success": true,
        "message": "Lấy danh sách loại phòng thành công",
        "data": {
            "room_types": [
                {
                    "room_type_id": 1,
                    "type_name": "Phòng đơn",
                    "capacity": 2,
                    "price": 1000000.0
                },
                {
                    "room_type_id": 2,
                    "type_name": "Phòng đôi",
                    "capacity": 4,
                    "price": 1500000.0
                }
            ]
        }
    }
    """
    try:
        room_types = RoomType.query.order_by(RoomType.type_name).all()

        room_types_data = {
            "room_types": [rt.to_dict_simple() for rt in room_types]
        }

        return APIResponse.success(
            data=room_types_data, message="Lấy danh sách loại phòng thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)
