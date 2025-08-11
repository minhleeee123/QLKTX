/**
 * Room Browser JavaScript for Student Interface
 * Handles room registration, details viewing, and interactions
 */

let selectedRoomId = null;
let selectedRoomNumber = null;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    initializeRoomBrowser();
});

function initializeRoomBrowser() {
    console.log("Initializing room browser...");
    
    // Initialize modals
    const registerModal = document.getElementById("registerModal");
    const roomDetailModal = document.getElementById("roomDetailModal");

    // Set up confirm registration handler
    const confirmRegisterBtn = document.getElementById("confirmRegisterBtn");
    if (confirmRegisterBtn) {
        confirmRegisterBtn.addEventListener("click", confirmRoomRegistration);
        console.log("Confirm registration button handler attached");
    } else {
        console.error("Confirm register button not found!");
    }

    // Set up direct event listeners on buttons
    function setupButtonListeners() {
        const registerButtons = document.querySelectorAll('[data-action="register-room"]');
        const viewDetailButtons = document.querySelectorAll('[data-action="view-room-details"]');
        const cancelButtons = document.querySelectorAll('[data-action="cancel-registration"]');
        
        console.log("Found buttons:", {
            register: registerButtons.length,
            viewDetail: viewDetailButtons.length,
            cancel: cancelButtons.length
        });

        registerButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const roomId = parseInt(this.getAttribute("data-room-id"));
                const roomNumber = this.getAttribute("data-room-number");
                console.log("Register button clicked:", roomId, roomNumber);
                registerRoom(roomId, roomNumber);
            });
        });

        viewDetailButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const roomId = parseInt(this.getAttribute("data-room-id"));
                console.log("View details button clicked:", roomId);
                viewRoomDetails(roomId);
            });
        });

        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const registrationId = parseInt(this.getAttribute("data-registration-id"));
                console.log("Cancel button clicked:", registrationId);
                cancelRegistration(registrationId);
            });
        });
    }

    // Setup initial button listeners
    setupButtonListeners();
    
    // Also keep the event delegation as backup
    document.addEventListener("click", function(event) {
        console.log("Document click detected on:", event.target);
        
        const button = event.target.closest("[data-action]");
        if (!button) {
            console.log("No data-action button found");
            return;
        }

        event.preventDefault(); // Prevent default button behavior
        
        const action = button.getAttribute("data-action");
        console.log("Button clicked with action:", action, "Button:", button);
        
        switch(action) {
            case "register-room":
                const roomId = parseInt(button.getAttribute("data-room-id"));
                const roomNumber = button.getAttribute("data-room-number");
                console.log("Registering room:", roomId, roomNumber);
                registerRoom(roomId, roomNumber);
                break;
            case "cancel-registration":
                const registrationId = parseInt(button.getAttribute("data-registration-id"));
                console.log("Canceling registration:", registrationId);
                cancelRegistration(registrationId);
                break;
            case "view-room-details":
                const detailRoomId = parseInt(button.getAttribute("data-room-id"));
                console.log("Viewing room details:", detailRoomId);
                viewRoomDetails(detailRoomId);
                break;
            default:
                console.warn("Unknown action:", action);
        }
    });

    // Handle modal cleanup
    if (registerModal) {
        registerModal.addEventListener("hidden.bs.modal", function () {
            selectedRoomId = null;
            selectedRoomNumber = null;
            console.log("Registration modal closed");
        });
    }

    console.log("Room browser initialized successfully");
}

/**
 * Show room registration modal
 */
function registerRoom(roomId, roomNumber) {
    console.log("registerRoom called with:", roomId, roomNumber);
    
    selectedRoomId = roomId;
    selectedRoomNumber = roomNumber;

    // Update modal content
    const roomNumberElement = document.getElementById("roomNumberToRegister");
    if (roomNumberElement) {
        roomNumberElement.textContent = roomNumber;
        console.log("Updated modal with room number:", roomNumber);
    } else {
        console.error("roomNumberToRegister element not found!");
    }

    // Show modal
    const modalElement = document.getElementById("registerModal");
    if (modalElement) {
        const registerModal = new bootstrap.Modal(modalElement);
        registerModal.show();
        console.log("Registration modal shown");
    } else {
        console.error("registerModal element not found!");
    }
}

/**
 * Confirm and submit room registration
 */
async function confirmRoomRegistration() {
    if (!selectedRoomId) {
        showNotification("error", "Không tìm thấy thông tin phòng");
        return;
    }

    console.log("Confirming registration for room:", selectedRoomId);
    
    const confirmBtn = document.getElementById("confirmRegisterBtn");
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
                console.log("CSRF token added to request");
            }
        }

        // Make registration request
        const response = await fetch(`/student/register/${selectedRoomId}`, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        console.log("Response status:", response.status);
        
        const data = await response.json();
        console.log("Response data:", data);

        if (response.ok && data.success) {
            // Hide modal
            const modalElement = document.getElementById("registerModal");
            if (modalElement) {
                const registerModal = bootstrap.Modal.getInstance(modalElement);
                if (registerModal) {
                    registerModal.hide();
                } else {
                    // Manually hide modal
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.remove();
                }
            }

            // Show success message
            showNotification("success", data.message || "Đăng ký phòng thành công!");

            // Reload page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification("error", data.message || "Có lỗi xảy ra khi đăng ký phòng");
        }
    } catch (error) {
        console.error("Registration error:", error);
        showNotification("error", "Lỗi kết nối. Vui lòng thử lại.");
    } finally {
        // Reset button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
    }
}

/**
 * View room details in modal
 */
