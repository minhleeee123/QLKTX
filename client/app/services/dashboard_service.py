from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.services.api_client import api_client
from app.services.contract_service import ContractService
from app.services.registration_service import registration_service
from app.utils.api_response import APIResponse


class DashboardService:
    """Service for fetching dashboard data from the server API"""

    @staticmethod
    def get_admin_dashboard_stats() -> Dict[str, Any]:
        """Get comprehensive dashboard statistics for admin"""
        response = api_client.get("/dashboard/admin-stats")
        
        if response.get("success") and response.get("data"):
            return APIResponse.success_dict(data=response["data"])
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy thống kê dashboard")
            )
    
    @staticmethod
    def get_recent_activities(limit: int = 10) -> Dict[str, Any]:
        """Get recent activities for dashboard"""
        params = {'limit': limit}
        response = api_client.get("/dashboard/recent-activities", params)
        
        if response.get("success") and response.get("data"):
            return APIResponse.success_dict(data=response["data"])
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy hoạt động gần đây")
            )
    
    @staticmethod
    def get_dashboard_alerts() -> Dict[str, Any]:
        """Get important alerts for dashboard"""
        response = api_client.get("/dashboard/alerts")
        
        if response.get("success") and response.get("data"):
            return APIResponse.success_dict(data=response["data"])
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy thông báo")
            )

    @staticmethod
    def get_student_dashboard_data(user_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a student"""
        dashboard_data = {
            'current_room': None,
            'contract': None,
            'registrations': [],
            'recent_payments': [],
            'pending_maintenance': 0,
            'notifications': []
        }

        # Get student's registrations
        registrations_response = registration_service.get_registrations()
        if registrations_response.get('success') and registrations_response.get('data'):
            registrations_data = registrations_response['data']
            if 'registrations' in registrations_data:
                dashboard_data['registrations'] = registrations_data['registrations']

                # Find approved registration (current room)
                for reg in dashboard_data['registrations']:
                    if reg['status'] == 'approved':
                        dashboard_data['current_room'] = {
                            'room_number': reg['room']['room_number'],
                            'building_name': reg['room']['building_name'],
                            'room_type': reg['room']['room_type'],
                            'price': reg['room']['price'],
                            'registration_date': reg['registration_date']
                        }
                        break

        # Get student's contracts
        contracts_response = ContractService.get_contracts()
        if contracts_response.get('success') and contracts_response.get('data'):
            contracts_data = contracts_response['data']
            if 'contracts' in contracts_data and contracts_data['contracts']:
                # Get the most recent active contract
                active_contracts = [c for c in contracts_data['contracts'] if c.get('status') == 'active']
                if active_contracts:
                    dashboard_data['contract'] = active_contracts[0]

        # Get payment information (this would need a payment service)
        # For now, we'll simulate this based on contract data
        if dashboard_data['contract']:
            dashboard_data['recent_payments'] = DashboardService._get_mock_payment_data(
                dashboard_data['contract']
            )

        # Generate notifications based on data
        dashboard_data['notifications'] = DashboardService._generate_notifications(dashboard_data)

        return dashboard_data

    @staticmethod
    def _get_mock_payment_data(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock payment data based on contract info"""
        # This is temporary until we have a proper payment service
        return [
            {
                'month': '7/2025',
                'amount': contract.get('monthly_rent', 2500000),
                'status': 'paid',
                'paid_date': '2025-07-05'
            },
            {
                'month': '8/2025',
                'amount': contract.get('monthly_rent', 2500000),
                'status': 'pending',
                'due_date': '2025-08-15'
            }
        ]

    @staticmethod
    def _generate_notifications(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate notifications based on student data"""
        notifications = []

        # Payment reminder
        if data['recent_payments']:
            pending_payments = [p for p in data['recent_payments'] if p['status'] == 'pending']
            if pending_payments:
                notifications.append({
                    'type': 'warning',
                    'title': 'Nhắc nhở!',
                    'message': f"Tiền phòng tháng {pending_payments[0]['month']} đến hạn thanh toán trong 5 ngày."
                })

        # Registration status
        if data['registrations']:
            pending_regs = [r for r in data['registrations'] if r['status'] == 'pending']
            if pending_regs:
                notifications.append({
                    'type': 'info',
                    'title': 'Đơn đăng ký',
                    'message': f"Bạn có {len(pending_regs)} đơn đăng ký phòng đang chờ xử lý."
                })

        # Default notifications if no real data
        if not notifications:
            notifications = [
                {
                    'type': 'info',
                    'title': 'Thông báo',
                    'message': 'Chào mừng bạn đến với hệ thống quản lý ký túc xá!'
                }
            ]

        return notifications

    @staticmethod
    def get_recent_activities(user_id: int) -> List[Dict[str, Any]]:
        """Get recent activities for a student"""
        activities = []

        # Get registrations for activity history
        registrations_response = registration_service.get_registrations()
        if registrations_response.get('success') and registrations_response.get('data'):
            registrations_data = registrations_response['data']
            if 'registrations' in registrations_data:
                for reg in registrations_data['registrations'][-3:]:  # Last 3 registrations
                    reg_date = DashboardService._format_date_for_display(reg['registration_date'])
                    if reg['status'] == 'approved':
                        activities.append({
                            'icon': 'fas fa-check-circle text-success',
                            'description': f"Đơn đăng ký phòng {reg['room']['room_number']} đã được duyệt",
                            'date': reg_date
                        })
                    elif reg['status'] == 'pending':
                        activities.append({
                            'icon': 'fas fa-clock text-warning',
                            'description': f"Đã gửi đơn đăng ký phòng {reg['room']['room_number']}",
                            'date': reg_date
                        })
                    elif reg['status'] == 'rejected':
                        activities.append({
                            'icon': 'fas fa-times-circle text-danger',
                            'description': f"Đơn đăng ký phòng {reg['room']['room_number']} bị từ chối",
                            'date': reg_date
                        })

        # Add some default activities if no real data
        if not activities:
            activities = [
                {
                    'icon': 'fas fa-user-circle text-info',
                    'description': 'Chào mừng bạn đến với hệ thống ký túc xá',
                    'date': DashboardService._format_date_for_display(datetime.now().isoformat())
                }
            ]

        return activities

    @staticmethod
    def _format_date_for_display(date_str: str) -> str:
        """Format ISO date string for user-friendly display"""
        try:
            if isinstance(date_str, str):
                # Handle different date formats
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                
                # Calculate relative time
                now = datetime.now()
                if dt.date() == now.date():
                    return "Hôm nay"
                elif dt.date() == (now - timedelta(days=1)).date():
                    return "Hôm qua"
                elif (now - dt).days < 7:
                    return f"{(now - dt).days} ngày trước"
                else:
                    return dt.strftime('%d/%m/%Y')
            return date_str
        except (ValueError, AttributeError):
            return "Gần đây"


# Global instance
dashboard_service = DashboardService()
dashboard_service = DashboardService()
