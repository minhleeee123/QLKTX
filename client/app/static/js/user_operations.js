// User management JavaScript functions
let isEditMode = false;
let currentUserId = null;

// Function to open create user modal
function openCreateUserModal() {
    isEditMode = false;
    currentUserId = null;
    document.getElementById('userModalLabel').textContent = 'Thêm người dùng';
    document.getElementById('saveUserBtn').innerHTML = '<i class="fas fa-save"></i> Lưu';
    document.getElementById('userForm').reset();
    document.getElementById('passwordSection').style.display = 'block';
    document.getElementById('password').required = true;
    document.getElementById('confirmPassword').required = true;
}

// Function to open edit user modal
function openEditUserModal(userId) {
    // Convert string to number if needed
    userId = parseInt(userId);
    
    isEditMode = true;
    currentUserId = userId;
    document.getElementById('userModalLabel').textContent = 'Chỉnh sửa người dùng';
    document.getElementById('saveUserBtn').innerHTML = '<i class="fas fa-save"></i> Cập nhật';
    document.getElementById('passwordSection').style.display = 'none';
    document.getElementById('password').required = false;
    document.getElementById('confirmPassword').required = false;
    
    // Show loading state
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
    
    // Load user data
    fetch(`/users/api/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const user = data.user;
                document.getElementById('fullName').value = user.full_name || '';
                document.getElementById('email').value = user.email || '';
                document.getElementById('phoneNumber').value = user.phone_number || '';
                document.getElementById('studentId').value = user.student_id || '';
                document.getElementById('role').value = user.role || '';
                document.getElementById('isActive').value = user.is_active ? 'true' : 'false';
            } else {
                alert('Lỗi: ' + data.message);
                modal.hide();
            }
        })
        .catch(error => {
            alert('Có lỗi xảy ra khi tải thông tin người dùng: ' + error.message);
            modal.hide();
        });
}

// Function to view user details
function viewUserDetails(userId) {
    // Convert string to number if needed
    userId = parseInt(userId);
    
    // Show loading state
    document.getElementById('userDetailContent').innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
        </div>
    `;
    
    fetch(`/users/api/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const user = data.user;
                const content = `
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <strong>ID:</strong> 
                                <span class="text-muted">${user.user_id}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Họ và tên:</strong> 
                                <span class="text-muted">${user.full_name}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Email:</strong> 
                                <span class="text-muted">${user.email}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Số điện thoại:</strong> 
                                <span class="text-muted">${user.phone_number || 'Chưa có'}</span>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <strong>Mã sinh viên:</strong> 
                                <span class="text-muted">${user.student_id || 'Chưa có'}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Vai trò:</strong> 
                                <span class="badge ${getRoleBadgeClass(user.role)}">${getRoleText(user.role)}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Trạng thái:</strong> 
                                <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">${user.is_active ? 'Hoạt động' : 'Không hoạt động'}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Ngày tạo:</strong> 
                                <span class="text-muted">${user.created_at ? new Date(user.created_at).toLocaleString('vi-VN') : 'Chưa có'}</span>
                            </div>
                        </div>
                    </div>
                `;
                document.getElementById('userDetailContent').innerHTML = content;
            } else {
                document.getElementById('userDetailContent').innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle"></i> ${data.message}
                    </div>
                `;
            }
        })
        .catch(error => {
            document.getElementById('userDetailContent').innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i> Có lỗi xảy ra: ${error.message}
                </div>
            `;
        });
}

// Helper function to get role text
function getRoleText(role) {
    const roleMap = {
        'admin': 'Quản trị viên',
        'management': 'Quản lý', 
        'student': 'Sinh viên',
        'staff': 'Nhân viên'
    };
    return roleMap[role] || role;
}

// Helper function to get role badge class
function getRoleBadgeClass(role) {
    const roleClassMap = {
        'admin': 'bg-danger',
        'management': 'bg-warning text-dark',
        'student': 'bg-primary',
        'staff': 'bg-info text-dark'
    };
    return roleClassMap[role] || 'bg-secondary';
}

// Delete user function
function deleteUser(userId, userName) {
    // Convert string to number if needed
    userId = parseInt(userId);
    
    if (confirm(`Bạn có chắc chắn muốn xóa người dùng "${userName}"?`)) {
        fetch(`/users/api/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || ''
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                showNotification('success', data.message);
                // Reload page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showNotification('error', 'Lỗi: ' + data.message);
            }
        })
        .catch(error => {
            showNotification('error', 'Có lỗi xảy ra: ' + error.message);
        });
    }
}

// Function to show notifications
function showNotification(type, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1055; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Handle form submission when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const userForm = document.getElementById('userForm');
    if (userForm) {
        userForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const userData = {};
            
            for (let [key, value] of formData.entries()) {
                userData[key] = value;
            }
            
            // Convert is_active to boolean
            userData.is_active = userData.is_active === 'true';
            
            // Validate passwords for create mode
            if (!isEditMode) {
                if (userData.password !== userData.confirm_password) {
                    showNotification('error', 'Mật khẩu xác nhận không khớp!');
                    return;
                }
                
                if (userData.password.length < 6) {
                    showNotification('error', 'Mật khẩu phải có ít nhất 6 ký tự!');
                    return;
                }
            }
            
            // Remove confirm_password from data
            delete userData.confirm_password;
            
            const url = isEditMode ? `/users/api/${currentUserId}` : '/users/api';
            const method = isEditMode ? 'PUT' : 'POST';
            
            // Disable submit button
            const submitBtn = document.getElementById('saveUserBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || ''
                },
                body: JSON.stringify(userData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
                    modal.hide();
                    
                    // Show success message
                    showNotification('success', data.message);
                    
                    // Reload page after a short delay
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    showNotification('error', 'Lỗi: ' + data.message);
                }
            })
            .catch(error => {
                showNotification('error', 'Có lỗi xảy ra: ' + error.message);
            })
            .finally(() => {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }
});
