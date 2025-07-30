import json
from typing import Any, Dict, Optional

from app.services.api_client import api_client


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

        # Return the complete API response (no data extraction)
        return api_client.get("/rooms", params)

    @staticmethod
    def get_room(room_id: int) -> Dict[str, Any]:
        """Get room details by ID"""
        # Return the complete API response (no data extraction)
        return api_client.get(f"/rooms/{room_id}")

    @staticmethod
    def create_room(room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new room"""
        # Return the complete API response (no data extraction)
        return api_client.post("/rooms", room_data)

    @staticmethod
    def update_room(room_id: int, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update room information"""
        # Return the complete API response (no data extraction)
        return api_client.put(f"/rooms/{room_id}", room_data)

    @staticmethod
    def delete_room(room_id: int) -> Dict[str, Any]:
        """Delete room by ID"""
        # Return the complete API response (no data extraction)
        return api_client.delete(f"/rooms/{room_id}")

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
