from .auth import auth_bp
from .dashboard import dashboard_bp
from .users import users_bp
from .rooms import rooms_bp

__all__ = ['auth_bp', 'dashboard_bp', 'users_bp', 'rooms_bp']
