from typing import Dict, Any, Optional

from flask import json
from .api_client import api_client


class UserService:
    """Service for handling user management operations"""

    @staticmethod
    def get_users(
        page: int = 1, per_page: int = 10, role: str = None, search: str = None
    ) -> Dict[str, Any]:
        """Get list of users with pagination and filters"""
        params = {"page": page, "per_page": per_page}

        if role:
            params["role"] = role
        if search:
            params["search"] = search

        # Return the complete API response (no data extraction)
        return api_client.get("/users", params)

    @staticmethod
    def get_user(user_id: int) -> Dict[str, Any]:
        """Get user details by ID"""
        # Return the complete API response (no data extraction)
        response = api_client.get(f"/users/{user_id}")

        user = response.get("data")

        return user

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        # Return the complete API response (no data extraction)
        return api_client.post("/users", user_data)

    @staticmethod
    def update_user(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        # Return the complete API response (no data extraction)
        return api_client.put(f"/users/{user_id}", user_data)

    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        """Delete user by ID"""
        # Return the complete API response (no data extraction)
        return api_client.delete(f"/users/{user_id}")

    @staticmethod
    def get_roles() -> list:
        """Get available roles"""
        return [
            {"value": "admin", "label": "Quản trị viên"},
            {"value": "management", "label": "Quản lý"},
            {"value": "student", "label": "Sinh viên"},
            {"value": "staff", "label": "Nhân viên"},
        ]


# Global user service instance
user_service = UserService()
