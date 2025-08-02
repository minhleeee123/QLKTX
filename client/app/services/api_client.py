import requests
from flask import current_app, json, session
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.api_response import APIResponse


class APIClient:
    """Base API client for communicating with the server"""

    def __init__(self):
        self.base_url = None
        self.session = requests.Session()

    def _get_base_url(self) -> str:
        """Get the API base URL from config"""
        if not self.base_url:
            self.base_url = current_app.config["API_BASE_URL"]
        return self.base_url

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including JWT token if available"""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Add JWT token if user is logged in
        if "access_token" in session:
            headers["Authorization"] = f"Bearer {session['access_token']}"

        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return backend's standardized JSON data"""
        try:
            data = response.json()
            # If token expired, clear session
            if response.status_code == 401:
                session.clear()

            # Return the backend response as-is since it's already properly structured
            return data

        except ValueError:
            # Fallback for non-JSON responses
            return {
                "success": False,
                "message": "Invalid response format",
                "data": None,
                "status_code": response.status_code,
            }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        url = f"{self._get_base_url()}{endpoint}"

        try:
            response = self.session.get(
                url, headers=self._get_headers(), params=params, timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "data": None,
                "status_code": 500,
            }

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        url = f"{self._get_base_url()}{endpoint}"

        try:
            response = self.session.post(
                url, headers=self._get_headers(), json=data, timeout=30
            )

            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "data": None,
                "status_code": 500,
            }

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request to API"""
        url = f"{self._get_base_url()}{endpoint}"

        try:
            response = self.session.put(
                url, headers=self._get_headers(), json=data, timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "data": None,
                "status_code": 500,
            }

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        url = f"{self._get_base_url()}{endpoint}"

        try:
            response = self.session.delete(url, headers=self._get_headers(), timeout=30)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "data": None,
                "status_code": 500,
            }


# Global API client instance
api_client = APIClient()
