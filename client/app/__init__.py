import os
from datetime import datetime
from flask import Flask, redirect, url_for, render_template
from .extensions import session, csrf, login_manager
from .services.auth_service import auth_service
from .blueprints import auth_bp, dashboard_bp, users_bp, rooms_bp

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        from .config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    session.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'warning'
    
    # User loader for Flask-Login
    from .models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        from flask import session
        if 'user_id' in session and str(session.get('user_id')) == user_id:
            # Create user from session data
            user_data = {
                'user_id': session.get('user_id'),
                'email': session.get('email'),
                'role': session.get('role'),
                'full_name': session.get('full_name')
            }
            return User(user_data)
        return None
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(rooms_bp, url_prefix='/rooms')
    
    # Global template context processor
    @app.context_processor
    def inject_user():
        return {
            'current_user': auth_service.get_current_user(),
            'is_authenticated': auth_service.is_authenticated()
        }
    
    # Template filters
    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y'):
        """Format datetime string"""
        if not value:
            return '-'
        try:
            if isinstance(value, str):
                # Parse ISO format from API
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                dt = value
            return dt.strftime(format)
        except:
            return value
    
    @app.template_filter('datetime_full')
    def datetime_full_filter(value):
        """Format datetime with time"""
        return datetime_filter(value, '%d/%m/%Y %H:%M')
    
    # Root route - redirect to dashboard or login
    @app.route('/')
    def index():
        if auth_service.is_authenticated():
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app