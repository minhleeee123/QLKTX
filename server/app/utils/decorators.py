"""
Decorators for the server application.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

def require_role(allowed_roles):
    """
    Decorator để kiểm tra quyền truy cập dựa trên vai trò người dùng.
    
    Args:
        allowed_roles (list or str): Danh sách các vai trò được phép truy cập hoặc một vai trò đơn lẻ.
    
    Returns:
        function: Decorated function that checks user role before executing the view function.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
        
    def decorator(f):
        @wraps(f)
        @jwt_required()  # Ensure JWT is checked before role
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role.role_name not in allowed_roles:
                return jsonify({'message': 'Không có quyền truy cập'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
