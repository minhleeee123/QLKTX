from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Room, Building, RoomType
from app.utils.decorators import require_role

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/', methods=['GET'])
# @jwt_required()
def get_rooms():
    """Lấy danh sách phòng"""
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
        
        return jsonify({
            'rooms': [{
                'room_id': room.room_id,
                'room_number': room.room_number,
                'building': {
                    'building_id': room.building.building_id,
                    'building_name': room.building.building_name
                },
                'room_type': {
                    'room_type_id': room.room_type.room_type_id,
                    'type_name': room.room_type.type_name,
                    'capacity': room.room_type.capacity,
                    'price': float(room.room_type.price)
                },
                'status': room.status,
                'current_occupancy': room.current_occupancy,
                'available_slots': room.remaining_capacity,
                'is_available': room.is_available
            } for room in rooms.items],
            'pagination': {
                'page': rooms.page,
                'pages': rooms.pages,
                'per_page': rooms.per_page,
                'total': rooms.total,
                'has_next': rooms.has_next,
                'has_prev': rooms.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@rooms_bp.route('/<int:room_id>', methods=['GET'])
# @jwt_required()
def get_room(room_id):
    """Lấy thông tin chi tiết một phòng"""
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify('Phòng không tồn tại'), 404
        
        return jsonify({
            'room': {
                'room_id': room.room_id,
                'room_number': room.room_number,
                'building': {
                    'building_id': room.building.building_id,
                    'building_name': room.building.building_name
                },
                'room_type': {
                    'room_type_id': room.room_type.room_type_id,
                    'type_name': room.room_type.type_name,
                    'capacity': room.room_type.capacity,
                    'price': float(room.room_type.price)
                },
                'status': room.status,
                'current_occupancy': room.current_occupancy,
                'available_slots': room.remaining_capacity,
                'is_available': room.is_available
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@rooms_bp.route('/', methods=['POST'])
# @jwt_required()
# @require_role(['admin', 'management'])
def create_room():
    """Tạo phòng mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['room_number', 'building_id', 'room_type_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Kiểm tra phòng đã tồn tại
        existing_room = Room.query.filter_by(
            room_number=data['room_number'],
            building_id=data['building_id']
        ).first()
        if existing_room:
            return jsonify('Phòng đã tồn tại trong tòa nhà này'), 400
        
        # Kiểm tra building và room_type tồn tại
        building = Building.query.get(data['building_id'])
        if not building:
            return jsonify('Tòa nhà không tồn tại'), 400
        
        room_type = RoomType.query.get(data['room_type_id'])
        if not room_type:
            return jsonify('Loại phòng không tồn tại'), 400
        
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
        
        return jsonify({
            'message': 'Tạo phòng thành công',
            'room': {
                'room_id': room.room_id,
                'room_number': room.room_number,
                'building_name': room.building.building_name,
                'room_type_name': room.room_type.type_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
# @jwt_required()
# @require_role(['admin', 'management'])
def update_room(room_id):
    """Cập nhật thông tin phòng"""
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify('Phòng không tồn tại'), 404
        
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
        
        return jsonify({
            'message': 'Cập nhật phòng thành công',
            'room': {
                'room_id': room.room_id,
                'room_number': room.room_number,
                'status': room.status,
                'current_occupancy': room.current_occupancy
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/buildings', methods=['GET'])
# @jwt_required()
def get_buildings():
    """Lấy danh sách tòa nhà"""
    try:
        buildings = Building.query.all()
        
        return jsonify({
            'buildings': [{
                'building_id': building.building_id,
                'building_name': building.building_name,
                'total_rooms': len(building.rooms),
                'available_rooms': len([r for r in building.rooms if r.status == 'available'])
            } for building in buildings]
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

@rooms_bp.route('/buildings', methods=['POST'])
# @jwt_required()
# @require_role(['admin', 'management'])
def create_building():
    """Tạo tòa nhà mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('building_name'):
            return jsonify('Tên tòa nhà là bắt buộc'), 400
        
        # Kiểm tra tòa nhà đã tồn tại
        existing_building = Building.query.filter_by(building_name=data['building_name']).first()
        if existing_building:
            return jsonify('Tòa nhà đã tồn tại'), 400
        
        # Tạo tòa nhà mới
        building = Building(building_name=data['building_name'])
        
        db.session.add(building)
        db.session.commit()
        
        return jsonify({
            'message': 'Tạo tòa nhà thành công',
            'building': {
                'building_id': building.building_id,
                'building_name': building.building_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/buildings/<int:building_id>', methods=['GET'])
# @jwt_required()
def get_building(building_id):
    """Lấy thông tin chi tiết một tòa nhà"""
    try:
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Tòa nhà không tồn tại'}), 404
        
        return jsonify({
            'building': {
                'building_id': building.building_id,
                'building_name': building.building_name,
                'total_rooms': len(building.rooms),
                'available_rooms': len([r for r in building.rooms if r.status == 'available'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rooms_bp.route('/buildings/<int:building_id>', methods=['PUT'])
# @jwt_required()
# @require_role(['admin', 'management'])
def update_building(building_id):
    """Cập nhật thông tin tòa nhà"""
    try:
        building = Building.query.get(building_id)
        if not building:
            return jsonify('Tòa nhà không tồn tại'), 404
        
        data = request.get_json()
        
        if not data.get('building_name'):
            return jsonify({'error': 'Tên tòa nhà là bắt buộc'}), 400
        
        # Kiểm tra tên tòa nhà đã tồn tại (trừ chính nó)
        existing_building = Building.query.filter(
            Building.building_name == data['building_name'],
            Building.building_id != building_id
        ).first()
        if existing_building:
            return jsonify({'error': 'Tên tòa nhà đã tồn tại'}), 400
        
        # Cập nhật thông tin
        building.building_name = data['building_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật tòa nhà thành công',
            'building': {
                'building_id': building.building_id,
                'building_name': building.building_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/buildings/<int:building_id>', methods=['DELETE', 'POST'])
# @jwt_required()
# @require_role(['admin'])
def delete_building(building_id):
    """Xóa tòa nhà (chỉ Admin)"""
    print(f"[SERVER DEBUG] delete_building called with building_id: {building_id}")
    try:
        building = Building.query.get(building_id)
        if not building:
            return jsonify({'error': 'Tòa nhà không tồn tại'}), 404
        
        # Kiểm tra tòa nhà có phòng không
        if building.rooms:
            return jsonify({
                'error': f'Không thể xóa tòa nhà này vì đang có {len(building.rooms)} phòng.',
                'room_count': len(building.rooms)
            }), 400
        
        db.session.delete(building)
        db.session.commit()
        
        return jsonify({'message': 'Xóa tòa nhà thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/room-types', methods=['GET'])
# @jwt_required()
def get_room_types():
    """Lấy danh sách loại phòng"""
    try:
        room_types = RoomType.query.all()
        
        return jsonify({
            'room_types': [{
                'room_type_id': rt.room_type_id,
                'type_name': rt.type_name,
                'capacity': rt.capacity,
                'price': float(rt.price),
                'total_rooms': len(rt.rooms),
                'available_rooms': len([r for r in rt.rooms if r.status == 'available'])
            } for rt in room_types]
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500

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
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Validate data types and values
        try:
            capacity = int(data['capacity'])
            price = float(data['price'])
        except ValueError:
            return jsonify('Sức chứa và giá phòng phải là số'), 400
        
        if capacity <= 0:
            return jsonify('Sức chứa phải lớn hơn 0'), 400
        if price < 0:
            return jsonify('Giá phòng không được âm'), 400
        
        # Kiểm tra loại phòng đã tồn tại
        existing_room_type = RoomType.query.filter_by(type_name=data['type_name']).first()
        if existing_room_type:
            return jsonify('Loại phòng đã tồn tại'), 400
        
        # Tạo loại phòng mới
        room_type = RoomType(
            type_name=data['type_name'],
            capacity=capacity,
            price=price
        )
        
        db.session.add(room_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Tạo loại phòng thành công',
            'room_type': {
                'room_type_id': room_type.room_type_id,
                'type_name': room_type.type_name,
                'capacity': room_type.capacity,
                'price': float(room_type.price)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@rooms_bp.route('/room-types/<int:room_type_id>', methods=['GET'])
# @jwt_required()
def get_room_type(room_type_id):
    """Lấy thông tin chi tiết một loại phòng"""
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return jsonify({'error': 'Loại phòng không tồn tại'}), 404
        
        return jsonify({
            'room_type': {
                'room_type_id': room_type.room_type_id,
                'type_name': room_type.type_name,
                'capacity': room_type.capacity,
                'price': float(room_type.price),
                'total_rooms': len(room_type.rooms),
                'available_rooms': len([r for r in room_type.rooms if r.status == 'available'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rooms_bp.route('/room-types/<int:room_type_id>', methods=['PUT'])
# @jwt_required()
# @require_role(['admin', 'management'])
def update_room_type(room_type_id):
    """Cập nhật thông tin loại phòng"""
    try:
        room_type = RoomType.query.get(room_type_id)
        if not room_type:
            return jsonify('Loại phòng không tồn tại'), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type_name', 'capacity', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify(f'{field} là bắt buộc'), 400
        
        # Validate data types and values
        try:
            capacity = int(data['capacity'])
            price = float(data['price'])
        except ValueError:
            return jsonify('Sức chứa và giá phòng phải là số'), 400
        
        if capacity <= 0:
            return jsonify('Sức chứa phải lớn hơn 0'), 400
        if price < 0:
            return jsonify('Giá phòng không được âm'), 400
        
        # Kiểm tra tên loại phòng đã tồn tại (trừ chính nó)
        existing_room_type = RoomType.query.filter(
            RoomType.type_name == data['type_name'],
            RoomType.room_type_id != room_type_id
        ).first()
        if existing_room_type:
            return jsonify('Tên loại phòng đã tồn tại'), 400
        
        # Cập nhật thông tin
        room_type.type_name = data['type_name']
        room_type.capacity = capacity
        room_type.price = price
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật loại phòng thành công',
            'room_type': {
                'room_type_id': room_type.room_type_id,
                'type_name': room_type.type_name,
                'capacity': room_type.capacity,
                'price': float(room_type.price)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

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
            return jsonify({'error': 'Loại phòng không tồn tại'}), 404

        # Kiểm tra loại phòng có đang được sử dụng không
        print(f"[SERVER DEBUG] Checking rooms using this room_type: {len(room_type.rooms) if room_type.rooms else 0}")
        if room_type.rooms:
            print(f"[SERVER DEBUG] Cannot delete - room_type has {len(room_type.rooms)} rooms")
            return jsonify({
                'error': f'Không thể xóa loại phòng này vì đang có {len(room_type.rooms)} phòng sử dụng.',
                'room_count': len(room_type.rooms)
            }), 400

        print(f"[SERVER DEBUG] Proceeding to delete room_type: {room_type.type_name}")
        db.session.delete(room_type)
        db.session.commit()
        print(f"[SERVER DEBUG] Successfully deleted room_type")

        return jsonify({'message': 'Xóa loại phòng thành công'}), 200

    except Exception as e:
        print(f"[SERVER DEBUG] Exception in delete_room_type: {str(e)}")
        db.session.rollback()
        return jsonify(str(e)), 500

# Reading rooms blueprint
