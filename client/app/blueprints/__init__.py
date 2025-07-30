from app.blueprints.auth import auth_bp
from app.blueprints.buildings import buildings_bp
from app.blueprints.contracts import contracts_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.room_types import room_types_bp
from app.blueprints.rooms import rooms_bp
from app.blueprints.users import users_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "users_bp",
    "rooms_bp",
    "contracts_bp",
    "buildings_bp",
    "room_types_bp",
]
