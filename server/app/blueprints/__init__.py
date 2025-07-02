from .auth import auth_bp
from .users import users_bp
from .rooms import rooms_bp
from .registrations import registrations_bp
from .contracts import contracts_bp
from .payments import payments_bp
from .maintenance import maintenance_bp

__all__ = [
    'auth_bp',
    'users_bp', 
    'rooms_bp',
    'registrations_bp',
    'contracts_bp',
    'payments_bp',
    'maintenance_bp'
]
