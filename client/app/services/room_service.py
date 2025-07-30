from typing import Dict, Any, Optional
import json
from .api_client import api_client
from app.utils.api_response import APIResponse


class RoomService:
    """Service for handling room management operations"""

    @staticmethod
    def get_rooms(page: int = 1, per_page: int = 20, building_id: int = None, 
                 room_type_id: int = None, status: str = None, search: str = None) -> Dict[str, Any]:
        """Get list of rooms with pagination and filters"""
        params = {
            'page': page,
            'per_page': per_page
        }

        if building_id:
            params['building_id'] = building_id
        if room_type_id:
            params['room_type_id'] = room_type_id
        if status:
            params['status'] = status
        if search:
            params['search'] = search

        response = api_client.get("/rooms", params)
        if response.get('success'):
            return response.get('data', {})
        else:
            raise Exception(response.get('error', 'Unknown error'))

    @staticmethod
    def get_room(room_id: int) -> Dict[str, Any]:
        """Get room details by ID"""
        response = api_client.get(f"/rooms/{room_id}")

        if response.get("success") and response.get("data"):
            # API client wraps the server response in {success: true, data: {...}}
            # Server returns {room: {...}}
            data = response["data"]
            if "room" in data:
                return {"success": True, "room": data["room"]}
            else:
                return {"success": False, "error": "Dữ liệu phòng không hợp lệ"}
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể lấy thông tin phòng')
            }

    @staticmethod
    def create_room(room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new room"""
        response = api_client.post("/rooms", room_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return {"success": True, "room": server_data.get("room", server_data)}
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể tạo phòng')
            }

    @staticmethod
    def update_room(room_id: int, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update room information"""
        response = api_client.put(f"/rooms/{room_id}", room_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return {"success": True, "room": server_data.get("room", server_data)}
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể cập nhật phòng')
            }

    @staticmethod
    def delete_room(room_id: int) -> Dict[str, Any]:
        """Delete room by ID"""
        response = api_client.delete(f"/rooms/{room_id}")

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success"):
            server_data = response.get("data", {})
            return {
                "success": True,
                "message": server_data.get("message", "Xóa phòng thành công"),
            }
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể xóa phòng')
            }

    @staticmethod
    def get_buildings() -> Dict[str, Any]:
        """Get list of buildings"""
        response = api_client.get("/rooms/buildings")

        if response.get("success") and response.get("data"):
            server_data = response["data"]
            if "buildings" in server_data:
                return {"success": True, "buildings": server_data["buildings"]}
            else:
                return {
                    "success": False,
                    "error": "Invalid response format from server",
                }
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể tải danh sách tòa nhà')
            }

    @staticmethod
    def create_building(building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new building"""
        response = api_client.post("/rooms/buildings", building_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            return {"success": True, "building": response["data"]}
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể tạo tòa nhà"),
            }

    @staticmethod
    def update_building(building_id: int, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update building information"""
        response = api_client.put(f"/rooms/buildings/{building_id}", building_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            return {"success": True, "building": response["data"]}
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể cập nhật tòa nhà"),
            }

    @staticmethod
    def delete_building(building_id: int) -> Dict[str, Any]:
        """Delete building by ID"""
        response = api_client.delete(f"/rooms/buildings/{building_id}")

        # API client wraps response in {success: bool, data: {...}}
        if response.get('success'):
            server_data = response.get("data", {})
            return {
                "success": True,
                "message": server_data.get("message", "Xóa tòa nhà thành công"),
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể xóa tòa nhà"),
            }

    @staticmethod
    def get_room_types() -> Dict[str, Any]:
        """Get list of room types"""
        response = api_client.get("/rooms/room-types")

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            # Server returns {room_types: [...]} in the data field
            server_data = response["data"]
            if "room_types" in server_data:
                return {"success": True, "room_types": server_data["room_types"]}
            else:
                return {
                    "success": False,
                    "error": "Invalid response format from server",
                }
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể tải danh sách loại phòng')
            }

    @staticmethod
    def create_room_type(room_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new room type"""
        response = api_client.post("/rooms/room-types", room_type_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            return {"success": True, "room_type": response["data"]}
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể tạo loại phòng"),
            }

    @staticmethod
    def update_room_type(room_type_id: int, room_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update room type information"""
        response = api_client.put(f"/rooms/room-types/{room_type_id}", room_type_data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            return {"success": True, "room_type": response["data"]}
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể cập nhật loại phòng"),
            }

    @staticmethod
    def delete_room_type(room_type_id: int) -> Dict[str, Any]:
        """Delete room type by ID"""
        response = api_client.delete(f"/rooms/room-types/{room_type_id}")

        # API client wraps response in {success: bool, data: {...}}
        if response.get('success'):
            server_data = response.get("data", {})
            return {
                "success": True,
                "message": server_data.get("message", "Xóa loại phòng thành công"),
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Không thể xóa loại phòng"),
            }

    @staticmethod
    def get_room_statuses() -> list:
        """Get available room statuses"""
        return [
            {'value': 'available', 'label': 'Có sẵn'},
            {'value': 'occupied', 'label': 'Đã có người ở'},
            {'value': 'pending_approval', 'label': 'Chờ duyệt'},
            {'value': 'maintenance', 'label': 'Bảo trì'}
        ]


# Global room service instance
room_service = RoomService()