async function viewRoomDetails(roomId) {
    console.log("Viewing room details for:", roomId);
    
    // Show modal with loading state
    const modalElement = document.getElementById("roomDetailModal");
    if (!modalElement) {
        console.error("Room detail modal not found!");
        return;
    }
    
    const roomDetailModal = new bootstrap.Modal(modalElement);
    roomDetailModal.show();

    const contentElement = document.getElementById("roomDetailContent");
    if (!contentElement) {
        console.error("Room detail content element not found!");
        return;
    }
    
    const loadingTemplate = document.getElementById("loadingTemplate");
    if (loadingTemplate) {
        contentElement.innerHTML = loadingTemplate.innerHTML;
    } else {
        contentElement.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div><p class="mt-2">Đang tải...</p></div>';
    }

    try {
        // Fetch room details
        const response = await fetch(`/student/rooms/${roomId}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        console.log("Room details response status:", response.status);
        const data = await response.json();
        console.log("Room details response data:", data);

        if (response.ok && data.success) {
            const room = data.data.room;

            // Prepare template data
            const templateData = {
                room_id: room.room_id,
                room_number: room.room_number,
                building_name: room.building.building_name,
                room_type_name: room.room_type.type_name,
                capacity: room.room_type.capacity,
                current_occupancy: room.current_occupancy,
                available_slots: room.available_slots,
                monthly_price: formatCurrency(room.room_type.price),
                description: room.description || "Không có mô tả",
            };

            // Render template
            const template = document.getElementById("roomDetailTemplate");
            if (template) {
                const renderedHTML = renderTemplate(template.innerHTML, templateData);
                contentElement.innerHTML = renderedHTML;
            } else {
                // Fallback if template not found
                contentElement.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-door-open"></i> Thông tin phòng</h6>
                            <table class="table table-sm">
                                <tr><td><strong>Số phòng:</strong></td><td>${room.room_number}</td></tr>
                                <tr><td><strong>Tòa nhà:</strong></td><td>${room.building.building_name}</td></tr>
                                <tr><td><strong>Loại phòng:</strong></td><td>${room.room_type.type_name}</td></tr>
                                <tr><td><strong>Sức chứa:</strong></td><td>${room.room_type.capacity} người</td></tr>
                                <tr><td><strong>Hiện tại:</strong></td><td>${room.current_occupancy}/${room.room_type.capacity} người</td></tr>
                                <tr><td><strong>Còn trống:</strong></td><td>${room.available_slots} chỗ</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-money-bill-wave"></i> Thông tin giá</h6>
                            <table class="table table-sm">
                                <tr><td><strong>Giá phòng:</strong></td><td><strong class="text-primary">${formatCurrency(room.room_type.price)} VNĐ/tháng</strong></td></tr>
                            </table>
                            <h6 class="mt-3"><i class="fas fa-info-circle"></i> Mô tả</h6>
                            <p class="text-muted">${room.description || 'Không có mô tả'}</p>
                        </div>
                    </div>
                    <div class="mt-3 text-center">
                        <button class="btn btn-primary" data-action="register-room" data-room-id="${room.room_id}" data-room-number="${room.room_number}">
                            <i class="fas fa-paper-plane"></i> Đăng ký phòng này
                        </button>
                    </div>
                `;
            }
        } else {
            contentElement.innerHTML = `
                <div class="text-center py-4 text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>${data.message || "Có lỗi xảy ra khi tải thông tin phòng"}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error("Error loading room details:", error);
        contentElement.innerHTML = `
            <div class="text-center py-4 text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <p>Lỗi kết nối. Vui lòng thử lại.</p>
            </div>
        `;
    }
}

/**
 * Cancel room registration
 */
async function cancelRegistration(registrationId) {
    console.log("Canceling registration:", registrationId);
    
    if (!confirm("Bạn có chắc chắn muốn hủy đăng ký này không?")) {
        return;
    }

    try {
        // Prepare request data with CSRF token
        const formData = new FormData();
        
        // Add CSRF token if CSRFUtils is available
        if (typeof CSRFUtils !== 'undefined') {
            const token = CSRFUtils.getToken();
            if (token) {
                formData.append('csrf_token', token);
                console.log("CSRF token added to cancel request");
            }
        }

        const response = await fetch(`/student/registrations/${registrationId}/cancel`, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        console.log("Cancel response status:", response.status);
        const data = await response.json();
        console.log("Cancel response data:", data);

        if (response.ok && data.success) {
            showNotification("success", data.message || "Hủy đăng ký thành công!");
            // Reload page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification("error", data.message || "Có lỗi xảy ra khi hủy đăng ký");
        }
    } catch (error) {
        console.error("Cancel registration error:", error);
        showNotification("error", "Lỗi kết nối. Vui lòng thử lại.");
    }
}

/**
 * Utility functions
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

function formatCurrency(amount) {
    return new Intl.NumberFormat("vi-VN").format(amount);
}

function renderTemplate(template, data) {
    let result = template;
    for (const [key, value] of Object.entries(data)) {
        const regex = new RegExp(`{{${key}}}`, "g");
        result = result.replace(regex, value);
    }
    return result;
}

// Export functions for global access
window.registerRoom = registerRoom;
window.viewRoomDetails = viewRoomDetails;
window.cancelRegistration = cancelRegistration;

// Export for debugging
window.testButton = function() {
    console.log("Testing button click...");
    const button = document.querySelector('[data-action="register-room"]');
    console.log("Found button:", button);
    if (button) {
        const roomId = button.getAttribute('data-room-id');
        const roomNumber = button.getAttribute('data-room-number');
        console.log("Button data:", roomId, roomNumber);
        registerRoom(parseInt(roomId), roomNumber);
    } else {
        console.log("No register button found");
    }
};
