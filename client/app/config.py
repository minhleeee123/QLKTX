import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'qlktx:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Server API configuration
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://localhost:5000/api'
    
    # WTForms configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
