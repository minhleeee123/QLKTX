// Room management JavaScript functions
let isEditMode = false;
let currentRoomId = null;

// Function to open create room modal
function openCreateRoomModal() {
    isEditMode = false;
    currentRoomId = null;
    document.getElementById('roomModalLabel').textContent = 'Thêm phòng mới';
    document.getElementById('saveRoomBtn').innerHTML = '<i class="fas fa-save"></i> Lưu';
    document.getElementById('roomForm').reset();
    document.getElementById('roomId').value = '';
    
    clearFormErrors();
    loadBuildingsAndRoomTypes();
}

// Function to open edit room modal
function openEditRoomModal(roomId) {
    // Convert string to number if needed
    roomId = parseInt(roomId);
    
    isEditMode = true;
    currentRoomId = roomId;
    document.getElementById('roomModalLabel').textContent = 'Chỉnh sửa phòng';
    document.getElementById('saveRoomBtn').innerHTML = '<i class="fas fa-save"></i> Cập nhật';
    document.getElementById('roomId').value = roomId;
    
    clearFormErrors();
    loadBuildingsAndRoomTypes();
    
    // Show loading state
    const modal = new bootstrap.Modal(document.getElementById('roomModal'));
    modal.show();
    
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
        if (data.success) {
            const room = data.room;
            console.log('Room data for edit:', room);
            document.getElementById('roomNumber').value = room.room_number || '';
            document.getElementById('buildingId').value = room.building_id || '';
            document.getElementById('roomTypeId').value = room.room_type_id || '';
            document.getElementById('status').value = room.status || 'available';
            document.getElementById('description').value = room.description || '';
        } else {
            showNotification('error', 'Lỗi: ' + data.message);
            modal.hide();
        }
    })
    .catch(error => {
        showNotification('error', 'Có lỗi xảy ra khi tải thông tin phòng: ' + error.message);
        modal.hide();
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
        if (data.success) {
            const room = data.room;
            console.log('Room data:', room);
            
            // Get the template and replace placeholders
            let template = document.getElementById('roomDetailTemplate').innerHTML;
            
            // Create a replacement map for easier template handling
            const replacements = {
                '{{room_id}}': room.room_id || 'N/A',
                '{{room_number}}': room.room_number || 'N/A',
                '{{building_name}}': room.building?.building_name || 'N/A',
                '{{room_type_name}}': room.room_type?.type_name || 'N/A',
                '{{capacity}}': room.room_type?.capacity || 'N/A',
                '{{monthly_price}}': room.room_type?.price ? new Intl.NumberFormat('vi-VN').format(room.room_type.price) : 'N/A',
                '{{status_badge_class}}': getStatusBadgeClass(room.status),
                '{{status_text}}': getStatusText(room.status),
                '{{description}}': room.description || 'Không có mô tả',
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
            errorTemplate = errorTemplate.replaceAll('{{message}}', data.message);
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

// Function to open delete room modal
function openDeleteRoomModal(button) {
    const roomId = button.getAttribute('data-room-id');
    const roomNumber = button.getAttribute('data-room-number');
    
    document.getElementById('roomToDelete').textContent = roomNumber;
    document.getElementById('deleteRoomForm').action = `/rooms/${roomId}/delete`;
}

// Load buildings and room types for dropdowns
function loadBuildingsAndRoomTypes() {
    // Load buildings
    fetch('/api/buildings', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const buildingSelect = document.getElementById('buildingId');
            buildingSelect.innerHTML = '<option value="">Chọn tòa nhà</option>';
            
            data.buildings.forEach(building => {
                const option = document.createElement('option');
                option.value = building.building_id;
                option.textContent = building.building_name;
                buildingSelect.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Error loading buildings:', error);
    });
    
    // Load room types
    fetch('/api/room-types', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const roomTypeSelect = document.getElementById('roomTypeId');
            roomTypeSelect.innerHTML = '<option value="">Chọn loại phòng</option>';
            
            data.room_types.forEach(roomType => {
                const option = document.createElement('option');
                option.value = roomType.room_type_id;
                option.textContent = `${roomType.type_name} (${roomType.capacity} người)`;
                roomTypeSelect.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Error loading room types:', error);
    });
}

// Helper function to get status text
function getStatusText(status) {
    const statusMap = {
        'available': 'Có sẵn',
        'occupied': 'Đã có người ở',
        'pending_approval': 'Chờ duyệt',
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
        'pending_approval': 'bg-warning',
        'maintenance': 'bg-secondary',
        'unavailable': 'bg-dark'
    };
    return statusClassMap[status] || 'bg-secondary';
}

// Clear form errors
function clearFormErrors() {
    const errorElements = document.querySelectorAll('.text-danger.small');
    errorElements.forEach(element => {
        element.textContent = '';
    });
}

// Display form errors
function displayFormErrors(errors) {
    clearFormErrors();
    
    for (const [field, message] of Object.entries(errors)) {
        const errorElement = document.getElementById(field + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }
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
            
            // Create FormData object for submission
            const submitFormData = new FormData();
            
            // Add CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                             document.querySelector('input[name="csrf_token"]')?.value || '';
            if (csrfToken) {
                submitFormData.append('csrf_token', csrfToken);
            }
            
            // Add room data to form
            Object.keys(roomData).forEach(key => {
                if (roomData[key] !== null && roomData[key] !== undefined && key !== 'csrf_token') {
                    submitFormData.append(key, roomData[key]);
                }
            });
            
            const url = isEditMode ? `/rooms/${currentRoomId}/edit` : '/rooms/create';
            const method = 'POST';
            
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
                    // Show errors
                    if (data.errors) {
                        displayFormErrors(data.errors);
                    } else {
                        showNotification('error', 'Lỗi: ' + data.message);
                    }
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
