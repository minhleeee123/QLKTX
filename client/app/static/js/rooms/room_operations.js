// Room management JavaScript functions
let isEditMode = false;
let currentRoomId = null;

// Utility Functions

/**
 * Template utilities
 */
const TemplateUtils = {
  /**
   * Replace template placeholders with data
   */
  render(templateId, data) {
    let template = document.getElementById(templateId).innerHTML;

    Object.entries(data).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      template = template.replaceAll(placeholder, value);
    });

    return template;
  },

  /**
   * Show loading template in container
   */
  showLoading(containerId, loadingTemplateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(loadingTemplateId).innerHTML;
    container.innerHTML = template;
  },

  /**
   * Show error template in container
   */
  showError(containerId, errorTemplateId, message) {
    const container = document.getElementById(containerId);
    const template = this.render(errorTemplateId, { message });
    container.innerHTML = template;
  },
};

/**
 * Room data management utilities
 */
const RoomDataUtils = {
  /**
   * Fetch room data from server
   */
  async fetchRoom(roomId) {
    const response = await fetch(`/rooms/${roomId}`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });

    const apiResponse = await response.json();
    console.log("Fetched room API response:", apiResponse);

    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Failed to fetch room data");
    }

    // Backend returns: {success, message, data: {room: {...}}, status_code}
    // We want just the room object
    return apiResponse.data.room;
  },

  /**
   * Populate form fields with room data
   */
  populateForm(room) {
    const fieldMap = {
      roomNumber: room.room_number,
      buildingId: room.building_id,
      roomTypeId: room.room_type_id,
      status: room.status,
      description: room.description
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
  },

  /**
   * Fetch buildings for dropdown
   */
  async fetchBuildings() {
    const response = await fetch("/rooms/buildings", {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const apiResponse = await response.json();
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Failed to fetch buildings");
    }

    return apiResponse.data.buildings;
  },

  /**
   * Fetch room types for dropdown
   */
  async fetchRoomTypes() {
    const response = await fetch("/rooms/room-types", {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const apiResponse = await response.json();
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Failed to fetch room types");
    }

    return apiResponse.data.room_types;
  }
};

/**
 * Modal management utilities
 */
const ModalUtils = {
  /**
   * Show modal with proper cleanup handling
   */
  show(modalId, cleanupCallback = null) {
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);

    // Add cleanup event listener
    modalElement.addEventListener(
      "hidden.bs.modal",
      function () {
        this.cleanup();
        if (cleanupCallback) cleanupCallback();
      }.bind(this),
      { once: true }
    );

    modal.show();
    return modal;
  },

  /**
   * Hide modal with cleanup
   */
  hide(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
      modal.hide();
    }
    this.cleanup();
  },

  /**
   * Clean up modal backdrop and body styles
   */
  cleanup() {
    const backdrop = document.querySelector(".modal-backdrop");
    if (backdrop) {
      backdrop.remove();
    }
    document.body.classList.remove("modal-open");
    document.body.style.paddingRight = "";
    document.body.style.overflow = "";
  }
};

// Function to open create room modal
function openCreateRoomModal() {
  isEditMode = false;
  currentRoomId = null;
  document.getElementById("roomModalLabel").textContent = "Thêm phòng mới";
  document.getElementById("saveRoomBtn").innerHTML =
    '<i class="fas fa-save"></i> Lưu';
  document.getElementById("roomForm").reset();
  document.getElementById("roomId").value = "";

  // Enable all fields for create mode
  const roomNumberField = document.getElementById("roomNumber");
  const buildingField = document.getElementById("buildingId");

  if (roomNumberField) {
    roomNumberField.disabled = false;
    roomNumberField.style.backgroundColor = ""; // Reset background
  }

  if (buildingField) {
    buildingField.disabled = false;
    buildingField.style.backgroundColor = ""; // Reset background
  }

  clearFormErrors();
  loadBuildingsAndRoomTypes();
}

// Function to open edit room modal
async function openEditRoomModal(roomId) {
  // Convert string to number if needed
  roomId = parseInt(roomId);

  isEditMode = true;
  currentRoomId = roomId;
  document.getElementById("roomModalLabel").textContent = "Chỉnh sửa phòng";
  document.getElementById("saveRoomBtn").innerHTML =
    '<i class="fas fa-save"></i> Cập nhật';
  document.getElementById("roomId").value = roomId;

  clearFormErrors();
  await loadBuildingsAndRoomTypes();

  // Disable non-updatable fields in edit mode
  const roomNumberField = document.getElementById("roomNumber");
  const buildingField = document.getElementById("buildingId");

  if (roomNumberField) {
    roomNumberField.disabled = true;
    roomNumberField.style.backgroundColor = "#f8f9fa"; // Light gray background
  }

  if (buildingField) {
    buildingField.disabled = true;
    buildingField.style.backgroundColor = "#f8f9fa"; // Light gray background
  }

  // Show modal
  ModalUtils.show("roomModal");

  try {
    // Load room data
    const room = await RoomDataUtils.fetchRoom(roomId);
    console.log("Loaded room data:", room);

    // Populate form with room data
    RoomDataUtils.populateForm(room);
  } catch (error) {
    showNotification("error", "Lỗi: " + error.message);
    ModalUtils.hide("roomModal");
  }
}

