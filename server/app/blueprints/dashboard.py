from datetime import date, datetime, timedelta

from app.extensions import db
from app.models import (
    Contract,
    MaintenanceRequest,
    Payment,
    Registration,
    Role,
    Room,
    RoomType,
    User,
)
from app.utils.api_response import APIResponse
from app.utils.decorators import require_role
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/admin-stats', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_admin_dashboard_stats():
    """Get comprehensive dashboard statistics for admin"""
    try:
        # Room Statistics
        total_rooms = Room.query.count()
        occupied_rooms = Room.query.filter(Room.current_occupancy > 0).count()
        available_rooms = Room.query.filter_by(status='available').count()
        maintenance_rooms = Room.query.filter_by(status='maintenance').count()
        
        # Alternative occupancy calculation - count rooms with active contracts
        rooms_with_contracts = db.session.query(Room.room_id).join(
            Registration, Room.room_id == Registration.room_id
        ).join(
            Contract, Registration.registration_id == Contract.registration_id
        ).filter(
            Contract.start_date <= date.today(),
            Contract.end_date >= date.today()
        ).distinct().count()
        
        # Use the higher of the two occupancy counts
        occupied_rooms = max(occupied_rooms, rooms_with_contracts)
        
        # User Statistics
        total_students = User.query.join(Role).filter(Role.role_name == 'student').count()
        total_staff = User.query.join(Role).filter(Role.role_name == 'staff').count() 
        total_admins = User.query.join(Role).filter(Role.role_name == 'admin').count()
        
        # Contract Statistics
        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(
            Contract.start_date <= date.today(),
            Contract.end_date >= date.today()
        ).count()
        expired_contracts = Contract.query.filter(
            Contract.end_date < date.today()
        ).count()
        expiring_soon = Contract.query.filter(
            Contract.end_date <= date.today() + timedelta(days=30),
            Contract.end_date >= date.today()
        ).count()
        
        # Registration Statistics
        pending_registrations = Registration.query.filter_by(status='pending').count()
        approved_registrations = Registration.query.filter_by(status='approved').count()
        rejected_registrations = Registration.query.filter_by(status='rejected').count()
        
        # Payment Statistics
        total_revenue = db.session.query(
            db.func.sum(Payment.amount)
        ).filter(
            Payment.status == 'confirmed'
        ).scalar() or 0
        
        pending_payments = Payment.query.filter_by(status='pending').count()
        confirmed_payments = Payment.query.filter_by(status='confirmed').count()
        
        # Maintenance Statistics
        pending_maintenance = MaintenanceRequest.query.filter_by(status='pending').count()
        in_progress_maintenance = MaintenanceRequest.query.filter_by(status='in_progress').count()
        completed_maintenance = MaintenanceRequest.query.filter_by(status='completed').count()
        
        # Monthly revenue for the last 6 months
        monthly_revenue = []
        for i in range(6):
            start_date = (date.today().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            end_date = (start_date.replace(month=start_date.month+1) if start_date.month < 12 
                       else start_date.replace(year=start_date.year+1, month=1)) - timedelta(days=1)
            
            month_revenue = db.session.query(
                db.func.sum(Payment.amount)
            ).filter(
                Payment.status == 'confirmed',
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).scalar() or 0
            
            monthly_revenue.append({
                'month': start_date.strftime('%Y-%m'),
                'month_name': start_date.strftime('%m/%Y'),
                'revenue': float(month_revenue)
            })
        
        monthly_revenue.reverse()  # Show oldest to newest
        
        stats_data = {
            "room_stats": {
                "total_rooms": total_rooms,
                "occupied_rooms": occupied_rooms,
                "available_rooms": available_rooms,
                "maintenance_rooms": maintenance_rooms,
                "occupancy_rate": round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 1)
            },
            "user_stats": {
                "total_students": total_students,
                "total_staff": total_staff,
                "total_admins": total_admins,
                "total_users": total_students + total_staff + total_admins
            },
            "contract_stats": {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "expired_contracts": expired_contracts,
                "expiring_soon": expiring_soon
            },
            "registration_stats": {
                "pending_registrations": pending_registrations,
                "approved_registrations": approved_registrations,
                "rejected_registrations": rejected_registrations,
                "total_registrations": pending_registrations + approved_registrations + rejected_registrations
            },
            "payment_stats": {
                "total_revenue": float(total_revenue),
                "pending_payments": pending_payments,
                "confirmed_payments": confirmed_payments,
                "monthly_revenue": monthly_revenue
            },
            "maintenance_stats": {
                "pending_maintenance": pending_maintenance,
                "in_progress_maintenance": in_progress_maintenance,
                "completed_maintenance": completed_maintenance,
                "total_maintenance": pending_maintenance + in_progress_maintenance + completed_maintenance
            }
        }

        return APIResponse.success(
            data={"stats": stats_data}, 
            message="Lấy thống kê dashboard thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@dashboard_bp.route('/recent-activities', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_recent_activities():
    """Get recent activities for dashboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        activities = []
        
        # Recent Registrations
        recent_registrations = Registration.query.order_by(
            Registration.registration_date.desc()
        ).limit(5).all()
        
        for reg in recent_registrations:
            if reg.student and reg.room:
                activities.append({
                    'type': 'registration',
                    'icon': 'fas fa-user-plus',
                    'color': 'success' if reg.status == 'approved' else ('warning' if reg.status == 'pending' else 'danger'),
                    'message': f"Sinh viên {reg.student.full_name} đã đăng ký phòng {reg.room.room_number}",
                    'status': reg.status,
                    'timestamp': reg.registration_date,
                    'relative_time': get_relative_time(reg.registration_date)
                })
        
        # Recent Payments
        recent_payments = Payment.query.order_by(
            Payment.payment_date.desc()
        ).limit(5).all()
        
        for payment in recent_payments:
            if payment.contract:
                activities.append({
                    'type': 'payment',
                    'icon': 'fas fa-credit-card',
                    'color': 'primary' if payment.status == 'confirmed' else ('warning' if payment.status == 'pending' else 'danger'),
                    'message': f"Thanh toán {'{:,.0f}'.format(payment.amount)}đ cho hợp đồng {payment.contract.contract_code}",
                    'status': payment.status,
                    'timestamp': payment.payment_date,
                    'relative_time': get_relative_time(payment.payment_date)
                })
        
        # Recent Maintenance Requests
        recent_maintenance = MaintenanceRequest.query.order_by(
            MaintenanceRequest.request_date.desc()
        ).limit(3).all()
        
        for maintenance in recent_maintenance:
            activities.append({
                'type': 'maintenance',
                'icon': 'fas fa-tools',
                'color': 'warning' if maintenance.status == 'pending' else ('info' if maintenance.status == 'in_progress' else 'success'),
                'message': f"Yêu cầu bảo trì: {maintenance.issue_description[:50]}{'...' if len(maintenance.issue_description) > 50 else ''}",
                'status': maintenance.status,
                'timestamp': maintenance.request_date,
                'relative_time': get_relative_time(maintenance.request_date)
            })
        
        # Recent Contracts
        recent_contracts = Contract.query.order_by(
            Contract.start_date.desc()
        ).limit(3).all()
        
        for contract in recent_contracts:
            if contract.registration and contract.registration.student and contract.registration.room:
                activities.append({
                    'type': 'contract',
                    'icon': 'fas fa-file-contract',
                    'color': 'success' if contract.is_active else 'secondary',
                    'message': f"Hợp đồng {contract.contract_code} - {contract.registration.student.full_name} - Phòng {contract.registration.room.room_number}",
                    'status': 'active' if contract.is_active else 'inactive',
                    'timestamp': contract.start_date,
                    'relative_time': get_relative_time(contract.start_date)
                })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        activities = activities[:limit]

        return APIResponse.success(
            data={"activities": activities}, 
            message="Lấy hoạt động gần đây thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
@require_role(['admin', 'management'])
def get_dashboard_alerts():
    """Get important alerts for dashboard"""
    try:
        alerts = []
        
        # Pending maintenance requests
        pending_maintenance = MaintenanceRequest.query.filter_by(status='pending').count()
        if pending_maintenance > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fas fa-tools',
                'title': 'Yêu cầu bảo trì chờ xử lý',
                'count': pending_maintenance,
                'message': f"{pending_maintenance} yêu cầu bảo trì đang chờ xử lý",
                'action_url': '/maintenance'
            })
        
        # Contracts expiring soon
        expiring_contracts = Contract.query.filter(
            Contract.end_date <= date.today() + timedelta(days=30),
            Contract.end_date >= date.today()
        ).count()
        if expiring_contracts > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fas fa-calendar-alt',
                'title': 'Hợp đồng sắp hết hạn',
                'count': expiring_contracts,
                'message': f"{expiring_contracts} hợp đồng sẽ hết hạn trong 30 ngày tới",
                'action_url': '/contracts/expiring-soon'
            })
        
        # Overdue payments
        # Overdue payments (payments pending for more than 7 days)
        overdue_date = date.today() - timedelta(days=7)
        overdue_payments = Payment.query.filter(
            Payment.status == 'pending',
            Payment.payment_date <= overdue_date
        ).count()
        
        if overdue_payments > 0:
            alerts.append({
                'type': 'danger',
                'icon': 'fas fa-exclamation-circle',
                'title': 'Thanh toán quá hạn',
                'count': overdue_payments,
                'message': f"{overdue_payments} thanh toán đã quá hạn hơn 7 ngày",
                'action_url': '/payments?status=overdue'
            })
        
        # Pending registrations
        pending_registrations = Registration.query.filter_by(status='pending').count()
        if pending_registrations > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fas fa-clipboard-list',
                'title': 'Đơn đăng ký chờ duyệt',
                'count': pending_registrations,
                'message': f"{pending_registrations} đơn đăng ký đang chờ duyệt",
                'action_url': '/registrations?status=pending'
            })
        
        # Rooms at full capacity or over capacity
        overcrowded_rooms = db.session.query(Room).join(
            RoomType, Room.room_type_id == RoomType.room_type_id
        ).filter(
            Room.current_occupancy >= RoomType.capacity
        ).count()
        
        if overcrowded_rooms > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fas fa-exclamation-triangle',
                'title': 'Phòng đầy hoặc quá tải',
                'count': overcrowded_rooms,
                'message': f"{overcrowded_rooms} phòng đã đạt hoặc vượt sức chứa",
                'action_url': '/rooms?status=overcrowded'
            })
        
        # Contracts expiring in next 7 days (urgent)
        urgent_expiring = Contract.query.filter(
            Contract.end_date <= date.today() + timedelta(days=7),
            Contract.end_date >= date.today()
        ).count()
        
        if urgent_expiring > 0:
            alerts.append({
                'type': 'danger',
                'icon': 'fas fa-clock',
                'title': 'Hợp đồng hết hạn trong 7 ngày',
                'count': urgent_expiring,
                'message': f"{urgent_expiring} hợp đồng sẽ hết hạn trong tuần này",
                'action_url': '/contracts?expiring=urgent'
            })
        
        # Pending registrations
        pending_registrations = Registration.query.filter_by(status='pending').count()
        if pending_registrations > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fas fa-clipboard-list',
                'title': 'Đơn đăng ký chờ duyệt',
                'count': pending_registrations,
                'message': f"{pending_registrations} đơn đăng ký đang chờ duyệt",
                'action_url': '/registrations'
            })

        return APIResponse.success(
            data={"alerts": alerts}, 
            message="Lấy thông báo thành công"
        )

    except Exception as e:
        return APIResponse.error(message=str(e), status_code=500)


def get_relative_time(timestamp):
    """Convert timestamp to relative time string"""
    if not timestamp:
        return "Không rõ"
    
    now = datetime.now()
    if isinstance(timestamp, date) and not isinstance(timestamp, datetime):
        timestamp = datetime.combine(timestamp, datetime.min.time())
    
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} ngày trước"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} giờ trước"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} phút trước"
    else:
        return "Vừa xong"