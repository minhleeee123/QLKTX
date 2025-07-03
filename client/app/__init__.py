import os
from flask import Flask, redirect, url_for, render_template
from .extensions import session, csrf
from .services.auth_service import auth_service
from .blueprints import auth_bp, dashboard_bp

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
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Global template context processor
    @app.context_processor
    def inject_user():
        return {
            'current_user': auth_service.get_current_user(),
            'is_authenticated': auth_service.is_authenticated()
        }
    
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