// Function to view room details
async function viewRoomDetails(roomId) {
  // Convert string to number if needed
  roomId = parseInt(roomId);

  // Show the modal first
  ModalUtils.show("roomDetailModal");

  // Show loading state
  TemplateUtils.showLoading("roomDetailContent", "roomDetailLoadingTemplate");

  try {
    const room = await RoomDataUtils.fetchRoom(roomId);
    console.log("Loaded room data for details:", room);

    // Prepare template data
    const templateData = {
      room_id: room.room_id || "N/A",
      room_number: room.room_number || "N/A",
      building_name: room.building?.building_name || "N/A",
      room_type_name: room.room_type?.type_name || "N/A",
      capacity: room.room_type?.capacity || "N/A",
      monthly_price: room.room_type?.price
        ? new Intl.NumberFormat("vi-VN").format(room.room_type.price)
        : "N/A",
      status_badge_class: getStatusBadgeClass(room.status),
      status_text: getStatusText(room.status),
      description: room.description || "Không có mô tả",
      created_at: room.created_at
        ? new Date(room.created_at).toLocaleString("vi-VN")
        : "Chưa có",
    };

    // Render and display template
    const renderedTemplate = TemplateUtils.render(
      "roomDetailTemplate",
      templateData
    );
    document.getElementById("roomDetailContent").innerHTML = renderedTemplate;
  } catch (error) {
    console.error("Error fetching room data:", error);
    TemplateUtils.showError(
      "roomDetailContent",
      "roomDetailErrorTemplate",
      error.message || "Có lỗi xảy ra khi tải thông tin phòng"
    );
  }
}

// Function to open delete room modal
function openDeleteRoomModal(button) {
  const roomId = button.getAttribute("data-room-id");
  const roomNumber = button.getAttribute("data-room-number");

  document.getElementById("roomToDelete").textContent = roomNumber;
  document.getElementById("deleteRoomForm").action = `/rooms/${roomId}/delete`;
}

// Load buildings and room types for dropdowns
async function loadBuildingsAndRoomTypes() {
  try {
    // Load buildings
    const buildings = await RoomDataUtils.fetchBuildings();
    const buildingSelect = document.getElementById("buildingId");
    buildingSelect.innerHTML = '<option value="">Chọn tòa nhà</option>';

    buildings.forEach((building) => {
      const option = document.createElement("option");
      option.value = building.building_id;
      option.textContent = building.building_name;
      buildingSelect.appendChild(option);
    });

    // Load room types
    const roomTypes = await RoomDataUtils.fetchRoomTypes();
    const roomTypeSelect = document.getElementById("roomTypeId");
    roomTypeSelect.innerHTML = '<option value="">Chọn loại phòng</option>';

    roomTypes.forEach((roomType) => {
      const option = document.createElement("option");
      option.value = roomType.room_type_id;
      option.textContent = `${roomType.type_name} (${roomType.capacity} người)`;
      roomTypeSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading buildings and room types:", error);
    showNotification("error", "Có lỗi khi tải danh sách tòa nhà và loại phòng");
  }
}

// Helper function to get status text
function getStatusText(status) {
  const statusMap = {
    available: "Có sẵn",
    occupied: "Đã có người ở",
    pending_approval: "Chờ duyệt",
    maintenance: "Bảo trì",
    unavailable: "Không khả dụng",
  };
  return statusMap[status] || status;
}

// Helper function to get status badge class
function getStatusBadgeClass(status) {
  const statusClassMap = {
    available: "bg-success",
    occupied: "bg-danger",
    pending_approval: "bg-warning",
    maintenance: "bg-secondary",
    unavailable: "bg-dark",
  };
  return statusClassMap[status] || "bg-secondary";
}

/**
 * Handle form submission with proper error handling and UI feedback
 */
async function submitRoomForm(url, formData, submitBtn, originalButtonText) {
  try {
    console.log("Submitting to URL:", url);
    console.log("Form data entries:", [...formData.entries()]);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    });

    console.log("Response status:", response.status);
    console.log("Response headers:", [...response.headers.entries()]);

    const apiResponse = await handleResponse(response);
    console.log("API Response:", apiResponse);

    handleSuccessResponse(apiResponse);
  } catch (error) {
    console.error("Submit error:", error);
    handleErrorResponse(error);
  } finally {
    resetSubmitButton(submitBtn, originalButtonText);
  }
}

