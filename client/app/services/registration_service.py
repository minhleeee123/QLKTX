import json
from typing import Any, Dict, Optional

from app.services.api_client import api_client


class RegistrationService:
    """Service for handling room registration operations"""

    @staticmethod
    def get_registrations(page: int = 1, per_page: int = 20, status: str = None) -> Dict[str, Any]:
        """Get list of registrations with pagination and filters"""
        params = {
            'page': page,
            'per_page': per_page
        }

        if status:
            params['status'] = status

        # Return the complete API response (no data extraction)
        return api_client.get("/registrations", params)

    @staticmethod
    def get_registration(registration_id: int) -> Dict[str, Any]:
        """Get registration details by ID"""
        # Return the complete API response (no data extraction)
        return api_client.get(f"/registrations/{registration_id}/json")

    @staticmethod
    def create_registration(room_id: int) -> Dict[str, Any]:
        """Create new room registration"""
        registration_data = {
            'room_id': room_id
        }
        # Return the complete API response (no data extraction)
        return api_client.post("/registrations", registration_data)

    @staticmethod
    def cancel_registration(registration_id: int) -> Dict[str, Any]:
        """Cancel a registration (DELETE request)"""
        # Return the complete API response (no data extraction)
        return api_client.delete(f"/registrations/{registration_id}")

    @staticmethod
    def approve_registration(registration_id: int) -> Dict[str, Any]:
        """Approve a registration (admin only)"""
        # Return the complete API response (no data extraction)
        return api_client.post(f"/registrations/{registration_id}/approve", {})

    @staticmethod
    def reject_registration(registration_id: int) -> Dict[str, Any]:
        """Reject a registration (admin only)"""
        # Return the complete API response (no data extraction)
        return api_client.post(f"/registrations/{registration_id}/reject", {})


# Global registration service instance
registration_service = RegistrationService()
