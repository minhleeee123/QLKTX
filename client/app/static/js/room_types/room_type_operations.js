// Room Type management JavaScript functions

// Handle room type modal events
document.addEventListener('DOMContentLoaded', function() {
    const roomTypeModal = document.getElementById('roomTypeModal');
    const modalTitle = roomTypeModal.querySelector('.modal-title');
    const roomTypeForm = document.getElementById('roomTypeForm');
    const roomTypeIdInput = document.getElementById('room_type_id');
    const typeNameInput = document.getElementById('type_name');
    const capacityInput = document.getElementById('capacity');
    const priceInput = document.getElementById('price');
    
    // Handle room type modal show event
    roomTypeModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const isEdit = button.classList.contains('edit-room-type');
        
        if (isEdit) {
            const roomTypeId = button.getAttribute('data-id');
            const typeName = button.getAttribute('data-name');
            const capacity = button.getAttribute('data-capacity');
            const price = button.getAttribute('data-price');
            
            modalTitle.textContent = 'Chỉnh sửa loại phòng';
            roomTypeIdInput.value = roomTypeId;
            typeNameInput.value = typeName;
            capacityInput.value = capacity;
            priceInput.value = price;
            roomTypeForm.action = `/room-types/${roomTypeId}/edit`;
        } else {
            modalTitle.textContent = 'Thêm loại phòng mới';
            roomTypeIdInput.value = '';
            typeNameInput.value = '';
            capacityInput.value = '';
            priceInput.value = '';
            roomTypeForm.action = '/room-types/create';
        }
    });
    
    // Handle delete room type modal
    const deleteRoomTypeModal = document.getElementById('deleteRoomTypeModal');
    if (deleteRoomTypeModal) {
        deleteRoomTypeModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const roomTypeId = button.getAttribute('data-id');
            const typeName = button.getAttribute('data-name');
            
            document.getElementById('roomTypeToDelete').textContent = typeName;
            document.getElementById('deleteRoomTypeForm').action = `/room-types/${roomTypeId}/delete`;
        });
    }
    
    // Handle form submission
    if (roomTypeForm) {
        roomTypeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const actionUrl = this.action;
            
            // Disable submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            
            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(roomTypeModal);
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
