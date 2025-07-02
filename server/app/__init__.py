from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, migrate, jwt

def create_app():
    app = Flask(__name__)
    # Chọn config theo environment
    app.config.from_object(DevelopmentConfig)

    # Khởi tạo extension
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    from .blueprints import (
        auth_bp, users_bp, rooms_bp, 
        registrations_bp, contracts_bp, 
        payments_bp, maintenance_bp
    )
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(registrations_bp, url_prefix='/api/registrations')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')

    return app
