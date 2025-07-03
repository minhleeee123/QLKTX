from flask import Blueprint, render_template, redirect, url_for
from ..services.auth_service import auth_service
from ..utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page - redirects based on user role"""
    user = auth_service.get_current_user()
    print(user)  # Debugging line to check user details
    print("Index route accessed")  # Debugging line to check route access
    if user['role'] == 'admin':
        print("Redirecting to admin dashboard")  # Debugging line
        return redirect(url_for('dashboard.admin'))
    elif user['role'] == 'staff':
        return redirect(url_for('dashboard.staff'))
    elif user['role'] == 'student':
        return redirect(url_for('dashboard.student'))
    else:
        return redirect(url_for('auth.logout'))

@dashboard_bp.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if not auth_service.is_admin():
        return redirect(url_for('dashboard.index'))
    
    user = auth_service.get_current_user()
    return render_template('dashboard/admin.html', user=user)

@dashboard_bp.route('/staff')
@login_required
def staff():
    """Staff dashboard"""
    if not auth_service.is_staff():
        return redirect(url_for('dashboard.index'))
    
    user = auth_service.get_current_user()
    return render_template('dashboard/staff.html', user=user)

@dashboard_bp.route('/student')
@login_required
def student():
    """Student dashboard"""
    if not auth_service.is_student():
        return redirect(url_for('dashboard.index'))
    
    user = auth_service.get_current_user()
    return render_template('dashboard/student.html', user=user)
