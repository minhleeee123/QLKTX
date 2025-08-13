from datetime import date, datetime

from app.extensions import db
from app.models import Contract, Payment, Registration, Room, User
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

registrations_bp = Blueprint('registrations', __name__)

@registrations_bp.route('/', methods=['GET'])
@jwt_required()
def get_registrations():
    """Lấy danh sách đơn đăng ký"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        # Student chỉ xem được đơn của mình
        if current_user.role.role_name == 'student':
            query = Registration.query.filter_by(student_id=current_user_id)
        else:
            # Admin/Management xem tất cả
            query = Registration.query

        if status:
            query = query.filter_by(status=status)

        registrations = query.order_by(Registration.registration_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        registrations_data = {
            "registrations": [
                {
                    "registration_id": reg.registration_id,
                    "student": {
                        "user_id": reg.student.user_id,
                        "full_name": reg.student.full_name,
                        "student_id": reg.student.student_id,
                        "email": reg.student.email,
                    },
                    "room": {
                        "room_id": reg.room.room_id,
                        "room_number": reg.room.room_number,
                        "building_name": reg.room.building.building_name,
                        "room_type": reg.room.room_type.type_name,
                        "price": float(reg.room.room_type.price),
                    },
                    "status": reg.status,
                    "registration_date": reg.registration_date.isoformat(),
                    "has_contract": reg.contract is not None,
                }
                for reg in registrations.items
            ],
            "pagination": {
                "page": registrations.page,
                "pages": registrations.pages,
                "per_page": registrations.per_page,
                "total": registrations.total,
                "has_next": registrations.has_next,
                "has_prev": registrations.has_prev,
            },
        }

        return APIResponse.success(
            data=registrations_data, message="Lấy danh sách đăng ký thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)

@registrations_bp.route('/', methods=['POST'])
@jwt_required()
def create_registration():
    """Tạo đơn đăng ký mới (sinh viên)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Chỉ sinh viên mới được đăng ký
        if current_user.role.role_name != 'student':
            return APIResponse.error(
                message="Chỉ sinh viên mới được đăng ký phòng", status_code=403
            )

        data = request.get_json()
        room_id = data.get('room_id')

        if not room_id:
            return APIResponse.error(message="room_id là bắt buộc", status_code=400)

        # Kiểm tra phòng tồn tại
        room = Room.query.get(room_id)
        if not room:
            return APIResponse.error(message="Phòng không tồn tại", status_code=404)

        # Kiểm tra phòng còn chỗ trống
        if not room.is_available:
            return APIResponse.error(
                message="Phòng đã đầy hoặc không khả dụng", status_code=400
            )

        # Kiểm tra giới tính của sinh viên và tòa nhà
        building_gender = room.building.gender
        student_gender = current_user.gender
        if building_gender != "all" and building_gender != student_gender:
            return APIResponse.error(
                message=f"Bạn chỉ được đăng ký phòng ở tòa nhà dành cho giới tính '{student_gender}'",
                status_code=400,
            )

        # Kiểm tra sinh viên đã có đơn đăng ký pending/approved chưa
        existing_registration = (
            Registration.query.filter_by(student_id=current_user_id)
            .filter(Registration.status.in_(["pending", "approved"]))
            .first()
        )
        if existing_registration:
            return APIResponse.error(
                message="Bạn đã có đơn đăng ký đang chờ xử lý hoặc đã được duyệt",
                status_code=400,
            )

        # Tạo đơn đăng ký mới
        registration = Registration(
            student_id=current_user_id,
            room_id=room_id,
            status='pending',
            registration_date=datetime.utcnow()
        )

        db.session.add(registration)
        db.session.commit()

        registration_data = {
            "registration": {
                "registration_id": registration.registration_id,
                "room_number": registration.room.room_number,
                "building_name": registration.room.building.building_name,
                "status": registration.status,
                "registration_date": registration.registration_date.isoformat(),
            }
        }

        return APIResponse.success(
            data=registration_data, message="Đăng ký phòng thành công", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)


