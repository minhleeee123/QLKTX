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
    
    // Add event listener to cleanup backdrop when modal is hidden
    const modalElement = document.getElementById('userModal');
    modalElement.addEventListener('hidden.bs.modal', function () {
        // Remove any remaining backdrop
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        // Ensure body classes and styles are cleaned up
        document.body.classList.remove('modal-open');
        document.body.style.paddingRight = '';
        document.body.style.overflow = '';
    }, { once: true }); // Use once: true to prevent multiple listeners
    
    modal.show();
    
    // Load user data - call server API 
    fetch(`/users/${userId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) { 
                const user = data.user.user;
                document.getElementById('fullName').value = user.full_name || '';
                document.getElementById('email').value = user.email || '';
                document.getElementById('phoneNumber').value = user.phone_number || '';
                document.getElementById('studentId').value = user.student_id || '';
                document.getElementById('role').value = user.role || '';
                document.getElementById('isActive').value = user.is_active ? 'true' : 'false';
            } else {
                alert('Lỗi: ' + data.message);
                modal.hide();
                // Remove backdrop manually if it exists
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.paddingRight = '';
            }
        })
        .catch(error => {
            alert('Có lỗi xảy ra khi tải thông tin người dùng: ' + error.message);
            modal.hide();
            // Remove backdrop manually if it exists
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
        });
}

// Function to view user details
function viewUserDetails(userId) {
    // Convert string to number if needed
    userId = parseInt(userId);
    
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
            if (data.success) {
                const user = data.user.user;
                
                // Get the template and replace placeholders
                let template = document.getElementById('userDetailTemplate').innerHTML;
                
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
                // Redirect to show Flask flash message
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    location.reload();
                }
            } else {
                // Redirect to show Flask flash message
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    showNotification('Lỗi: ' + data.message, 'danger');
                }
            }
        })
        .catch(error => {
            showNotification('Có lỗi xảy ra: ' + error.message, 'danger');
        });
    }
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
                    showNotification('Mật khẩu xác nhận không khớp!', 'danger');
                    return;
                }
                
                if (userData.password.length < 6) {
                    showNotification('Mật khẩu phải có ít nhất 6 ký tự!', 'danger');
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
            const method = 'POST';
            
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
            .then(response => {
                // Check if response is ok first
                if (!response.ok) {
                    // For non-200 responses, still try to parse JSON for error message
                    return response.json().then(data => {
                        // For errors, show notification but don't redirect - keep modal open
                        throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
                    }).catch(parseError => {
                        // If JSON parsing fails, throw HTTP error
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Close modal and redirect only on success
                    const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
                    modal.hide();
                    
                    // Redirect to show Flask flash message
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        location.reload();
                    }
                } else {
                    // For server validation errors, redirect to show Flask flash message
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        // Keep modal open and show client-side notification for immediate feedback
                        showNotification('Lỗi: ' + data.message, 'danger');
                    }
                }
            })
            .catch(error => {
                // For network/parsing errors, show client-side notification
                showNotification('Có lỗi xảy ra: ' + error.message, 'danger');
            })
            .finally(() => {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }
});
