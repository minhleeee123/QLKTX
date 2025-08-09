// Room Type management JavaScript functions

// Global variables
let currentRoomTypeId = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  initializeRoomTypeOperations();
});

// Make functions globally available
window.deleteRoomType = function (roomTypeId, roomTypeName) {
  if (
    confirm(
      `Bạn có chắc chắn muốn xóa loại phòng "${roomTypeName}"?\n\nLưu ý: Việc xóa loại phòng sẽ ảnh hưởng đến tất cả các phòng đang sử dụng loại phòng này!`
    )
  ) {
    performDeleteRoomType(roomTypeId);
  }
};

window.openCreateRoomTypeModal = openCreateRoomTypeModal;
window.openEditRoomTypeModal = openEditRoomTypeModal;
window.viewRoomTypeDetails = viewRoomTypeDetails;

function initializeRoomTypeOperations() {
  // Initialize modal event handlers
  initializeModalHandlers();

  // Initialize form submission handlers
  initializeFormHandlers();
}

function initializeModalHandlers() {
  const roomTypeModal = document.getElementById("roomTypeModal");
  const deleteModal = document.getElementById("deleteRoomTypeModal");

  if (roomTypeModal) {
    roomTypeModal.addEventListener("hidden.bs.modal", function () {
      resetRoomTypeForm();
    });
  }
}

function initializeFormHandlers() {
  const roomTypeForm = document.getElementById("roomTypeForm");

  if (roomTypeForm) {
    roomTypeForm.addEventListener("submit", function (e) {
      e.preventDefault();
      submitRoomTypeForm();
    });
  }
}

// Open create room type modal
function openCreateRoomTypeModal() {
  currentRoomTypeId = null;
  const modal = new bootstrap.Modal(document.getElementById("roomTypeModal"));
  const modalTitle = document.getElementById("roomTypeModalLabel");

  modalTitle.textContent = "Thêm loại phòng mới";
  resetRoomTypeForm();
  modal.show();
}

// Open edit room type modal
function openEditRoomTypeModal(roomTypeId) {
  currentRoomTypeId = roomTypeId;
  const modal = new bootstrap.Modal(document.getElementById("roomTypeModal"));
  const modalTitle = document.getElementById("roomTypeModalLabel");

  modalTitle.textContent = "Chỉnh sửa loại phòng";

  // Load room type data
  loadRoomTypeData(roomTypeId)
    .then(() => {
      modal.show();
    })
    .catch((error) => {
      console.error("Error loading room type data:", error);
      showAlert("Lỗi khi tải thông tin loại phòng", "danger");
    });
}

// Load room type data for editing
async function loadRoomTypeData(roomTypeId) {
  try {
    // Get CSRF token with fallback methods
    let csrfToken = null;
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
      csrfToken = csrfMeta.getAttribute("content");
    }

    // Fallback: try to get from hidden input
    if (!csrfToken) {
      const csrfInput = document.querySelector('input[name="csrf_token"]');
      if (csrfInput) {
        csrfToken = csrfInput.value;
      }
    }

    const headers = {
      "X-Requested-With": "XMLHttpRequest",
    };

    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }

    const response = await fetch(`/room-types/${roomTypeId}`, {
      method: "GET",
      headers: headers,
    });

    if (!response.ok) {
      throw new Error("Failed to load room type data");
    }

    const data = await response.json();
    const roomType = data.room_type;

    // Populate form fields
    document.getElementById("roomTypeId").value = roomType.room_type_id;
    document.getElementById("typeName").value = roomType.type_name;
    document.getElementById("capacity").value = roomType.capacity;
    document.getElementById("price").value = roomType.price;
    document.getElementById("description").value = roomType.description || "";
  } catch (error) {
    console.error("Error loading room type data:", error);
    throw error;
  }
}

