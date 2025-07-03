import requests
from flask import current_app, session
from typing import Dict, Any, Optional

class APIClient:
    """Base API client for communicating with the server"""
    
    def __init__(self):
        self.base_url = None
        self.session = requests.Session()
        
    def _get_base_url(self) -> str:
        """Get the API base URL from config"""
        if not self.base_url:
            self.base_url = current_app.config['API_BASE_URL']
        return self.base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including JWT token if available"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add JWT token if user is logged in
        if 'access_token' in session:
            headers['Authorization'] = f"Bearer {session['access_token']}"
            
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return JSON data"""
        try:
            data = response.json()
        except ValueError:
            data = 'Invalid response format'
            
        if not response.ok:
            # If token expired, clear session
            if response.status_code == 401:
                session.clear()
                
        return {
            'success': response.ok,
            'status_code': response.status_code,
            'data': data if response.ok else None,
            'error': data if not response.ok else None
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        url = f"{self._get_base_url()}{endpoint}"
        
        try:
            response = self.session.get(
                url, 
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': 500,
                'data': None,
                'error': f'Connection error: {str(e)}'
            }
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        url = f"{self._get_base_url()}{endpoint}"
        
        try:
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': 500,
                'data': None,
                'error': f'Connection error: {str(e)}'
            }
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request to API"""
        url = f"{self._get_base_url()}{endpoint}"
        
        try:
            response = self.session.put(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': 500,
                'data': None,
                'error': f'Connection error: {str(e)}'
            }
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        url = f"{self._get_base_url()}{endpoint}"
        
        try:
            response = self.session.delete(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': 500,
                'data': None,
                'error': f'Connection error: {str(e)}'
            }

# Global API client instance
api_client = APIClient()
