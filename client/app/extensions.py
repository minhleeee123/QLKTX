from flask_session import Session
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
session = Session()
csrf = CSRFProtect()