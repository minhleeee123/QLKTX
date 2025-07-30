from flask import jsonify
from datetime import datetime
from typing import Dict, Any, Optional


class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Return a successful API response"""
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message="An error occurred", status_code=400, error_code=None):
        """Return an error API response"""
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code
    
    @staticmethod
    def success_dict(data=None, message="Success", status_code=200):
        """Return a successful API response as dictionary"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error_dict(message="An error occurred", status_code=400, error_code=None):
        """Return an error API response as dictionary"""
        return {
            "success": False,
            "message": message,
            "error_code": error_code,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }


def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum items per page allowed
    
    Returns:
        Dictionary with pagination data
    """
    # Ensure per_page doesn't exceed maximum
    per_page = min(per_page, max_per_page)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Calculate pagination metadata
    has_prev = page > 1
    has_next = (page * per_page) < total
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next,
            "prev_page": prev_page,
            "next_page": next_page
        }
    }
