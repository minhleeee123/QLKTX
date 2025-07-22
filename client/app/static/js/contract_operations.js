// Contract Operations JavaScript

// Global variables
let currentContractId = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for modal cleanup
    const contractDetailModal = document.getElementById('contractDetailModal');
    const contractEditModal = document.getElementById('contractEditModal');
    
    if (contractDetailModal) {
        contractDetailModal.addEventListener('hidden.bs.modal', function() {
            cleanupModal('contractDetailModal');
        });
    }
    
    if (contractEditModal) {
        contractEditModal.addEventListener('hidden.bs.modal', function() {
            cleanupModal('contractEditModal');
        });
    }
});

// Function to clean up modals
function cleanupModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.paddingRight = '';
    }
}

// Function to view contract details
function viewContractDetails(contractId) {
    contractId = parseInt(contractId);
    console.log('viewContractDetails called with contractId:', contractId);
    
    currentContractId = contractId;
    
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
            if (data && data.success && data.contract) {
                displayContractDetails(data.contract);
            } else {
                showContractError(data.message || 'Không thể tải thông tin hợp đồng');
            }
        })
        .catch(error => {
            console.error('Error loading contract details:', error);
            showContractError('Có lỗi xảy ra khi tải thông tin hợp đồng: ' + error.message);
        });
}

// Function to display contract details
function displayContractDetails(contract) {
    // Get the template and replace placeholders
    let template = document.getElementById('contractDetailTemplate').innerHTML;
    
    // Format dates
    const createdAt = contract.created_at ? new Date(contract.created_at).toLocaleString('vi-VN') : 'Chưa có';
    const startDate = contract.start_date || 'Chưa có';
    const endDate = contract.end_date || 'Chưa có';
    
    // Determine status
    const statusInfo = getContractStatusInfo(contract);
    
    // Format currency
    const totalPaid = contract.total_paid ? new Intl.NumberFormat('vi-VN').format(contract.total_paid) : '0';
    const monthlyPrice = contract.room?.price ? new Intl.NumberFormat('vi-VN').format(contract.room.price) : 'N/A';
    
    // Create replacement map
    const replacements = {
        '{{contract_id}}': contract.contract_id || 'N/A',
        '{{contract_code}}': contract.contract_code || 'N/A',
        '{{created_at}}': createdAt,
        '{{start_date}}': startDate,
        '{{end_date}}': endDate,
        '{{duration_months}}': contract.duration_months || 0,
        '{{status_badge_class}}': statusInfo.badgeClass,
        '{{status_text}}': statusInfo.text,
        '{{days_remaining}}': contract.days_remaining || 0,
        '{{days_remaining_class}}': getDaysRemainingClass(contract.days_remaining),
        '{{student_name}}': contract.student?.full_name || 'N/A',
        '{{student_id}}': contract.student?.student_id || 'N/A',
        '{{student_email}}': contract.student?.email || 'N/A',
        '{{student_phone}}': contract.student?.phone_number || 'Chưa có',
        '{{room_number}}': contract.room?.room_number || 'N/A',
        '{{building_name}}': contract.room?.building_name || 'N/A',
        '{{room_type}}': contract.room?.room_type || 'N/A',
        '{{monthly_price}}': monthlyPrice,
        '{{total_paid}}': totalPaid,
        '{{payment_count}}': contract.payment_count || 0,
        '{{pending_payments}}': contract.pending_payments_count || 0
    };
    
    // Replace all placeholders
    Object.keys(replacements).forEach(key => {
        template = template.replaceAll(key, replacements[key]);
    });
    
    // Insert the template
    document.getElementById('contractDetailContent').innerHTML = template;
    
    // Load recent payments if available
    if (contract.payments && contract.payments.length > 0) {
        displayRecentPayments(contract.payments.slice(0, 5)); // Show last 5 payments
    }
}

// Function to get contract status information
function getContractStatusInfo(contract) {
    if (contract.is_expired) {
        return {
            text: 'Đã hết hạn',
            badgeClass: 'bg-danger'
        };
    } else if (contract.is_active) {
        if (contract.days_remaining <= 7) {
            return {
                text: 'Sắp hết hạn',
                badgeClass: 'bg-warning'
            };
        } else {
            return {
                text: 'Đang hiệu lực',
                badgeClass: 'bg-success'
            };
        }
    } else {
        return {
            text: 'Chưa hiệu lực',
            badgeClass: 'bg-secondary'
        };
    }
}

// Function to get days remaining class
function getDaysRemainingClass(daysRemaining) {
    if (daysRemaining <= 7) {
        return 'text-danger fw-bold';
    } else if (daysRemaining <= 30) {
        return 'text-warning fw-bold';
    } else {
        return 'text-success';
    }
}

