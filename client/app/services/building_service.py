from typing import Any, Dict

from app.services.api_client import api_client


class BuildingService:
    """Service for handling building management operations"""

    @staticmethod
    def get_buildings() -> Dict[str, Any]:
        """Get list of buildings"""
        # Return the complete API response (no data extraction)
        return api_client.get("/buildings")

    @staticmethod
    def get_building(building_id: int) -> Dict[str, Any]:
        """Get building details by ID"""
        # Return the complete API response (no data extraction)
        return api_client.get(f"/buildings/{building_id}")

    @staticmethod
    def create_building(building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new building"""
        # Return the complete API response (no data extraction)
        return api_client.post("/buildings", building_data)

    @staticmethod
    def update_building(building_id: int, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update building information"""
        # Return the complete API response (no data extraction)
        return api_client.put(f"/buildings/{building_id}", building_data)

    @staticmethod
    def delete_building(building_id: int) -> Dict[str, Any]:
        """Delete building by ID"""
        # Return the complete API response (no data extraction)
        return api_client.delete(f"/buildings/{building_id}")


# Global building service instance
building_service = BuildingService()
