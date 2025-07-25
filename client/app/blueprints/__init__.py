from .auth import auth_bp
from .dashboard import dashboard_bp
from .users import users_bp
from .rooms import rooms_bp
from .contracts import contracts_bp
from .buildings import buildings_bp
from .room_types import room_types_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "users_bp",
    "rooms_bp",
    "contracts_bp",
    "buildings_bp",
    "room_types_bp",
]