// Submit room type form
async function submitRoomTypeForm() {
  const form = document.getElementById("roomTypeForm");
  const submitBtn = document.getElementById("submitBtn");
  const submitText = document.getElementById("submitText");
  const spinner = submitBtn.querySelector(".spinner-border");

  // Show loading state
  submitBtn.disabled = true;
  spinner.classList.remove("d-none");
  submitText.textContent = "Đang xử lý...";

  // Clear previous error messages
  clearErrorMessages();

  try {
    const formData = new FormData(form);
    const url = currentRoomTypeId
      ? `/room-types/${currentRoomTypeId}/edit`
      : "/room-types/create";

    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const data = await response.json();

    if (response.ok && data.success) {
      // Success
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("roomTypeModal")
      );
      modal.hide();

      showAlert(data.message || "Thao tác thành công", "success");

      // Reload page to refresh data
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      // Handle validation errors
      if (data.errors) {
        displayErrorMessages(data.errors);
      } else {
        showAlert(data.message || "Có lỗi xảy ra", "danger");
      }
    }
  } catch (error) {
    console.error("Error submitting form:", error);
    showAlert("Lỗi kết nối. Vui lòng thử lại.", "danger");
  } finally {
    // Hide loading state
    submitBtn.disabled = false;
    spinner.classList.add("d-none");
    submitText.textContent = "Lưu";
  }
}

// View room type details
function viewRoomTypeDetails(roomTypeId) {
  console.log("Viewing details for room type ID:", roomTypeId);
  const modal = new bootstrap.Modal(
    document.getElementById("roomTypeDetailsModal")
  );
  const content = document.getElementById("roomTypeDetailsContent");

  // Show loading
  content.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
        </div>
    `;

  modal.show();

  // Load details
  loadRoomTypeDetails(roomTypeId)
    .then((data) => {
      displayRoomTypeDetails(data.room_type);
    })
    .catch((error) => {
      console.error("Error loading room type details:", error);
      content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Không thể tải thông tin loại phòng
                </div>
            `;
    });
}

// Load room type details
async function loadRoomTypeDetails(roomTypeId) {
  // Get CSRF token with fallback methods
  let csrfToken = null;
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  if (csrfMeta) {
    csrfToken = csrfMeta.getAttribute("content");
  }

  // Fallback: try to get from hidden input
  if (!csrfToken) {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
      csrfToken = csrfInput.value;
    }
  }

  const headers = {
    "X-Requested-With": "XMLHttpRequest",
  };

  if (csrfToken) {
    headers["X-CSRFToken"] = csrfToken;
  }

  const response = await fetch(`/room-types/${roomTypeId}`, {
    method: "GET",
    headers: headers,
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ error: "Network error" }));
    console.error("Error fetching room type details:", errorData);
    throw new Error("Failed to load room type details");
  }

  const room_type = await response.json();
  console.log("Fetched room type details:", room_type);

  return room_type.data;
}

