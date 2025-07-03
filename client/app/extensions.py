from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Initialize extensions
session = Session()
csrf = CSRFProtect()
login_manager = LoginManager()