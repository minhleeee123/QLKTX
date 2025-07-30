from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, MaintenanceRequest, Room
from datetime import datetime
from app.utils.decorators import require_role
from app.utils.api_response import APIResponse

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/', methods=['GET'])
@jwt_required()
def get_maintenance_requests():
    """Lấy danh sách yêu cầu bảo trì"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        # Student chỉ xem được yêu cầu của mình
        if current_user.role.role_name == 'student':
            query = MaintenanceRequest.query.filter_by(student_id=current_user_id)
        elif current_user.role.role_name == "staff":
            # Maintenance staff xem yêu cầu được giao cho mình
            query = MaintenanceRequest.query.filter(
                db.or_(
                    MaintenanceRequest.assigned_to_user_id == current_user_id,
                    MaintenanceRequest.status == 'pending'
                )
            )
        else:
            # Admin/Management xem tất cả
            query = MaintenanceRequest.query

        if status:
            query = query.filter_by(status=status)

        requests = query.order_by(MaintenanceRequest.request_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        requests_data = {
            "maintenance_requests": [
                {
                    "request_id": req.request_id,
                    "student": {
                        "user_id": req.student.user_id,
                        "full_name": req.student.full_name,
                        "student_id": req.student.student_id,
                        "email": req.student.email,
                    },
                    "room": {
                        "room_id": req.room.room_id,
                        "room_number": req.room.room_number,
                        "building_name": req.room.building.building_name,
                    },
                    "title": req.title,
                    "description": req.description,
                    "image_url": req.image_url,
                    "status": req.status,
                    "status_display": req.status_display,
                    "request_date": req.request_date.isoformat(),
                    "days_since_request": req.days_since_request,
                    "is_urgent": req.is_urgent,
                    "assigned_to": (
                        {
                            "user_id": req.assigned_to.user_id,
                            "full_name": req.assigned_to.full_name,
                        }
                        if req.assigned_to
                        else None
                    ),
                    "completed_date": (
                        req.completed_date.isoformat() if req.completed_date else None
                    ),
                }
                for req in requests.items
            ],
            "pagination": {
                "page": requests.page,
                "pages": requests.pages,
                "per_page": requests.per_page,
                "total": requests.total,
                "has_next": requests.has_next,
                "has_prev": requests.has_prev,
            },
        }

        return APIResponse.success(
            data=requests_data, message="Lấy danh sách yêu cầu bảo trì thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@maintenance_bp.route('/', methods=['POST'])
@jwt_required()
def create_maintenance_request():
    """Tạo yêu cầu bảo trì mới (sinh viên)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Chỉ sinh viên mới được tạo yêu cầu bảo trì
        if current_user.role.role_name != 'student':
            return APIResponse.error(
                message="Chỉ sinh viên mới được tạo yêu cầu bảo trì", status_code=403
            )

        data = request.get_json()

        # Validate required fields
        required_fields = ['room_id', 'title']
        for field in required_fields:
            if not data.get(field):
                return APIResponse.error(
                    message=f"{field} là bắt buộc", status_code=400
                )

        # Kiểm tra phòng tồn tại
        room = Room.query.get(data['room_id'])
        if not room:
            return APIResponse.error(message="Phòng không tồn tại", status_code=404)

        # Tạo yêu cầu bảo trì mới
        maintenance_request = MaintenanceRequest(
            student_id=current_user_id,
            room_id=data['room_id'],
            title=data['title'],
            description=data.get('description'),
            image_url=data.get('image_url'),
            status='pending'
        )

        db.session.add(maintenance_request)
        db.session.commit()

        request_data = {
            "maintenance_request": {
                "request_id": maintenance_request.request_id,
                "title": maintenance_request.title,
                "room_number": maintenance_request.room.room_number,
                "status": maintenance_request.status,
                "request_date": maintenance_request.request_date.isoformat(),
            }
        }

        return APIResponse.success(
            data=request_data, message="Tạo yêu cầu bảo trì thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@maintenance_bp.route('/<int:request_id>/assign', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def assign_maintenance_request(request_id):
    """Phân công yêu cầu bảo trì cho nhân viên"""
    try:
        maintenance_request = MaintenanceRequest.query.get(request_id)
        if not maintenance_request:
            return jsonify('Yêu cầu bảo trì không tồn tại'), 404

        if maintenance_request.status not in ['pending', 'assigned']:
            return jsonify('Chỉ có thể phân công yêu cầu đang chờ xử lý'), 400

        data = request.get_json()
        assigned_to_user_id = data.get('assigned_to_user_id')

        if not assigned_to_user_id:
            return jsonify('assigned_to_user_id là bắt buộc'), 400

        # Kiểm tra user tồn tại và là maintenance staff
        assigned_user = User.query.get(assigned_to_user_id)
        if not assigned_user or assigned_user.role.role_name != "staff":
            return jsonify('Nhân viên bảo trì không tồn tại'), 404

        maintenance_request.assigned_to_user_id = assigned_to_user_id
        maintenance_request.status = 'assigned'

        db.session.commit()

        return jsonify({
            'message': 'Phân công yêu cầu bảo trì thành công',
            'maintenance_request': {
                'request_id': maintenance_request.request_id,
                'status': maintenance_request.status,
                'assigned_to': assigned_user.full_name
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@maintenance_bp.route("/<int:request_id>/start", methods=["POST"])
@jwt_required()
@require_role(["staff"])
def start_maintenance(request_id):
    """Bắt đầu xử lý yêu cầu bảo trì"""
    try:
        current_user_id = get_jwt_identity()

        maintenance_request = MaintenanceRequest.query.get(request_id)
        if not maintenance_request:
            return jsonify('Yêu cầu bảo trì không tồn tại'), 404

        # Chỉ nhân viên được phân công mới được bắt đầu
        if maintenance_request.assigned_to_user_id != current_user_id:
            return jsonify('Bạn không được phân công xử lý yêu cầu này'), 403

        if maintenance_request.status != 'assigned':
            return jsonify('Chỉ có thể bắt đầu yêu cầu đã được phân công'), 400

        maintenance_request.status = 'in_progress'

        db.session.commit()

        return jsonify({
            'message': 'Bắt đầu xử lý yêu cầu bảo trì',
            'maintenance_request': {
                'request_id': maintenance_request.request_id,
                'status': maintenance_request.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500


@maintenance_bp.route("/<int:request_id>/complete", methods=["POST"])
@jwt_required()
@require_role(["staff"])
def complete_maintenance(request_id):
    """Hoàn thành yêu cầu bảo trì"""
    try:
        current_user_id = get_jwt_identity()
        
        maintenance_request = MaintenanceRequest.query.get(request_id)
        if not maintenance_request:
            return jsonify('Yêu cầu bảo trì không tồn tại'), 404
        
        # Chỉ nhân viên được phân công mới được hoàn thành
        if maintenance_request.assigned_to_user_id != current_user_id:
            return jsonify('Bạn không được phân công xử lý yêu cầu này'), 403
        
        if maintenance_request.status != 'in_progress':
            return jsonify('Chỉ có thể hoàn thành yêu cầu đang được xử lý'), 400
        
        maintenance_request.status = 'completed'
        maintenance_request.completed_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Hoàn thành yêu cầu bảo trì',
            'maintenance_request': {
                'request_id': maintenance_request.request_id,
                'status': maintenance_request.status,
                'completed_date': maintenance_request.completed_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@maintenance_bp.route('/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_maintenance_request(request_id):
    """Hủy yêu cầu bảo trì"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        maintenance_request = MaintenanceRequest.query.get(request_id)
        if not maintenance_request:
            return jsonify('Yêu cầu bảo trì không tồn tại'), 404
        
        # Student chỉ hủy được yêu cầu của mình và phải ở trạng thái pending
        if current_user.role.role_name == 'student':
            if (maintenance_request.student_id != current_user_id or 
                maintenance_request.status != 'pending'):
                return jsonify('Chỉ có thể hủy yêu cầu đang chờ xử lý của mình'), 403
        
        # Admin/Management có thể hủy bất kỳ yêu cầu nào chưa hoàn thành
        elif current_user.role.role_name in ['admin', 'management']:
            if maintenance_request.status == 'completed':
                return jsonify('Không thể hủy yêu cầu đã hoàn thành'), 400
        else:
            return jsonify('Không có quyền hủy yêu cầu này'), 403
        
        maintenance_request.status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Hủy yêu cầu bảo trì thành công',
            'maintenance_request': {
                'request_id': maintenance_request.request_id,
                'status': maintenance_request.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 500

@maintenance_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_maintenance_statistics():
    """Thống kê yêu cầu bảo trì"""
    try:
        total_requests = MaintenanceRequest.query.count()
        pending_requests = MaintenanceRequest.query.filter_by(status='pending').count()
        assigned_requests = MaintenanceRequest.query.filter_by(status='assigned').count()
        in_progress_requests = MaintenanceRequest.query.filter_by(status='in_progress').count()
        completed_requests = MaintenanceRequest.query.filter_by(status='completed').count()
        cancelled_requests = MaintenanceRequest.query.filter_by(status='cancelled').count()
        
        # Yêu cầu khẩn cấp (pending > 3 ngày)
        urgent_requests = MaintenanceRequest.query.filter(
            MaintenanceRequest.status == 'pending',
            db.func.datediff(db.func.now(), MaintenanceRequest.request_date) > 3
        ).count()
        
        return jsonify({
            'statistics': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'assigned_requests': assigned_requests,
                'in_progress_requests': in_progress_requests,
                'completed_requests': completed_requests,
                'cancelled_requests': cancelled_requests,
                'urgent_requests': urgent_requests
            }
        }), 200
        
    except Exception as e:
        return jsonify(str(e)), 500
