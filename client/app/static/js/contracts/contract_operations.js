// Contract management JavaScript functions

// Helper function to get status text
function getContractStatusText(status) {
    const statusMap = {
        'active': 'Đang hoạt động',
        'pending': 'Chờ duyệt',
        'expired': 'Hết hạn',
        'terminated': 'Đã chấm dứt',
        'cancelled': 'Đã hủy'
    };
    return statusMap[status] || status;
}

// Helper function to get status badge class
function getContractStatusBadgeClass(status) {
    const statusClassMap = {
        'active': 'bg-success',
        'pending': 'bg-warning',
        'expired': 'bg-danger',
        'terminated': 'bg-secondary',
        'cancelled': 'bg-dark'
    };
    return statusClassMap[status] || 'bg-secondary';
}

// Function to view contract details
function viewContractDetails(contractId) {
    // Convert string to number if needed
    contractId = parseInt(contractId);
    console.log('viewContractDetails called with contractId:', contractId);
    
    // Show the modal first
    const modal = new bootstrap.Modal(document.getElementById('contractDetailModal'));
    modal.show();
    
    // Show loading state
    const loadingTemplate = document.getElementById('contractDetailLoadingTemplate').innerHTML;
    document.getElementById('contractDetailContent').innerHTML = loadingTemplate;
    
    fetch(`/contracts/${contractId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Contract data received:', data);
        if (data.success) {
            const contract = data.contract;
            console.log('Contract data:', contract);
            
            // Get the template and replace placeholders
            let template = document.getElementById('contractDetailTemplate').innerHTML;
            
            // Create a replacement map for easier template handling
            const replacements = {
                '{{contract_id}}': contract.contract_id || 'N/A',
                '{{user_name}}': contract.user?.full_name || 'N/A',
                '{{room_number}}': contract.room?.room_number || 'N/A',
                '{{building_name}}': contract.room?.building?.building_name || 'N/A',
                '{{start_date}}': contract.start_date ? new Date(contract.start_date).toLocaleDateString('vi-VN') : 'N/A',
                '{{end_date}}': contract.end_date ? new Date(contract.end_date).toLocaleDateString('vi-VN') : 'N/A',
                '{{monthly_fee}}': contract.monthly_fee ? new Intl.NumberFormat('vi-VN').format(contract.monthly_fee) + ' VNĐ' : 'N/A',
                '{{deposit}}': contract.deposit ? new Intl.NumberFormat('vi-VN').format(contract.deposit) + ' VNĐ' : 'N/A',
                '{{status_badge_class}}': getContractStatusBadgeClass(contract.status),
                '{{status_text}}': getContractStatusText(contract.status),
                '{{notes}}': contract.notes || 'Không có ghi chú',
                '{{created_at}}': contract.created_at ? new Date(contract.created_at).toLocaleString('vi-VN') : 'Chưa có'
            };
            
            // Replace all placeholders
            Object.keys(replacements).forEach(key => {
                template = template.replaceAll(key, replacements[key]);
            });
            
            document.getElementById('contractDetailContent').innerHTML = template;
        } else {
            // Show error template
            let errorTemplate = document.getElementById('contractDetailErrorTemplate').innerHTML;
            errorTemplate = errorTemplate.replaceAll('{{message}}', data.message);
            document.getElementById('contractDetailContent').innerHTML = errorTemplate;
        }
    })
    .catch(error => {
        console.error('Error fetching contract data:', error);
        // Show error template
        let errorTemplate = document.getElementById('contractDetailErrorTemplate').innerHTML;
        errorTemplate = errorTemplate.replaceAll('{{message}}', 'Có lỗi xảy ra: ' + error.message);
        document.getElementById('contractDetailContent').innerHTML = errorTemplate;
    });
}

// Function to approve contract
function approveContract(contractId) {
    if (confirm('Bạn có chắc chắn muốn duyệt hợp đồng này?')) {
        const formData = new FormData();
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        fetch(`/contracts/${contractId}/approve`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('success', data.message);
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

// Function to terminate contract
function terminateContract(contractId) {
    if (confirm('Bạn có chắc chắn muốn chấm dứt hợp đồng này?')) {
        const formData = new FormData();
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        fetch(`/contracts/${contractId}/terminate`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('success', data.message);
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

// Handle contract form submission
document.addEventListener('DOMContentLoaded', function() {
    const contractForm = document.getElementById('contractForm');
    if (contractForm) {
        contractForm.addEventListener('submit', function(e) {
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
                    // Close modal if exists
                    const modal = bootstrap.Modal.getInstance(document.getElementById('contractModal'));
                    if (modal) {
                        modal.hide();
                    }
                    
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
