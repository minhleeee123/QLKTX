/**
 * Registration Management JavaScript
 * Handles approve/reject actions for admin registration management
 */

let selectedRegistrationId = null;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    initializeRegistrationManagement();
});

function initializeRegistrationManagement() {
    console.log("Initializing registration management...");
    
    // Initialize modals
    const approveModal = document.getElementById("approveModal");
    const rejectModal = document.getElementById("rejectModal");

    // Set up confirm approve handler
    const confirmApproveBtn = document.getElementById("confirmApproveBtn");
    if (confirmApproveBtn) {
        confirmApproveBtn.addEventListener("click", confirmApproveRegistration);
        console.log("Confirm approve button handler attached");
    }

    // Set up confirm reject handler
    const confirmRejectBtn = document.getElementById("confirmRejectBtn");
    if (confirmRejectBtn) {
        confirmRejectBtn.addEventListener("click", confirmRejectRegistration);
        console.log("Confirm reject button handler attached");
    }

    // Set up event delegation for approve/reject buttons
    document.addEventListener("click", function(event) {
        const button = event.target.closest("[data-action]");
        if (!button) return;

        event.preventDefault();
        
        const action = button.getAttribute("data-action");
        const registrationId = parseInt(button.getAttribute("data-registration-id"));
        const studentName = button.getAttribute("data-student-name");
        const roomNumber = button.getAttribute("data-room-number");
        
        console.log("Button clicked:", action, registrationId, studentName, roomNumber);
        
        switch(action) {
            case "approve":
                showApproveModal(registrationId, studentName, roomNumber);
                break;
            case "reject":
                showRejectModal(registrationId, studentName, roomNumber);
                break;
            default:
                console.warn("Unknown action:", action);
        }
    });

    console.log("Registration management initialized successfully");
}

/**
 * Show approve confirmation modal
 */
function showApproveModal(registrationId, studentName, roomNumber) {
    console.log("Showing approve modal for registration:", registrationId);
    
    selectedRegistrationId = registrationId;
    
    // Update modal content
    document.getElementById("approveStudentName").textContent = studentName;
    document.getElementById("approveRoomNumber").textContent = roomNumber;
    
    // Show modal
    const modalElement = document.getElementById("approveModal");
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        console.log("Approve modal shown");
    }
}

/**
 * Show reject confirmation modal
 */
function showRejectModal(registrationId, studentName, roomNumber) {
    console.log("Showing reject modal for registration:", registrationId);
    
    selectedRegistrationId = registrationId;
    
    // Update modal content
    document.getElementById("rejectStudentName").textContent = studentName;
    document.getElementById("rejectRoomNumber").textContent = roomNumber;
    
    // Show modal
    const modalElement = document.getElementById("rejectModal");
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        console.log("Reject modal shown");
    }
}

/**
 * Confirm approve registration
 */
async function confirmApproveRegistration() {
    if (!selectedRegistrationId) {
        showNotification("error", "Không tìm thấy thông tin đăng ký");
        return;
    }

    console.log("Confirming approval for registration:", selectedRegistrationId);
    
    const confirmBtn = document.getElementById("confirmApproveBtn");
    const originalText = confirmBtn.innerHTML;

    try {
        // Set loading state
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        // Prepare request data with CSRF token
        const formData = new FormData();
        
        // Add CSRF token if CSRFUtils is available
        if (typeof CSRFUtils !== 'undefined') {
            const token = CSRFUtils.getToken();
            if (token) {
                formData.append('csrf_token', token);
                console.log("CSRF token added to approve request");
            }
        }

        // Make approve request
        const response = await fetch(`/registrations/${selectedRegistrationId}/approve`, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        console.log("Approve response status:", response.status);
        
        const data = await response.json();
        console.log("Approve response data:", data);

        if (response.ok && data.success) {
            // Hide modal
            const modalElement = document.getElementById("approveModal");
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }

            // Show success message
            showNotification("success", data.message || "Duyệt đơn thành công!");

            // Reload page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification("error", data.message || "Có lỗi xảy ra khi duyệt đơn");
        }
    } catch (error) {
        console.error("Approve error:", error);
        showNotification("error", "Lỗi kết nối. Vui lòng thử lại.");
    } finally {
        // Reset button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
        selectedRegistrationId = null;
    }
}

/**
 * Confirm reject registration
 */
async function confirmRejectRegistration() {
    if (!selectedRegistrationId) {
        showNotification("error", "Không tìm thấy thông tin đăng ký");
        return;
    }

    console.log("Confirming rejection for registration:", selectedRegistrationId);
    
    const confirmBtn = document.getElementById("confirmRejectBtn");
    const originalText = confirmBtn.innerHTML;

    try {
        // Set loading state
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        // Prepare request data with CSRF token
        const formData = new FormData();
        
        // Add CSRF token if CSRFUtils is available
        if (typeof CSRFUtils !== 'undefined') {
            const token = CSRFUtils.getToken();
            if (token) {
                formData.append('csrf_token', token);
                console.log("CSRF token added to reject request");
            }
        }

        // Make reject request
        const response = await fetch(`/registrations/${selectedRegistrationId}/reject`, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        console.log("Reject response status:", response.status);
        
        const data = await response.json();
        console.log("Reject response data:", data);

        if (response.ok && data.success) {
            // Hide modal
            const modalElement = document.getElementById("rejectModal");
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }

            // Show success message
            showNotification("success", data.message || "Từ chối đơn thành công!");

            // Reload page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification("error", data.message || "Có lỗi xảy ra khi từ chối đơn");
        }
    } catch (error) {
        console.error("Reject error:", error);
        showNotification("error", "Lỗi kết nối. Vui lòng thử lại.");
    } finally {
        // Reset button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
        selectedRegistrationId = null;
    }
}

/**
 * Show notification (using global notification system)
 */
function showNotification(type, message) {
    // Use the global notification system if available (from notifications.js)
    if (typeof window.showNotification === "function" && window.showNotification !== showNotification) {
        window.showNotification(type, message);
        return;
    }

    // Fallback notification
    const alertClass = type === "success" ? "alert-success" : "alert-danger";
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.insertAdjacentHTML("beforeend", alertHTML);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector(".alert");
        if (alert) {
            alert.remove();
        }
    }, 5000);
}
