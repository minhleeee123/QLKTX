from app.blueprints import (
    auth_bp,
    buildings_bp,
    contracts_bp,
    dashboard_bp,
    maintenance_bp,
    payments_bp,
    registrations_bp,
    room_types_bp,
    rooms_bp,
    users_bp,
)
from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, jwt, migrate
from flask import Flask, request


def create_app():
    app = Flask(__name__)
    # Chọn config theo environment
    app.config.from_object(DevelopmentConfig)

    # Enable CORS for cross-origin requests from client (port 5001 to port 5000)
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5001")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

    # Handle preflight requests
    @app.before_request
    def before_request():
        if request.method == "OPTIONS":
            response = Flask.response_class()
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:5001")
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
            )
            return response

    # Khởi tạo extension
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(buildings_bp, url_prefix="/api/buildings")
    app.register_blueprint(room_types_bp, url_prefix="/api/room-types")
    app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
    app.register_blueprint(registrations_bp, url_prefix="/api/registrations")
    app.register_blueprint(contracts_bp, url_prefix="/api/contracts")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(maintenance_bp, url_prefix="/api/maintenance")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Home page route to display all API endpoints
    @app.route("/")
    def home():
        """Display all available API endpoints with actual links"""

        base_url = request.url_root.rstrip("/")

        api_endpoints = {
            "1. QLKTX - Quản Lý Ký Túc Xá - APIs": {
                "description": "API Documentation for Dormitory Management System",
                "version": "1.0.0",
                "base_url": f"{base_url}/api",
            },
            "Authentication Endpoints": {
                f"{base_url}/api/auth/login": "POST - User login",
                f"{base_url}/api/auth/logout": "POST - User logout",
                f"{base_url}/api/auth/refresh": "POST - Refresh JWT token",
                f"{base_url}/api/auth/me": "GET - Get current user info",
            },
            "User Management": {
                f"{base_url}/api/users": "GET - Get list of users (with pagination)",
                f"{base_url}/api/users/{{id}}": "GET - Get user details",
                f"{base_url}/api/users": "POST - Create new user (admin only)",
                f"{base_url}/api/users/{{id}}": "PUT - Update user (admin only)",
                f"{base_url}/api/users/{{id}}": "DELETE - Delete user (admin only)",
                f"{base_url}/api/users/simple": "GET - Get simplified user list for dropdowns",
            },
            "Building Management": {
                f"{base_url}/api/buildings": "GET - Get list of buildings (with pagination)",
                f"{base_url}/api/buildings/{{id}}": "GET - Get building details",
                f"{base_url}/api/buildings": "POST - Create new building (admin only)",
                f"{base_url}/api/buildings/{{id}}": "PUT - Update building (admin only)",
                f"{base_url}/api/buildings/{{id}}": "DELETE - Delete building (admin only)",
                f"{base_url}/api/buildings/simple": "GET - Get simplified building list for dropdowns",
            },
            "Room Type Management": {
                f"{base_url}/api/room-types": "GET - Get list of room types (with pagination)",
                f"{base_url}/api/room-types/{{id}}": "GET - Get room type details",
                f"{base_url}/api/room-types": "POST - Create new room type (admin only)",
                f"{base_url}/api/room-types/{{id}}": "PUT - Update room type (admin only)",
                f"{base_url}/api/room-types/{{id}}": "DELETE - Delete room type (admin only)",
                f"{base_url}/api/room-types/simple": "GET - Get simplified room type list for dropdowns",
            },
            "Room Management": {
                f"{base_url}/api/rooms": "GET - Get list of rooms (with pagination and filters)",
                f"{base_url}/api/rooms/{{id}}": "GET - Get room details",
                f"{base_url}/api/rooms": "POST - Create new room (admin only)",
                f"{base_url}/api/rooms/{{id}}": "PUT - Update room (admin only)",
                f"{base_url}/api/rooms/{{id}}": "DELETE - Delete room (admin only)",
                f"{base_url}/api/rooms/available": "GET - Get available rooms",
                f"{base_url}/api/rooms/simple": "GET - Get simplified room list for dropdowns",
            },
            "Registration Management": {
                f"{base_url}/api/registrations": "GET - Get list of registrations (with pagination)",
                f"{base_url}/api/registrations/{{id}}": "GET - Get registration details",
                f"{base_url}/api/registrations": "POST - Create new registration",
                f"{base_url}/api/registrations/{{id}}": "PUT - Update registration status (admin only)",
                f"{base_url}/api/registrations/{{id}}": "DELETE - Delete registration",
                f"{base_url}/api/registrations/my": "GET - Get current user's registrations",
            },
            "Contract Management": {
                f"{base_url}/api/contracts": "GET - Get list of contracts (with pagination)",
                f"{base_url}/api/contracts/{{id}}": "GET - Get contract details",
                f"{base_url}/api/contracts": "POST - Create new contract (admin only)",
                f"{base_url}/api/contracts/{{id}}": "PUT - Update contract (admin only)",
                f"{base_url}/api/contracts/{{id}}": "DELETE - Delete contract (admin only)",
                f"{base_url}/api/contracts/my": "GET - Get current user's contracts",
            },
            "Payment Management": {
                f"{base_url}/api/payments": "GET - Get list of payments (with pagination)",
                f"{base_url}/api/payments/{{id}}": "GET - Get payment details",
                f"{base_url}/api/payments": "POST - Create new payment",
                f"{base_url}/api/payments/{{id}}": "PUT - Update payment status (admin only)",
                f"{base_url}/api/payments/{{id}}": "DELETE - Delete payment (admin only)",
                f"{base_url}/api/payments/my": "GET - Get current user's payments",
            },
            "Maintenance Management": {
                f"{base_url}/api/maintenance": "GET - Get list of maintenance requests (with pagination)",
                f"{base_url}/api/maintenance/{{id}}": "GET - Get maintenance request details",
                f"{base_url}/api/maintenance": "POST - Create new maintenance request",
                f"{base_url}/api/maintenance/{{id}}": "PUT - Update maintenance request",
                f"{base_url}/api/maintenance/{{id}}": "DELETE - Delete maintenance request",
                f"{base_url}/api/maintenance/my": "GET - Get current user's maintenance requests",
            },
            "Usage Notes": {
                "authentication": "Most endpoints require JWT token in Authorization header: 'Bearer <token>'",
                "admin_only": "Endpoints marked '(admin only)' require admin role",
                "pagination": "List endpoints support pagination with 'page' and 'per_page' query parameters",
                "filtering": "Many endpoints support filtering with various query parameters",
                "content_type": "POST/PUT requests require 'Content-Type: application/json' header",
                "id_placeholder": "Replace {id} in URLs with actual numeric IDs",
            },
        }
        return api_endpoints

    return app
