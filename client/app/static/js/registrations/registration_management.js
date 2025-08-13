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

  // Debug: Check if modals exist
  console.log("Approve modal found:", !!approveModal);
  console.log("Reject modal found:", !!rejectModal);

  // Debug: Check if modal content elements exist
  const approveStudentNameEl = document.getElementById("approveStudentName");
  const approveRoomNumberEl = document.getElementById("approveRoomNumber");
  const rejectStudentNameEl = document.getElementById("rejectStudentName");
  const rejectRoomNumberEl = document.getElementById("rejectRoomNumber");

  console.log("Approve student name element found:", !!approveStudentNameEl);
  console.log("Approve room number element found:", !!approveRoomNumberEl);
  console.log("Reject student name element found:", !!rejectStudentNameEl);
  console.log("Reject room number element found:", !!rejectRoomNumberEl);

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

  // Set up event delegation for approve/reject/view buttons
  document.addEventListener("click", function (event) {
    const button = event.target.closest("[data-action]");
    if (!button) return;

    event.preventDefault();

    const action = button.getAttribute("data-action");
    const registrationId = parseInt(
      button.getAttribute("data-registration-id")
    );
    const studentName = button.getAttribute("data-student-name");
    const roomNumber = button.getAttribute("data-room-number");

    console.log(
      "Button clicked:",
      action,
      registrationId,
      studentName,
      roomNumber
    );

    switch (action) {
      case "approve":
        showApproveModal(registrationId, studentName, roomNumber);
        break;
      case "reject":
        showRejectModal(registrationId, studentName, roomNumber);
        break;
      case "view":
        showRegistrationDetailModal(registrationId);
        break;
      default:
        console.warn("Unknown action:", action);
    }
  });
  /**
   * Show registration detail modal via AJAX
   */
  async function showRegistrationDetailModal(registrationId) {
    const modalElement = document.getElementById("registrationDetailModal");
    const modalContent = document.getElementById("registrationDetailContent");
    if (!modalElement || !modalContent) return;

    // Show loading template
    modalContent.innerHTML = document.getElementById(
      "registrationDetailLoadingTemplate"
    ).innerHTML;
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    try {
      const response = await fetch(`/registrations/${registrationId}`, {
        method: "GET",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) throw new Error("Không thể tải thông tin đăng ký");
      const data = await response.json();
      if (!data.success || !data.data)
        throw new Error(data.message || "Không tìm thấy đăng ký");

      // The registration data is in data.data.registration based on our route
      const registration = data.data.registration;
      if (!registration) throw new Error("Không tìm thấy thông tin đăng ký");

      // Fill template with registration data
      const template = document.getElementById(
        "registrationDetailTemplate"
      ).innerHTML;
      modalContent.innerHTML = template;
      // Fill fields
      document.getElementById("regDetailId").textContent =
        registration.registration_id;
      document.getElementById("regDetailDate").textContent =
        registration.registration_date;
      document.getElementById("regDetailStatus").textContent =
        registration.status;
      document.getElementById("regDetailStudentName").textContent =
        registration.student.full_name;
      document.getElementById("regDetailStudentId").textContent =
        registration.student.student_id;
      document.getElementById("regDetailStudentEmail").textContent =
        registration.student.email;
      document.getElementById("regDetailRoomNumber").textContent =
        registration.room.room_number;
      document.getElementById("regDetailBuildingName").textContent =
        registration.room.building_name;
      document.getElementById("regDetailRoomType").textContent =
        registration.room.room_type;
      document.getElementById("regDetailRoomPrice").textContent =
        registration.room.price;
    } catch (error) {
      modalContent.innerHTML = document.getElementById(
        "registrationDetailErrorTemplate"
      ).innerHTML;
      document.getElementById("registrationDetailErrorMsg").textContent =
        error.message;
    }
  }

  console.log("Registration management initialized successfully");
}

/**
 * Show approve confirmation modal
 */
function showApproveModal(registrationId, studentName, roomNumber) {
  console.log("Showing approve modal for registration:", registrationId);

  selectedRegistrationId = registrationId;

  // Wait a bit for any template includes to be processed
  setTimeout(() => {
    // Check if elements exist before trying to access them
    const studentNameElement = document.getElementById("approveStudentName");
    const roomNumberElement = document.getElementById("approveRoomNumber");

    if (!studentNameElement) {
      console.error("Element with ID 'approveStudentName' not found");
      console.error(
        "Available elements with 'approve' in ID:",
        Array.from(document.querySelectorAll('[id*="approve"]')).map(
          (el) => el.id
        )
      );
      return;
    }

    if (!roomNumberElement) {
      console.error("Element with ID 'approveRoomNumber' not found");
      return;
    }

    // Update modal content
    studentNameElement.textContent = studentName;
    roomNumberElement.textContent = roomNumber;

    // Show modal
    const modalElement = document.getElementById("approveModal");
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
      console.log("Approve modal shown");
    } else {
      console.error("Approve modal element not found");
    }
  }, 100); // Small delay to ensure DOM is ready

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

  // Check if elements exist before trying to access them
  const studentNameElement = document.getElementById("rejectStudentName");
  const roomNumberElement = document.getElementById("rejectRoomNumber");

  if (!studentNameElement) {
    console.error("Element with ID 'rejectStudentName' not found");
    return;
  }

  if (!roomNumberElement) {
    console.error("Element with ID 'rejectRoomNumber' not found");
    return;
  }

  // Update modal content
  studentNameElement.textContent = studentName;
  roomNumberElement.textContent = roomNumber;

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
