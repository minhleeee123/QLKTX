/**
 * Registrations Management JavaScript for Student Interface
 * Handles registration cancellation and status management
 */

let selectedRegistrationId = null;
let selectedRoomNumber = null;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    initializeRegistrations();
});

function initializeRegistrations() {
    // Initialize cancel modal
    const cancelModal = document.getElementById("cancelModal");

    // Set up event delegation for registration cards
    document.addEventListener("click", function (e) {
        if (e.target.closest('[data-action="cancel-registration"]')) {
            const button = e.target.closest('[data-action="cancel-registration"]');
            const registrationId = button.dataset.registrationId;
            const roomNumber = button.dataset.roomNumber;
            
            if (registrationId && roomNumber) {
                cancelRegistration(registrationId, roomNumber);
            }
        }
    });

    // Set up confirm cancellation handler
    const confirmCancelBtn = document.getElementById("confirmCancelBtn");
    if (confirmCancelBtn) {
        confirmCancelBtn.addEventListener("click", confirmCancellation);
    }

    // Handle modal cleanup
    if (cancelModal) {
        cancelModal.addEventListener("hidden.bs.modal", function () {
            selectedRegistrationId = null;
            selectedRoomNumber = null;
        });
    }

    console.log("Registrations manager initialized");
}

/**
 * Show cancellation confirmation modal
 */
function cancelRegistration(registrationId, roomNumber) {
    selectedRegistrationId = registrationId;
    selectedRoomNumber = roomNumber;

    // Update modal content
    const roomNumberElement = document.getElementById("roomNumberToCancel");
    if (roomNumberElement) {
        roomNumberElement.textContent = roomNumber;
    }

    // Show modal
    const cancelModal = new bootstrap.Modal(document.getElementById("cancelModal"));
    cancelModal.show();
}

/**
 * Confirm and submit registration cancellation
 */
async function confirmCancellation() {
    if (!selectedRegistrationId) {
        showNotification("error", "Không tìm thấy thông tin đăng ký");
        return;
    }

    const confirmBtn = document.getElementById("confirmCancelBtn");
    const originalText = confirmBtn.innerHTML;

    try {
        // Set loading state
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        // Make cancellation request
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        const response = await fetch(`/student/registrations/${selectedRegistrationId}/cancel`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
            },
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Hide modal
            const cancelModal = bootstrap.Modal.getInstance(
                document.getElementById("cancelModal")
            );
            cancelModal.hide();

            // Show success message
            showNotification("success", data.message);

            // Reload page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification("error", data.message || "Có lỗi xảy ra khi hủy đăng ký");
        }
    } catch (error) {
        console.error("Cancellation error:", error);
        showNotification("error", "Lỗi kết nối. Vui lòng thử lại.");
    } finally {
        // Reset button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
    }
}

/**
 * Utility functions
 */

function showNotification(type, message) {
    // Use the global notification system if available
    if (typeof window.showNotification === "function") {
        window.showNotification(type, message);
        return;
    }

    // Fallback notification
    const alertClass = type === "success" ? "alert-success" : "alert-danger";
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Find or create notification container
    let container = document.querySelector(".notification-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "notification-container position-fixed top-0 end-0 p-3";
        container.style.zIndex = "9999";
        document.body.appendChild(container);
    }

    container.insertAdjacentHTML("beforeend", alertHTML);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector(".alert");
        if (alert) {
            alert.remove();
        }
    }, 5000);
}
