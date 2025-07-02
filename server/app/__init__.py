from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    # Chọn config theo environment
    app.config.from_object(DevelopmentConfig)

    # Khởi tạo extension
    db.init_app(app)
    migrate.init_app(app, db)

    # (Sau này) register blueprint ở đây
    # from .blueprints.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