@registrations_bp.route("/<int:registration_id>/json", methods=["GET"])
@jwt_required()
def get_registration_json(registration_id):
    """Trả về thông tin đăng ký dưới dạng JSON cho modal"""
    try:
        registration = Registration.query.get(registration_id)
        if not registration:
            return jsonify({"success": False, "message": "Đăng ký không tồn tại"}), 404

        reg_data = {
            "registration_id": registration.registration_id,
            "registration_date": registration.registration_date.isoformat(),
            "status": registration.status,
            "student": {
                "full_name": registration.student.full_name,
                "student_id": registration.student.student_id,
                "email": registration.student.email,
            },
            "room": {
                "room_number": registration.room.room_number,
                "building_name": registration.room.building.building_name,
                "room_type": registration.room.room_type.type_name,
                "price": float(registration.room.room_type.price),
            },
        }
        return jsonify({"success": True, "registration": reg_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@registrations_bp.route('/<int:registration_id>/approve', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def approve_registration(registration_id):
    """Duyệt đơn đăng ký"""
    try:
        registration = Registration.query.get(registration_id)
        if not registration:
            return APIResponse.error(
                message="Đơn đăng ký không tồn tại", status_code=404
            )

        if registration.status != 'pending':
            return APIResponse.error(
                message="Chỉ có thể duyệt đơn đang chờ xử lý", status_code=400
            )

        # Kiểm tra phòng còn chỗ trống
        room = registration.room
        if not room.is_available:
            return APIResponse.error(
                message="Phòng đã đầy, không thể duyệt đơn", status_code=400
            )

        # Cập nhật trạng thái đơn đăng ký
        registration.status = 'approved'

        # Cập nhật số người trong phòng
        room.current_occupancy += 1
        if room.current_occupancy >= room.room_type.capacity:
            room.status = 'occupied'

        # Tạo hợp đồng tự động
        contract_code = f"HD{registration.registration_id:04d}"
        start_date = date.today()
        end_date = date(start_date.year + 1, start_date.month, start_date.day)  # 1 năm

        contract = Contract(
            registration_id=registration.registration_id,
            contract_code=contract_code,
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(contract)
        db.session.flush()  # To get the contract ID

        # Tạo khoản thanh toán đầu tiên (pending) cho tháng đầu
        room_price = registration.room.room_type.price
        initial_payment = Payment(
            contract_id=contract.contract_id,
            amount=room_price,
            payment_method="bank_transfer",  # Mặc định
            status="pending",  # Chờ sinh viên thanh toán
        )

        db.session.add(initial_payment)

        db.session.commit()

        registration_data = {
            "registration": {
                "registration_id": registration.registration_id,
                "status": registration.status,
                "contract_code": contract.contract_code,
            }
        }

        return APIResponse.success(
            data=registration_data, message="Duyệt đơn đăng ký thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@registrations_bp.route('/<int:registration_id>/reject', methods=['POST'])
@jwt_required()
@require_role(['admin', 'management'])
def reject_registration(registration_id):
    """Từ chối đơn đăng ký"""
    try:
        registration = Registration.query.get(registration_id)
        if not registration:
            return APIResponse.error(
                message="Đơn đăng ký không tồn tại", status_code=404
            )

        if registration.status != 'pending':
            return APIResponse.error(
                message="Chỉ có thể từ chối đơn đang chờ xử lý", status_code=400
            )

        registration.status = 'rejected'
        db.session.commit()

        registration_data = {
            "registration": {
                "registration_id": registration.registration_id,
                "status": registration.status,
            }
        }

        return APIResponse.success(
            data=registration_data, message="Từ chối đơn đăng ký thành công"
        )

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)

@registrations_bp.route('/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    """Hủy đơn đăng ký (sinh viên chỉ hủy được đơn pending của mình)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        registration = Registration.query.get(registration_id)
        if not registration:
            return APIResponse.error(
                message="Đơn đăng ký không tồn tại", status_code=404
            )

        # Sinh viên chỉ hủy được đơn của mình
        if (current_user.role.role_name == 'student' and 
            registration.student_id != current_user_id):
            return APIResponse.error(
                message="Không có quyền hủy đơn này", status_code=403
            )

        # Chỉ có thể hủy đơn pending
        if registration.status != 'pending':
            return APIResponse.error(
                message="Chỉ có thể hủy đơn đang chờ xử lý", status_code=400
            )

        db.session.delete(registration)
        db.session.commit()

        return APIResponse.success(message="Hủy đơn đăng ký thành công")

    except Exception as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), status_code=500)
        return APIResponse.error(message=str(e), status_code=500)
