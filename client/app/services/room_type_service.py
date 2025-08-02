from typing import Any, Dict

from app.services.api_client import api_client


class RoomTypeService:
    """Service for handling room type management operations"""

    @staticmethod
    def get_room_types(page: int = 1, per_page: int = 20, search: str = None, 
                      min_capacity: int = None, max_capacity: int = None,
                      min_price: float = None, max_price: float = None) -> Dict[str, Any]:
        """Get list of room types with pagination and filters"""
        params = {
            'page': page,
            'per_page': per_page
        }

        if search:
            params['search'] = search
        if min_capacity:
            params['min_capacity'] = min_capacity
        if max_capacity:
            params['max_capacity'] = max_capacity
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price

        # Return the complete API response (no data extraction)
        return api_client.get("/room-types", params)

    @staticmethod
    def get_room_type(room_type_id: int) -> Dict[str, Any]:
        """Get room type details by ID"""
        # Return the complete API response (no data extraction)
        return api_client.get(f"/room-types/{room_type_id}")

    @staticmethod
    def create_room_type(room_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new room type"""
        # Return the complete API response (no data extraction)
        return api_client.post("/room-types", room_type_data)

    @staticmethod
    def update_room_type(room_type_id: int, room_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update room type information"""
        # Return the complete API response (no data extraction)
        return api_client.put(f"/room-types/{room_type_id}", room_type_data)

    @staticmethod
    def delete_room_type(room_type_id: int) -> Dict[str, Any]:
        """Delete room type by ID"""
        # Return the complete API response (no data extraction)
        return api_client.delete(f"/room-types/{room_type_id}")


# Global room type service instance
room_type_service = RoomTypeService()
