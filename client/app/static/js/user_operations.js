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
    fetch(`/users/${userId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
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
    console.log('viewUserDetails called with userId:', userId);
    
    // Show the modal first
    const modal = new bootstrap.Modal(document.getElementById('userDetailModal'));
    modal.show();
    
    // Show loading state
    const loadingTemplate = document.getElementById('userDetailLoadingTemplate').innerHTML;
    document.getElementById('userDetailContent').innerHTML = loadingTemplate;
    
    fetch(`/users/${userId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('User data received:', data);
            if (data.success) {
                const user = data.user;
                
                // Get the template and replace placeholders
                let template = document.getElementById('userDetailTemplate').innerHTML;
                console.log('User detail template:', template);
                
                // Create a replacement map for easier template handling
                const replacements = {
                    '{{user_id}}': user.user_id || 'N/A',
                    '{{full_name}}': user.full_name || 'N/A',
                    '{{email}}': user.email || 'N/A',
                    '{{phone_number}}': user.phone_number || 'Chưa có',
                    '{{student_id}}': user.student_id || 'Chưa có',
                    '{{role_badge_class}}': getRoleBadgeClass(user.role),
                    '{{role_text}}': getRoleText(user.role),
                    '{{status_badge_class}}': user.is_active ? 'bg-success' : 'bg-secondary',
                    '{{status_text}}': user.is_active ? 'Hoạt động' : 'Không hoạt động',
                    '{{created_at}}': user.created_at ? new Date(user.created_at).toLocaleString('vi-VN') : 'Chưa có'
                };
                
                // Replace all placeholders
                Object.keys(replacements).forEach(key => {
                    template = template.replaceAll(key, replacements[key]);
                });
                
                document.getElementById('userDetailContent').innerHTML = template;
            } else {
                // Show error template
                let errorTemplate = document.getElementById('userDetailErrorTemplate').innerHTML;
                errorTemplate = errorTemplate.replaceAll('{{message}}', data.message);
                document.getElementById('userDetailContent').innerHTML = errorTemplate;
            }
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            // Show error template
            let errorTemplate = document.getElementById('userDetailErrorTemplate').innerHTML;
            errorTemplate = errorTemplate.replaceAll('{{message}}', 'Có lỗi xảy ra: ' + error.message);
            document.getElementById('userDetailContent').innerHTML = errorTemplate;
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
        // Create FormData with CSRF token
        const formData = new FormData();
        const csrfToken = document.getElementById('csrfToken')?.value || 
                         document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        fetch(`/users/${userId}/delete`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
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
            
            // Create FormData object
            const submitFormData = new FormData();
            
            // Add CSRF token from the hidden input in the form
            const csrfToken = document.getElementById('csrfToken')?.value || 
                             document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
            if (csrfToken) {
                submitFormData.append('csrf_token', csrfToken);
            }
            
            // Add user data to form
            Object.keys(userData).forEach(key => {
                if (userData[key] !== null && userData[key] !== undefined) {
                    submitFormData.append(key, userData[key]);
                }
            });
            
            const url = isEditMode ? `/users/${currentUserId}/edit` : '/users/create';
            const method = 'POST'; // Always use POST for form submission
            
            // Disable submit button
            const submitBtn = document.getElementById('saveUserBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            
            fetch(url, {
                method: method,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: submitFormData
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