/**
 * Handle fetch response and parse JSON
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage;
    try {
      const errorData = await response.json();
      errorMessage =
        errorData.message || `HTTP ${response.status}: ${response.statusText}`;
    } catch (parseError) {
      errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }
  return await response.json();
}

/**
 * Handle successful response
 */
function handleSuccessResponse(data) {
  console.log("Handling success response:", data);

  if (data.success) {
    // Store notification for after redirect
    storeNotificationForRedirect(
      "success",
      data.message || "Thao tác thành công!"
    );
    closeModalAndRedirect(data.redirect);
  } else {
    if (data.errors) {
      displayFormErrors(data.errors);
    } else {
      showNotification("error", "Lỗi: " + (data.message || "Có lỗi xảy ra"));
    }
  }
}

/**
 * Handle error response
 */
function handleErrorResponse(error) {
  console.error("Error during fetch:", error);
  showNotification("error", "Có lỗi xảy ra: " + error.message);
}

/**
 * Close modal and redirect or reload page
 */
function closeModalAndRedirect(redirectUrl) {
  ModalUtils.hide("roomModal");

  if (redirectUrl) {
    window.location.href = redirectUrl;
  } else {
    location.reload();
  }
}

/**
 * Reset submit button to original state
 */
function resetSubmitButton(button, originalText) {
  button.disabled = false;
  button.innerHTML = originalText;
}

/**
 * Create FormData with CSRF token
 */
function createFormDataWithCSRF() {
  const formData = new FormData();
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    formData.append("csrf_token", csrfToken);
  }
  return formData;
}

/**
 * Get CSRF token from form or meta tag
 */
function getCSRFToken() {
  // Try multiple sources for CSRF token
  const token =
    document.getElementById("csrfToken")?.value ||
    document.querySelector("meta[name=csrf-token]")?.getAttribute("content") ||
    document.querySelector("input[name=csrf_token]")?.value ||
    "";

  console.log(
    "CSRF Token found:",
    token ? "Yes" : "No",
    token ? "(length: " + token.length + ")" : ""
  );
  return token;
}

// Clear form errors
function clearFormErrors() {
  const errorElements = document.querySelectorAll(".text-danger.small");
  errorElements.forEach((element) => {
    element.textContent = "";
  });
}

// Display form errors
function displayFormErrors(errors) {
  clearFormErrors();

  for (const [field, message] of Object.entries(errors)) {
    const errorElement = document.getElementById(field + "Error");
    if (errorElement) {
      errorElement.textContent = message;
    }
  }
}

// Notification storage utilities
/**
 * Store notification for display after redirect
 */
function storeNotificationForRedirect(type, message) {
  const notification = { type, message };
  sessionStorage.setItem("pendingNotification", JSON.stringify(notification));
}

/**
 * Retrieve and display stored notification, then clear it
 */
function showStoredNotification() {
  const storedNotification = sessionStorage.getItem("pendingNotification");
  if (storedNotification) {
    try {
      const notification = JSON.parse(storedNotification);
      showNotification(notification.type, notification.message);
      sessionStorage.removeItem("pendingNotification");
    } catch (error) {
      console.error("Error parsing stored notification:", error);
      sessionStorage.removeItem("pendingNotification");
    }
  }
}

// Handle form submission when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Check for and display any stored notifications from redirects
  showStoredNotification();

  const roomForm = document.getElementById("roomForm");
  if (roomForm) {
    roomForm.addEventListener("submit", function (e) {
      e.preventDefault();

      console.log(
        "Form submitted, isEditMode:",
        isEditMode,
        "currentRoomId:",
        currentRoomId
      );

      // Create FormData from the form directly
      const formData = new FormData(this);

      // Ensure CSRF token is included
      const csrfToken = getCSRFToken();
      if (csrfToken && !formData.has("csrf_token")) {
        formData.append("csrf_token", csrfToken);
      }

      // Log form data for debugging
      console.log("Form data entries:");
      for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
      }

      const url = isEditMode ? `/rooms/${currentRoomId}/edit` : "/rooms/create";
      console.log("Submitting to URL:", url);

      // Disable submit button
      const submitBtn = document.getElementById("saveRoomBtn");
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

      submitRoomForm(url, formData, submitBtn, originalText);
    });
  }
});
