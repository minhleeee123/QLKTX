import json
from flask import session
from typing import Dict, Any, Optional
from flask_login import login_user, logout_user, current_user
from .api_client import api_client
from ..models.user import User


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
            user_info = user_data.get("user", {})
            session["user_id"] = user_info.get("user_id")
            session["email"] = user_info.get("email")
            session["role"] = user_info.get("role")
            session["full_name"] = user_info.get("full_name")
            session["access_token"] = user_data.get("access_token")
            session.permanent = True
            
            # Create User object for Flask-Login
            user = User(user_info)
            login_user(user, remember=True)

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
            # Logout from Flask-Login
            logout_user()
            # Clear local session
            session.clear()

        return True

    @staticmethod
    def register(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        return api_client.post("/auth/register", user_data)

    @staticmethod
    def get_current_user() -> Optional[User]:
        """Get current user info"""
        if current_user.is_authenticated:
            return current_user
        return None

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return current_user.is_authenticated and "access_token" in session

    @staticmethod
    def has_role(role: str) -> bool:
        """Check if current user has specific role"""
        if not AuthService.is_authenticated():
            return False
        return current_user.role == role

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
    def is_management() -> bool:
        """Check if current user is management"""
        return AuthService.has_role("management")

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
