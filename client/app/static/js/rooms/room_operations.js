/**
 * Room Operations Manager
 * Simplified approach using module pattern to avoid initialization issues
 */

// Room operations module using IIFE (Immediately Invoked Function Expression)
const RoomOperations = (function () {
  // Private variables
  let isEditMode = false;
  let currentRoomId = null;

  // Configuration
  const config = {
    entityName: "room",
    entityNameDisplay: "phòng",
    baseUrl: "/rooms",
    modalPrefix: "room",
    formId: "roomForm",
    submitButtonId: "saveRoomBtn",
  };

  // Helper functions
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

  function showNotification(type, message) {
    if (typeof window.showNotification === "function") {
      window.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  // Load buildings and room types for dropdowns
  async function loadBuildingsAndRoomTypes() {
    try {
      // Load buildings
      const buildingsResponse = await APIUtils.get("/buildings");

      console.log("Fetched buildings data:", buildingsResponse);

      // Check if response has expected structure
      if (!buildingsResponse.data || !buildingsResponse.data.buildings) {
        throw new Error("Invalid response structure for buildings");
      }

      const buildings = buildingsResponse.data.buildings;

      const buildingSelect = document.getElementById("buildingId");
      if (buildingSelect) {
        buildingSelect.innerHTML = '<option value="">Chọn tòa nhà</option>';
        buildings.forEach((building) => {
          const option = document.createElement("option");
          option.value = building.building_id;
          option.textContent = building.building_name;
          buildingSelect.appendChild(option);
        });
      }

      // Load room types
      const roomTypesResponse = await APIUtils.get("/room-types");

      // Check if response has expected structure
      if (!roomTypesResponse.data || !roomTypesResponse.data.room_types) {
        throw new Error("Invalid response structure for room types");
      }

      const roomTypes = roomTypesResponse.data.room_types;

      const roomTypeSelect = document.getElementById("roomTypeId");
      if (roomTypeSelect) {
        roomTypeSelect.innerHTML = '<option value="">Chọn loại phòng</option>';
        roomTypes.forEach((roomType) => {
          const option = document.createElement("option");
          option.value = roomType.room_type_id;
          option.textContent = `${roomType.type_name} (${roomType.capacity} người)`;
          roomTypeSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error("Error loading buildings and room types:", error);

      // Provide more specific error messages
      let errorMessage = "Có lỗi khi tải danh sách tòa nhà và loại phòng";

      if (error.message.includes("500")) {
        errorMessage +=
          " - Lỗi máy chủ nội bộ. Vui lòng liên hệ quản trị viên.";
      } else if (error.message.includes("404")) {
        errorMessage +=
          " - Không tìm thấy endpoint. Vui lòng kiểm tra đường dẫn API.";
      } else if (error.message.includes("Expected JSON")) {
        errorMessage += " - Máy chủ trả về dữ liệu không hợp lệ.";
      }

      showNotification("error", errorMessage);

      // Set fallback options for dropdowns if they exist
      const buildingSelect = document.getElementById("buildingId");
      const roomTypeSelect = document.getElementById("roomTypeId");

      if (buildingSelect) {
        buildingSelect.innerHTML =
          '<option value="">Không thể tải danh sách tòa nhà</option>';
      }

      if (roomTypeSelect) {
        roomTypeSelect.innerHTML =
          '<option value="">Không thể tải danh sách loại phòng</option>';
      }
    }
  }

  // Populate form fields with room data
  function populateForm(room) {
    const fieldMap = {
      roomNumber: room.room_number,
      buildingId: room.building_id,
      roomTypeId: room.room_type_id,
      status: room.status,
      description: room.description,
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
  }

  // Fetch room data from server
  async function fetchRoom(roomId) {
    const apiResponse = await APIUtils.get(`${config.baseUrl}/${roomId}`);

    console.log("Fetched room data:", apiResponse);

    if (!apiResponse.success) {
      throw new Error(
        apiResponse.message || `Failed to fetch ${config.entityName} data`
      );
    }

    return apiResponse.data[config.entityName];
  }

  // Prepare template data for room detail view
  function prepareDetailTemplateData(room) {
    return {
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
  }

  // Toggle field states based on mode
  function toggleFieldsForMode(
    mode,
    fieldsToToggle = ["roomNumber", "buildingId"]
  ) {
    fieldsToToggle.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        if (mode === "edit") {
          field.disabled = true;
          field.style.backgroundColor = "#f8f9fa";
        } else {
          field.disabled = false;
          field.style.backgroundColor = "";
        }
      }
    });
  }

  // Handle successful response
  function handleSuccessResponse(data) {
    if (data.success) {
      NotificationUtils.storeForRedirect(
        "success",
        data.message || "Thao tác thành công!"
      );
      closeModalAndRedirect(data.redirect);
    } else {
      if (data.errors) {
        FormUtils.displayErrors(data.errors);
      } else {
        showNotification("error", "Lỗi: " + (data.message || "Có lỗi xảy ra"));
      }
    }
  }

  // Handle error response
  function handleErrorResponse(error) {
    console.error("Error during room operation:", error);
    showNotification("error", "Có lỗi xảy ra: " + error.message);
  }

  // Close modal and redirect
  function closeModalAndRedirect(redirectUrl) {
    // Hide the modal with enhanced cleanup
    ModalUtils.hide(`${config.modalPrefix}Modal`);

    // Force cleanup to ensure backdrop is removed
    setTimeout(() => {
      ModalUtils.cleanupBackdrop();
    }, 100);

    // Small delay before redirect to ensure modal is fully closed
    setTimeout(() => {
      if (redirectUrl) {
        window.location.href = redirectUrl;
      } else {
        window.location.reload();
      }
    }, 200);
  }

  // Submit form data to server
  async function submitForm(url, formData, submitBtn, originalButtonText) {
    try {
      const apiResponse = await APIUtils.post(url, formData);
      handleSuccessResponse(apiResponse);
    } catch (error) {
      handleErrorResponse(error);
    } finally {
      FormUtils.resetSubmitButton(submitBtn, originalButtonText);
    }
  }

  // Handle form submission
  async function handleFormSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Ensure CSRF token is included
    CSRFUtils.ensureTokenInFormData(formData);

    const url = isEditMode
      ? `${config.baseUrl}/${currentRoomId}/edit`
      : `${config.baseUrl}/create`;

    // Set button to loading state
    const submitBtn = document.getElementById(config.submitButtonId);
    const originalText = submitBtn ? submitBtn.innerHTML : "";
    FormUtils.setSubmitButtonLoading(submitBtn);

    await submitForm(url, formData, submitBtn, originalText);
  }

  // Public interface
  return {
    // Initialize the module
    init() {
      // Set up form submission
      const form = document.getElementById(config.formId);
      if (form) {
        form.addEventListener("submit", handleFormSubmit);
      }

      // Set up stored notifications
      const showNotificationFn = (type, message) => {
        showNotification(type, message);
      };
      NotificationUtils.showStored(showNotificationFn);
    },

    // Open create room modal
    async openCreateModal() {
      isEditMode = false;
      currentRoomId = null;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);
      const form = document.getElementById(config.formId);
      const roomIdField = document.getElementById("roomId");

      if (modalLabel) {
        modalLabel.textContent = "Thêm phòng mới";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Lưu';
      }

      if (form) {
        form.reset();
      }

      if (roomIdField) {
        roomIdField.value = "";
      }

      // Enable all fields for create mode
      toggleFieldsForMode("create");

      FormUtils.clearErrors();

      // Load dropdowns (don't block modal opening if this fails)
      try {
        await loadBuildingsAndRoomTypes();
      } catch (error) {
        console.warn(
          "Failed to load dropdowns, but continuing with modal open:",
          error
        );
      }

      // Show modal after attempting to load dropdowns
      ModalUtils.show(`${config.modalPrefix}Modal`);
    },

    // Open edit room modal
    async openEditModal(roomId) {
      roomId = parseInt(roomId);

      isEditMode = true;
      currentRoomId = roomId;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);
      const roomIdField = document.getElementById("roomId");

      if (modalLabel) {
        modalLabel.textContent = "Chỉnh sửa phòng";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Cập nhật';
      }

      if (roomIdField) {
        roomIdField.value = roomId;
      }

      // Disable non-updatable fields in edit mode
      toggleFieldsForMode("edit");

      FormUtils.clearErrors();

      // Load dropdowns first (don't block modal opening if this fails)
      try {
        await loadBuildingsAndRoomTypes();
      } catch (error) {
        console.warn(
          "Failed to load dropdowns, but continuing with modal open:",
          error
        );
      }

      // Show modal
      ModalUtils.show(`${config.modalPrefix}Modal`);

      try {
        // Load room data
        const room = await fetchRoom(roomId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log("Loaded room data:", room);
        }

        // Populate form with room data
        populateForm(room);
      } catch (error) {
        showNotification("error", "Lỗi: " + error.message);
        ModalUtils.hide(`${config.modalPrefix}Modal`);
      }
    },

    // View room details
    async viewEntityDetails(roomId) {
      roomId = parseInt(roomId);

      // Show the modal first
      ModalUtils.show(`${config.modalPrefix}DetailModal`);

      // Show loading state
      TemplateUtils.showLoading(
        `${config.modalPrefix}DetailContent`,
        `${config.modalPrefix}DetailLoadingTemplate`
      );

      try {
        const room = await fetchRoom(roomId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log(`Loaded ${config.entityName} data for details:`, room);
        }

        // Prepare template data
        const templateData = prepareDetailTemplateData(room);

        // Render and display template
        const renderedTemplate = TemplateUtils.render(
          `${config.modalPrefix}DetailTemplate`,
          templateData
        );

        document.getElementById(
          `${config.modalPrefix}DetailContent`
        ).innerHTML = renderedTemplate;
      } catch (error) {
        console.error(`Error fetching ${config.entityName} data:`, error);
        TemplateUtils.showError(
          `${config.modalPrefix}DetailContent`,
          `${config.modalPrefix}DetailErrorTemplate`,
          error.message ||
            `Có lỗi xảy ra khi tải thông tin ${config.entityNameDisplay}`
        );
      }
    },
  };
})();

// Export to global scope for backward compatibility
window.RoomOperations = RoomOperations;

// Function to open create room modal
function openCreateRoomModal() {
  RoomOperations.openCreateModal();
}

// Function to open edit room modal
async function openEditRoomModal(roomId) {
  await RoomOperations.openEditModal(roomId);
}

// Function to view room details
async function viewRoomDetails(roomId) {
  await RoomOperations.viewEntityDetails(roomId);
}

// Function to open delete room modal
function openDeleteRoomModal(button) {
  const roomId = button.getAttribute("data-room-id");
  const roomNumber = button.getAttribute("data-room-number");

  document.getElementById("roomToDelete").textContent = roomNumber;
  document.getElementById("deleteRoomForm").action = `/rooms/${roomId}/delete`;
}

// Handle form submission when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  RoomOperations.init();
});
