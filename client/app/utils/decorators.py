from functools import wraps

from app.services.auth_service import auth_service
from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_required


def role_required(role):
    """Decorator to require specific role for accessing routes"""
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.role == role:
                # Use abort(403) to trigger the 403 error page
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def management_required(f):
    """Decorator to require admin or management role"""
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role in ['admin', 'management']:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator to require staff role"""
    return role_required('staff')(f)

def student_required(f):
    """Decorator to require student role"""
    return role_required('student')(f)

def anonymous_required(f):
    """Decorator to require user to be logged out (for login/register pages)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function