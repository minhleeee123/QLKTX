from flask import session
from typing import Dict, Any, Optional
from .api_client import api_client


class AuthService:
    """Service for handling authentication operations"""

    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any]:
        """Login user with email and password"""
        data = {"email": email, "password": password}

        response = api_client.post("/auth/login", data)

        if response["success"]:
            # Store user info and token in session
            user_data = response["data"]
            session["user_id"] = user_data.get("user", {}).get("user_id")
            session["email"] = user_data.get("user", {}).get("email")
            session["role"] = user_data.get("user", {}).get("role")
            session["full_name"] = user_data.get("user", {}).get("full_name")
            session["access_token"] = user_data.get("access_token")
            session.permanent = True

        return response

    @staticmethod
    def logout() -> bool:
        """Logout current user"""
        try:
            # Call logout endpoint to invalidate token on server
            api_client.post("/auth/logout")
        except:
            pass  # Continue even if server logout fails
        finally:
            # Clear local session
            session.clear()

        return True

    @staticmethod
    def register(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        return api_client.post("/auth/register", user_data)

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current user info from session"""
        if "user_id" in session:
            return {
                "id": session.get("user_id"),
                "email": session.get("email"),
                "role": session.get("role"),
                "full_name": session.get("full_name"),
            }
        return None

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return "user_id" in session and "access_token" in session

    @staticmethod
    def has_role(role: str) -> bool:
        """Check if current user has specific role"""
        if not AuthService.is_authenticated():
            return False
        return session.get("role") == role

    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        return AuthService.has_role("admin")

    @staticmethod
    def is_staff() -> bool:
        """Check if current user is staff"""
        return AuthService.has_role("staff")

    @staticmethod
    def is_student() -> bool:
        """Check if current user is student"""
        return AuthService.has_role("student")

    @staticmethod
    def change_password(
        current_password: str, new_password: str, confirm_password: str
    ) -> Dict[str, Any]:
        """Change user password"""
        data = {
            "current_password": current_password,
            "new_password": new_password,
            "confirm_password": confirm_password,  # API yêu cầu confirm_password
        }
        return api_client.put("/auth/change-password", data)

    @staticmethod
    def refresh_token() -> Dict[str, Any]:
        """Refresh JWT token"""
        response = api_client.post("/auth/refresh")

        if response["success"]:
            # Update token in session
            session["access_token"] = response["data"].get("access_token")

        return response


# Global auth service instance
auth_service = AuthService()
