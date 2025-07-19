// Room management JavaScript functions
let isEditMode = false;
let currentRoomId = null;

// Function to open create room modal
function openCreateRoomModal() {
    isEditMode = false;
    currentRoomId = null;
    document.getElementById('roomModalLabel').textContent = 'Thêm phòng';
    document.getElementById('saveRoomBtn').innerHTML = '<i class="fas fa-save"></i> Lưu';
    document.getElementById('roomForm').reset();
    
    // Load building and room type options
    loadBuildingOptions();
    loadRoomTypeOptions();
}

// Function to open edit room modal
function openEditRoomModal(roomId) {
    // Convert string to number if needed
    roomId = parseInt(roomId);
    
    isEditMode = true;
    currentRoomId = roomId;
    document.getElementById('roomModalLabel').textContent = 'Chỉnh sửa phòng';
    document.getElementById('saveRoomBtn').innerHTML = '<i class="fas fa-save"></i> Cập nhật';
    
    // Show loading state
    const modal = new bootstrap.Modal(document.getElementById('roomModal'));
    
    // Add event listener to cleanup backdrop when modal is hidden
    const modalElement = document.getElementById('roomModal');
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
    
    // Load building and room type options first
    Promise.all([loadBuildingOptions(), loadRoomTypeOptions()])
        .then(() => {
            // Load room data
            fetch(`/rooms/${roomId}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Edit room data received:', data);
                    if (data && data.success && data.room) { 
                        const room = data.room;
                        console.log('Room data for edit:', room);
                        document.getElementById('roomNumber').value = room.room_number || '';
                        document.getElementById('buildingId').value = room.building?.building_id || room.building_id || '';
                        document.getElementById('roomTypeId').value = room.room_type?.room_type_id || room.room_type_id || '';
                        document.getElementById('capacity').value = room.room_type?.capacity || room.capacity || '';
                        document.getElementById('monthlyPrice').value = room.room_type?.price || room.monthly_price || '';
                        document.getElementById('status').value = room.status || '';
                        document.getElementById('description').value = room.description || '';
                    } else {
                        const errorMessage = data && data.message ? data.message : 'Không thể tải thông tin phòng';
                        alert('Lỗi: ' + errorMessage);
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
                    alert('Có lỗi xảy ra khi tải thông tin phòng: ' + error.message);
                    modal.hide();
                    // Remove backdrop manually if it exists
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    document.body.classList.remove('modal-open');
                    document.body.style.paddingRight = '';
                });
        });
}

// Function to view room details
function viewRoomDetails(roomId) {
    // Convert string to number if needed
    roomId = parseInt(roomId);
    console.log('viewRoomDetails called with roomId:', roomId);
    
    // Show the modal first
    const modal = new bootstrap.Modal(document.getElementById('roomDetailModal'));
    modal.show();
    
    // Show loading state
    const loadingTemplate = document.getElementById('roomDetailLoadingTemplate').innerHTML;
    document.getElementById('roomDetailContent').innerHTML = loadingTemplate;
    
    fetch(`/rooms/${roomId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('Room data received:', data);
            if (data && data.success && data.room) {
                const room = data.room;
                console.log('Room data:', room);
                
                // Get the template and replace placeholders
                let template = document.getElementById('roomDetailTemplate').innerHTML;
                
                // Create a replacement map for easier template handling
                const replacements = {
                    '{{room_id}}': room.room_id || 'N/A',
                    '{{room_number}}': room.room_number || 'N/A',
                    '{{building_name}}': room.building?.building_name || room.building_name || 'N/A',
                    '{{room_type_name}}': room.room_type?.type_name || room.room_type_name || 'N/A',
                    '{{capacity}}': room.room_type?.capacity || room.capacity || 'N/A',
                    '{{monthly_price}}': room.room_type?.price ? new Intl.NumberFormat('vi-VN').format(room.room_type.price) : 
                                       (room.monthly_price ? new Intl.NumberFormat('vi-VN').format(room.monthly_price) : 'N/A'),
                    '{{status_badge_class}}': getStatusBadgeClass(room.status),
                    '{{status_text}}': getStatusText(room.status),
                    '{{description}}': room.description || 'Chưa có mô tả',
                    '{{created_at}}': room.created_at ? new Date(room.created_at).toLocaleString('vi-VN') : 'Chưa có'
                };
                
                // Replace all placeholders
                Object.keys(replacements).forEach(key => {
                    template = template.replaceAll(key, replacements[key]);
                });
                
                document.getElementById('roomDetailContent').innerHTML = template;
            } else {
                // Show error template
                let errorTemplate = document.getElementById('roomDetailErrorTemplate').innerHTML;
                const errorMessage = data && data.message ? data.message : 'Không thể tải thông tin phòng';
                errorTemplate = errorTemplate.replaceAll('{{message}}', errorMessage);
                document.getElementById('roomDetailContent').innerHTML = errorTemplate;
            }
        })
        .catch(error => {
            console.error('Error fetching room data:', error);
            // Show error template
            let errorTemplate = document.getElementById('roomDetailErrorTemplate').innerHTML;
            errorTemplate = errorTemplate.replaceAll('{{message}}', 'Có lỗi xảy ra: ' + error.message);
            document.getElementById('roomDetailContent').innerHTML = errorTemplate;
        });
}

// Helper function to get status text
function getStatusText(status) {
    const statusMap = {
        'available': 'Có sẵn',
        'occupied': 'Đã thuê', 
        'maintenance': 'Bảo trì',
        'unavailable': 'Không khả dụng'
    };
    return statusMap[status] || status;
}

// Helper function to get status badge class
function getStatusBadgeClass(status) {
    const statusClassMap = {
        'available': 'bg-success',
        'occupied': 'bg-danger',
        'maintenance': 'bg-warning text-dark',
        'unavailable': 'bg-secondary'
    };
    return statusClassMap[status] || 'bg-secondary';
}

// Load building options
function loadBuildingOptions() {
    return fetch('/rooms/buildings', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('buildingId');
            select.innerHTML = '<option value="">Chọn tòa nhà</option>';
            
            if (data.success && data.buildings) {
                data.buildings.forEach(building => {
                    const option = document.createElement('option');
                    option.value = building.building_id;
                    option.textContent = building.building_name;
                    select.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error loading buildings:', error));
}

// Load room type options
function loadRoomTypeOptions() {
    return fetch('/rooms/room-types', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('roomTypeId');
            select.innerHTML = '<option value="">Chọn loại phòng</option>';
            
            if (data.success && data.room_types) {
                data.room_types.forEach(roomType => {
                    const option = document.createElement('option');
                    option.value = roomType.room_type_id;
                    option.textContent = roomType.type_name;
                    select.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error loading room types:', error));
}

// Delete room function
function deleteRoom(roomId, roomNumber) {
    // Convert string to number if needed
    roomId = parseInt(roomId);
    
    if (confirm(`Bạn có chắc chắn muốn xóa phòng "${roomNumber}"?`)) {
        // Create FormData with CSRF token
        const formData = new FormData();
        const csrfToken = document.getElementById('csrfToken')?.value || 
                         document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        fetch(`/rooms/${roomId}/delete`, {
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
    const roomForm = document.getElementById('roomForm');
    if (roomForm) {
        roomForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const roomData = {};
            
            for (let [key, value] of formData.entries()) {
                roomData[key] = value;
            }
            
            // Convert numeric fields
            roomData.capacity = parseInt(roomData.capacity);
            roomData.monthly_price = parseFloat(roomData.monthly_price);
            roomData.building_id = parseInt(roomData.building_id);
            roomData.room_type_id = parseInt(roomData.room_type_id);

            // Basic validation
            const errors = [];
            if (!roomData.room_number) {
                errors.push("Số phòng là bắt buộc");
            }
            if (!roomData.building_id || isNaN(roomData.building_id)) {
                errors.push("Tòa nhà là bắt buộc");
            }
            if (!roomData.room_type_id || isNaN(roomData.room_type_id)) {
                errors.push("Loại phòng là bắt buộc");
            }
            if (!roomData.capacity || isNaN(roomData.capacity) || roomData.capacity < 1) {
                errors.push("Sức chứa phải là số nguyên dương");
            }
            if (!roomData.monthly_price || isNaN(roomData.monthly_price) || roomData.monthly_price < 0) {
                errors.push("Giá hàng tháng phải là số không âm");
            }

            if (errors.length > 0) {
                showNotification('error', errors.join('; '));
                return;
            }
            
            // Create FormData object
            const submitFormData = new FormData();
            
            // Add CSRF token from the hidden input in the form
            const csrfToken = document.getElementById('csrfToken')?.value || 
                             document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
            if (csrfToken) {
                submitFormData.append('csrf_token', csrfToken);
            }
            
            // Add room data to form
            Object.keys(roomData).forEach(key => {
                if (roomData[key] !== null && roomData[key] !== undefined && roomData[key] !== '') {
                    submitFormData.append(key, roomData[key]);
                }
            });
            
            const url = isEditMode ? `/rooms/${currentRoomId}/edit` : '/rooms/create';
            const method = 'POST'; // Always use POST for form submission
            
            // Disable submit button
            const submitBtn = document.getElementById('saveRoomBtn');
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
                    const modal = bootstrap.Modal.getInstance(document.getElementById('roomModal'));
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