// Function to display recent payments
function displayRecentPayments(payments) {
    const container = document.getElementById('recentPaymentsList');
    if (!container) return;
    
    if (payments.length === 0) {
        container.innerHTML = '<p class="text-muted mb-0">Chưa có thanh toán nào.</p>';
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    
    payments.forEach(payment => {
        const statusBadge = getPaymentStatusBadge(payment.status);
        const amount = new Intl.NumberFormat('vi-VN').format(payment.amount);
        const date = new Date(payment.payment_date).toLocaleString('vi-VN');
        
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${amount}đ</div>
                    <small class="text-muted">${date} • ${payment.payment_method_display}</small>
                </div>
                <span class="badge ${statusBadge.class}">${statusBadge.text}</span>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Function to get payment status badge
function getPaymentStatusBadge(status) {
    switch (status) {
        case 'confirmed':
            return { class: 'bg-success', text: 'Đã xác nhận' };
        case 'pending':
            return { class: 'bg-warning', text: 'Chờ xác nhận' };
        case 'failed':
            return { class: 'bg-danger', text: 'Thất bại' };
        default:
            return { class: 'bg-secondary', text: status };
    }
}

// Function to show error in contract modal
function showContractError(message) {
    let template = document.getElementById('contractDetailErrorTemplate').innerHTML;
    template = template.replace('{{error_message}}', message);
    document.getElementById('contractDetailContent').innerHTML = template;
}

// Function to edit contract
function editContract(contractId) {
    contractId = parseInt(contractId);
    console.log('editContract called with contractId:', contractId);
    
    currentContractId = contractId;
    
    // Show loading and fetch contract details first
    const modal = new bootstrap.Modal(document.getElementById('contractEditModal'));
    modal.show();
    
    // Show loading state
    const loadingTemplate = document.getElementById('contractDetailLoadingTemplate').innerHTML;
    document.getElementById('contractEditContent').innerHTML = loadingTemplate;
    
    fetch(`/contracts/${contractId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('Contract data for edit:', data);
            if (data && data.success && data.contract) {
                displayContractEditForm(data.contract);
            } else {
                showContractError(data.message || 'Không thể tải thông tin hợp đồng để chỉnh sửa');
            }
        })
        .catch(error => {
            console.error('Error loading contract for edit:', error);
            showContractError('Có lỗi xảy ra khi tải thông tin hợp đồng: ' + error.message);
        });
}

// Function to display contract edit form
function displayContractEditForm(contract) {
    let template = document.getElementById('contractEditTemplate').innerHTML;
    
    const today = new Date().toISOString().split('T')[0];
    
    const replacements = {
        '{{contract_id}}': contract.contract_id,
        '{{contract_code}}': contract.contract_code || '',
        '{{student_name}}': contract.student?.full_name || 'N/A',
        '{{start_date}}': contract.start_date || '',
        '{{end_date}}': contract.end_date || '',
        '{{today}}': today,
        '{{room_number}}': contract.room?.room_number || 'N/A',
        '{{building_name}}': contract.room?.building_name || 'N/A',
        '{{room_type}}': contract.room?.room_type || 'N/A'
    };
    
    // Replace all placeholders
    Object.keys(replacements).forEach(key => {
        template = template.replaceAll(key, replacements[key]);
    });
    
    document.getElementById('contractEditContent').innerHTML = template;
}

// Function to edit contract from detail modal
function editContractFromDetail(contractId) {
    // Close detail modal first
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('contractDetailModal'));
    if (detailModal) {
        detailModal.hide();
    }
    
    // Wait a bit then open edit modal
    setTimeout(() => {
        editContract(contractId);
    }, 300);
}

// Function to save contract changes
function saveContractChanges() {
    const form = document.getElementById('contractEditForm');
    if (!form) return;
    
    const contractId = document.getElementById('contractId').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!endDate) {
        showAlert('Vui lòng chọn ngày kết thúc hợp lệ', 'danger');
        return;
    }
    
    // Validate end date is not in the past
    const today = new Date().toISOString().split('T')[0];
    if (endDate < today) {
        showAlert('Ngày kết thúc không thể trong quá khứ', 'danger');
        return;
    }
    
    // Show loading
    const submitButton = form.querySelector('button[onclick="saveContractChanges()"]');
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Đang lưu...';
    
    const data = {
        end_date: endDate
    };
    
    fetch(`/contracts/${contractId}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Contract update response:', data);
            
            if (data.success) {
                showAlert(data.message || 'Cập nhật hợp đồng thành công', 'success');
                
                // Close modal and reload page
                const modal = bootstrap.Modal.getInstance(document.getElementById('contractEditModal'));
                if (modal) {
                    modal.hide();
                }
                
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showAlert(data.message || 'Có lỗi xảy ra khi cập nhật hợp đồng', 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating contract:', error);
            showAlert('Có lỗi xảy ra khi cập nhật hợp đồng: ' + error.message, 'danger');
        })
        .finally(() => {
            // Restore button
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        });
}

// Function to load statistics
function loadStatistics() {
    const statsSection = document.getElementById('statisticsSection');
    
    if (statsSection.style.display === 'none') {
        fetch('/contracts/statistics', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.statistics) {
                    updateStatistics(data.statistics);
                    statsSection.style.display = 'block';
                } else {
                    showAlert('Không thể tải thống kê', 'danger');
                }
            })
            .catch(error => {
                console.error('Error loading statistics:', error);
                showAlert('Có lỗi xảy ra khi tải thống kê', 'danger');
            });
    } else {
        statsSection.style.display = 'none';
    }
}

// Function to update statistics display
function updateStatistics(stats) {
    document.getElementById('totalContracts').textContent = stats.total_contracts || 0;
    document.getElementById('activeContracts').textContent = stats.active_contracts || 0;
    document.getElementById('expiredContracts').textContent = stats.expired_contracts || 0;
    
    const revenue = stats.total_revenue ? new Intl.NumberFormat('vi-VN').format(stats.total_revenue) : '0';
    document.getElementById('totalRevenue').textContent = revenue + 'đ';
}

// Function to view payments (placeholder)
function viewPayments(contractId) {
    showAlert('Chức năng quản lý thanh toán sẽ được phát triển tiếp', 'info');
}

// Function to view all payments (placeholder)
function viewAllPayments(contractId) {
    viewPayments(contractId);
}

// Function to export contracts (placeholder)
function exportContracts() {
    showAlert('Chức năng xuất Excel sẽ được phát triển tiếp', 'info');
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to document
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
