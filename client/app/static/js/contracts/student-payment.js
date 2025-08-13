/**
 * Student Contract Payment Handler
 * Handles payment modal and processing for student contracts
 */

let currentContractId = null;
let currentPaymentButton = null;

// Use event delegation for payment buttons
document.addEventListener('DOMContentLoaded', function () {
    // Handle payment button clicks
    document.addEventListener('click', function (e) {
        if (e.target.closest('.payment-btn')) {
            const button = e.target.closest('.payment-btn');
            const contractId = button.getAttribute('data-contract-id');
            showPaymentModal(contractId, button);
        }
    });

    // Handle modal confirmation
    const confirmPaymentBtn = document.getElementById('confirmPaymentBtn');
    if (confirmPaymentBtn) {
        confirmPaymentBtn.addEventListener('click', function () {
            if (currentContractId && currentPaymentButton) {
                processPayment(currentContractId, currentPaymentButton);
            }
        });
    }
});

function showPaymentModal(contractId, button) {
    currentContractId = contractId;
    currentPaymentButton = button;

    // Show the modal
    const modalElement = document.getElementById('paymentModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
}

function processPayment(contractId, button) {
    // Hide the modal first
    const modalElement = document.getElementById('paymentModal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }

    // Show loading state on the button
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i><br>Đang xử lý...';
    button.disabled = true;

    // Show loading state on modal confirm button
    const confirmBtn = document.getElementById('confirmPaymentBtn');
    let originalConfirmText = '';
    if (confirmBtn) {
        originalConfirmText = confirmBtn.innerHTML;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
        confirmBtn.disabled = true;
    }

    console.log("Trying to pay contract ", contractId);

    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Make API call to pay contract - use client endpoint
    fetch(`/contracts/${contractId}/pay`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // If not JSON, get text to see what we received
                return response.text().then(text => {
                    console.error('Received non-JSON response:', text);
                    throw new Error(`Server returned ${response.status}: ${text.substring(0, 200)}`);
                });
            }
            
            return response.json();
        })
        .then(data => {
            console.log('Payment response:', data);
            
            if (data.success) {
                // Show success notification
                showSuccessNotification('Thanh toán thành công!');

                // Reload page after a short delay to show the success message
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showErrorNotification('Có lỗi xảy ra: ' + (data.message || 'Vui lòng thử lại'));

                // Restore button states
                button.innerHTML = originalText;
                button.disabled = false;
                if (confirmBtn) {
                    confirmBtn.innerHTML = originalConfirmText;
                    confirmBtn.disabled = false;
                }
            }
        })
        .catch(error => {
            console.error('Payment error:', error);
            showErrorNotification('Có lỗi xảy ra khi thanh toán: ' + error.message);

            // Restore button states
            button.innerHTML = originalText;
            button.disabled = false;
            if (confirmBtn) {
                confirmBtn.innerHTML = originalConfirmText;
                confirmBtn.disabled = false;
            }
        });

    // Reset current values
    currentContractId = null;
    currentPaymentButton = null;
}

function showSuccessNotification(message) {
    // Create a temporary success notification
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function showErrorNotification(message) {
    // Create a temporary error notification
    const notification = document.createElement('div');
    notification.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${message}
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
