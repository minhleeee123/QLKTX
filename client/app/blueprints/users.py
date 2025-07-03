from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..forms.user_forms import UserForm, UserSearchForm
from ..services.user_service import user_service
from ..services.auth_service import auth_service
from ..utils.decorators import login_required, admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@admin_required
def list_users():
    """List all users with pagination and search"""
    search_form = UserSearchForm()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    # Call API to get users
    response = user_service.get_users(
        page=page,
        per_page=per_page,
        search=search if search else None,
        role=role if role else None
    )
    
    if response['success']:
        users_data = response['data']
        users = users_data.get('users', [])
        pagination = users_data.get('pagination', {})
        
        # Populate search form with current values
        search_form.search.data = search
        search_form.role.data = role
        
        return render_template('users/list.html', 
                             users=users, 
                             pagination=pagination,
                             search_form=search_form,
                             current_search=search,
                             current_role=role)
    else:
        flash(f'Lỗi khi tải danh sách người dùng: {response.get("error", "")}', 'error')
        return render_template('users/list.html', 
                             users=[], 
                             pagination={},
                             search_form=search_form)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    form = UserForm(is_create=True)
    
    if form.validate_on_submit():
        user_data = {
            'full_name': form.full_name.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'student_id': form.student_id.data,
            'role_name': form.role_name.data,
            'is_active': form.is_active.data,
            'password': form.password.data
        }
        
        response = user_service.create_user(user_data)
        
        if response['success']:
            flash('Tạo người dùng thành công!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash(f'Lỗi khi tạo người dùng: {response.get("error", "")}', 'error')
    
    return render_template('users/form.html', form=form, title='Tạo người dùng mới', is_create=True)


@users_bp.route('/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    response = user_service.get_user(user_id)
    
    if response['success']:
        user = response['data']['user']
        return render_template('users/view.html', user=user)
    else:
        flash(f'Lỗi khi tải thông tin người dùng: {response.get("error", "")}', 'error')
        return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    # Get user data first
    response = user_service.get_user(user_id)
    
    if not response['success']:
        flash(f'Lỗi khi tải thông tin người dùng: {response.get("error", "")}', 'error')
        return redirect(url_for('users.list_users'))
    
    user = response['data']['user']
    form = UserForm(is_create=False)
    
    if form.validate_on_submit():
        user_data = {
            'full_name': form.full_name.data,
            'phone_number': form.phone_number.data,
            'role_name': form.role_name.data,
            'is_active': form.is_active.data
        }
        
        # Add password if provided
        if form.password.data:
            user_data['password'] = form.password.data
        
        response = user_service.update_user(user_id, user_data)
        
        if response['success']:
            flash('Cập nhật người dùng thành công!', 'success')
            return redirect(url_for('users.view_user', user_id=user_id))
        else:
            flash(f'Lỗi khi cập nhật người dùng: {response.get("error", "")}', 'error')
    
    # Populate form with current user data
    if request.method == 'GET':
        form.full_name.data = user.get('full_name')
        form.email.data = user.get('email')
        form.phone_number.data = user.get('phone_number')
        form.student_id.data = user.get('student_id')
        form.role_name.data = user.get('role')
        form.is_active.data = user.get('is_active')
    
    return render_template('users/form.html', 
                         form=form, 
                         user=user,
                         title='Chỉnh sửa người dùng', 
                         is_create=False)


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    current_user = auth_service.get_current_user()
    
    # Check if trying to delete self
    if current_user and current_user.get('id') == user_id:
        return jsonify({'success': False, 'message': 'Không thể xóa chính mình'}), 400
    
    response = user_service.delete_user(user_id)
    
    if response['success']:
        return jsonify({'success': True, 'message': 'Xóa người dùng thành công'})
    else:
        return jsonify({'success': False, 'message': response.get('error', 'Lỗi không xác định')}), 400
