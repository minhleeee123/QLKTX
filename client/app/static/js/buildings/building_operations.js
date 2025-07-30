// Building management JavaScript functions

// Handle building modal events
document.addEventListener('DOMContentLoaded', function() {
    const buildingModal = document.getElementById('buildingModal');
    const modalTitle = buildingModal.querySelector('.modal-title');
    const buildingForm = document.getElementById('buildingForm');
    const buildingIdInput = document.getElementById('building_id');
    const buildingNameInput = document.getElementById('building_name');
    
    // Handle building modal show event
    buildingModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const isEdit = button.classList.contains('edit-building');
        
        if (isEdit) {
            const buildingId = button.getAttribute('data-id');
            const buildingName = button.getAttribute('data-name');
            
            modalTitle.textContent = 'Chỉnh sửa tòa nhà';
            buildingIdInput.value = buildingId;
            buildingNameInput.value = buildingName;
            buildingForm.action = `/buildings/${buildingId}/edit`;
        } else {
            modalTitle.textContent = 'Thêm tòa nhà mới';
            buildingIdInput.value = '';
            buildingNameInput.value = '';
            buildingForm.action = '/buildings/create';
        }
    });
    
    // Handle delete building modal
    const deleteBuildingModal = document.getElementById('deleteBuildingModal');
    if (deleteBuildingModal) {
        deleteBuildingModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const buildingId = button.getAttribute('data-id');
            const buildingName = button.getAttribute('data-name');
            
            document.getElementById('buildingToDelete').textContent = buildingName;
            document.getElementById('deleteBuildingForm').action = `/buildings/${buildingId}/delete`;
        });
    }
    
    // Handle form submission
    if (buildingForm) {
        buildingForm.addEventListener('submit', function(e) {
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
                    const modal = bootstrap.Modal.getInstance(buildingModal);
                    modal.hide();
                    
                    // Show success message
                    showNotification("success", data.message);
                    
                    // Reload page after a short delay
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    showNotification("error", "Lỗi: " + data.message);
                }
            })
            .catch(error => {
                showNotification("error", "Có lỗi xảy ra: " + error.message);
            })
            .finally(() => {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }
});
