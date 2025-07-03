from functools import wraps
from flask import redirect, url_for, flash, request, abort
from ..services.auth_service import auth_service

def login_required(f):
    """Decorator to require login for accessing routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_service.is_authenticated():
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to require specific role for accessing routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_service.is_authenticated():
                flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not auth_service.has_role(role):
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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_service.is_authenticated():
            flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not auth_service.has_role('admin') and not auth_service.has_role('management'):
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
        if auth_service.is_authenticated():
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