// Display room type details in modal
function displayRoomTypeDetails(roomType) {
  const content = document.getElementById("roomTypeDetailsContent");
  const editBtn = document.getElementById("editFromDetailsBtn");

  console.log("Displaying room type details:", roomType);
  // roomType.room_type_id;
  // roomType.type_name;
  // roomType.capacity;
  // roomType.price;
  // roomType.total_rooms;
  // roomType.available_rooms;
  // roomType.total_rooms;
  // roomType.available_rooms;
  // roomType.description;
  // roomType.description;

  content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <dl class="row">
                    <dt class="col-sm-4">ID:</dt>
                    <dd class="col-sm-8">${roomType.room_type_id}</dd>
                    
                    <dt class="col-sm-4">Tên loại phòng:</dt>
                    <dd class="col-sm-8"><strong>${
                      roomType.type_name
                    }</strong></dd>
                    
                    <dt class="col-sm-4">Sức chứa:</dt>
                    <dd class="col-sm-8"><span class="badge bg-info">${
                      roomType.capacity
                    } người</span></dd>
                    
                    <dt class="col-sm-4">Giá phòng:</dt>
                    <dd class="col-sm-8"><strong>${formatCurrency(
                      roomType.price
                    )}</strong></dd>
                </dl>
            </div>
            <div class="col-md-6">
                <dl class="row">
                    <dt class="col-sm-5">Tổng số phòng:</dt>
                    <dd class="col-sm-7"><span class="badge bg-primary">${
                      roomType.total_rooms || 0
                    }</span></dd>
                    
                    <dt class="col-sm-5">Phòng có sẵn:</dt>
                    <dd class="col-sm-7"><span class="badge bg-success">${
                      roomType.available_rooms || 0
                    }</span></dd>
                    
                    <dt class="col-sm-5">Tỷ lệ sử dụng:</dt>
                    <dd class="col-sm-7">${calculateUsageRate(
                      roomType.total_rooms,
                      roomType.available_rooms,
                      roomType.occupied_rooms
                    )}</dd>
                </dl>
            </div>
        </div>
        ${
          roomType.description
            ? `
        <div class="row mt-3">
            <div class="col-12">
                <h6>Mô tả:</h6>
                <p class="text-muted">${roomType.description}</p>
            </div>
        </div>
        `
            : ""
        }
    `;

  if (editBtn) {
    editBtn.style.display = "inline-block";
    editBtn.onclick = () => {
      const detailsModal = bootstrap.Modal.getInstance(
        document.getElementById("roomTypeDetailsModal")
      );
      detailsModal.hide();
      setTimeout(() => openEditRoomTypeModal(roomType.room_type_id), 300);
    };
  }
}

// Perform room type deletion
async function performDeleteRoomType(roomTypeId) {
  console.log("Attempting to delete room type with ID:", roomTypeId);

  try {
    // Get CSRF token with multiple fallback options
    let csrfToken = null;

    // Try to get from meta tag first
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
      csrfToken = csrfMeta.getAttribute("content");
    }

    // Fallback 1: try to get from any hidden input with name csrf_token
    if (!csrfToken) {
      const csrfInput = document.querySelector('input[name="csrf_token"]');
      if (csrfInput) {
        csrfToken = csrfInput.value;
      }
    }

    // Fallback 2: try to get from element with id csrfToken
    if (!csrfToken) {
      const csrfInputId = document.getElementById("csrfToken");
      if (csrfInputId) {
        csrfToken = csrfInputId.value;
      }
    }

    console.log(
      "Room type delete - CSRF Token found:",
      csrfToken ? "Yes" : "No"
    );
    console.log("Room type delete - CSRF Token value:", csrfToken);

    // Prepare form data with CSRF token
    const formData = new FormData();
    if (csrfToken) {
      formData.append("csrf_token", csrfToken);
    }

    const headers = {
      "X-Requested-With": "XMLHttpRequest",
    };

    const response = await fetch(`/room-types/${roomTypeId}/delete`, {
      method: "POST",
      headers: headers,
      body: formData,
    });

    console.log("Response status:", response.status);
    console.log("Response headers:", response.headers.get("content-type"));

    // Check if response is JSON
    const contentType = response.headers.get("content-type");
    let data;

    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      // If not JSON, get as text to see what the server returned
      const textResponse = await response.text();
      console.log("Non-JSON response:", textResponse);
      throw new Error(
        `Server returned HTML instead of JSON. Status: ${response.status}`
      );
    }

    if (response.ok && data.success) {
      showAlert(data.message || "Xóa loại phòng thành công", "success");

      // Reload page to refresh data
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      showAlert(data.message || "Không thể xóa loại phòng", "danger");
    }
  } catch (error) {
    console.error("Error deleting room type:", error);
    showAlert("Lỗi kết nối. Vui lòng thử lại.", "danger");
  }
}

// Utility functions
function resetRoomTypeForm() {
  const form = document.getElementById("roomTypeForm");
  if (form) {
    form.reset();
    document.getElementById("roomTypeId").value = "";
    clearErrorMessages();
  }
}

function clearErrorMessages() {
  const errorElements = document.querySelectorAll(".text-danger.small");
  errorElements.forEach((element) => {
    element.textContent = "";
  });
}

function displayErrorMessages(errors) {
  Object.keys(errors).forEach((field) => {
    const errorElement = document.getElementById(`${field}Error`);
    if (errorElement) {
      errorElement.textContent = errors[field].join(", ");
    }
  });
}

function showAlert(message, type = "info") {
  // Create alert element
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(alertDiv);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.parentNode.removeChild(alertDiv);
    }
  }, 5000);
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(amount);
}

function calculateUsageRate(total, available, occupied) {
  if (!total || total === 0) {
    return '<span class="text-muted">Chưa có phòng</span>';
  }

  // Use occupied directly if provided, otherwise calculate from total - available
  const occupiedRooms =
    occupied !== undefined ? occupied : total - (available || 0);
  const rate = ((occupiedRooms / total) * 100).toFixed(1);

  // Determine color class based on usage rate
  let colorClass = "success";
  if (rate >= 90) {
    colorClass = "danger";
  } else if (rate >= 75) {
    colorClass = "warning";
  } else if (rate >= 50) {
    colorClass = "info";
  }

  return `
        <div class="progress" style="height: 15px;">
            <div class="progress-bar bg-${colorClass}" 
                 style="width: ${Math.max(rate, 3)}%; min-width: 20px;" 
                 title="${rate}%">
                ${rate}%
            </div>
        </div>
    `;
}
