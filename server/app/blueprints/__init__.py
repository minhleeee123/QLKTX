from app.blueprints.auth import auth_bp
from app.blueprints.buildings import buildings_bp
from app.blueprints.contracts import contracts_bp
from app.blueprints.maintenance import maintenance_bp
from app.blueprints.payments import payments_bp
from app.blueprints.registrations import registrations_bp
from app.blueprints.room_types import room_types_bp
from app.blueprints.rooms import rooms_bp
from app.blueprints.users import users_bp

__all__ = [
    "auth_bp",
    "users_bp",
    "buildings_bp",
    "room_types_bp",
    "rooms_bp",
    "registrations_bp",
    "contracts_bp",
    "payments_bp",
    "maintenance_bp",
]
