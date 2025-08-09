/**
 * Building Operations Manager
 * Extends BaseOperations for building-specific functionality
 */
/**
 * Building Operations Manager
 * Simplified approach using module pattern to avoid initialization issues
 */

// Building operations module using IIFE (Immediately Invoked Function Expression)
const BuildingOperations = (function () {
  // Private variables
  let isEditMode = false;
  let currentBuildingId = null;

  // Configuration
  const config = {
    entityName: "building",
    entityNameDisplay: "tòa nhà",
    baseUrl: "/buildings",
    modalPrefix: "building",
    formId: "buildingForm",
    submitButtonId: "saveBuildingBtn",
  };

  function showNotification(type, message) {
    if (typeof window.showNotification === "function") {
      window.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  // Populate form fields with building data
  function populateForm(building) {
    const fieldMap = {
      buildingName: building.building_name,
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
  }

  // Fetch building data from server
  async function fetchBuilding(buildingId) {
    const apiResponse = await APIUtils.get(`${config.baseUrl}/${buildingId}`);

    console.log("Fetched building data:", apiResponse);

    if (!apiResponse.success) {
      throw new Error(
        apiResponse.message || `Failed to fetch ${config.entityName} data`
      );
    }

    return apiResponse.data[config.entityName];
  }

  // Prepare template data for building detail view
  function prepareDetailTemplateData(building) {
    return {
      building_id: building.building_id || "N/A",
      building_name: building.building_name || "N/A",
      total_rooms: building.total_rooms || 0,
      available_rooms: building.available_rooms || 0,
      occupied_rooms: building.occupied_rooms || 0,
    };
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
    console.error("Error during building operation:", error);
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
    console.log("Submitting form to:", url);
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

    const formData = new FormData(e.target);
    const buildingData = {};

    for (let [key, value] of formData.entries()) {
      buildingData[key] = value;
    }

    // Get CSRF token with multiple fallback options
    let csrfToken = null;

    // Try to get from meta tag first
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
      csrfToken = csrfMeta.getAttribute("content");
    }

    // Fallback 1: try to get from hidden input in building form
    if (!csrfToken) {
      const csrfInput = document.querySelector(
        '#buildingForm input[name="csrf_token"]'
      );
      if (csrfInput) {
        csrfToken = csrfInput.value;
      }
    }

    // Fallback 2: try to get from any hidden input with name csrf_token
    if (!csrfToken) {
      const csrfInputAny = document.querySelector('input[name="csrf_token"]');
      if (csrfInputAny) {
        csrfToken = csrfInputAny.value;
      }
    }

    // Fallback 3: try to get from element with id csrfToken
    if (!csrfToken) {
      const csrfInputId = document.getElementById("csrfToken");
      if (csrfInputId) {
        csrfToken = csrfInputId.value;
      }
    }

    console.log("Building form - CSRF Token found:", csrfToken ? "Yes" : "No");
    console.log("Building form - CSRF Token value:", csrfToken);

    // Create FormData object with building data and CSRF token
    const submitFormData = new FormData();

    // Add CSRF token if found
    if (csrfToken) {
      submitFormData.append("csrf_token", csrfToken);
    }

    // Add building data to form (only building_name exists in server model)
    if (
      buildingData.building_name !== null &&
      buildingData.building_name !== undefined
    ) {
      submitFormData.append("building_name", buildingData.building_name);
    }

    const url = isEditMode
      ? `${config.baseUrl}/${currentBuildingId}/edit`
      : `${config.baseUrl}/create`;

    // Set button to loading state
    const submitBtn = document.getElementById(config.submitButtonId);
    const originalText = submitBtn ? submitBtn.innerHTML : "";
    FormUtils.setSubmitButtonLoading(submitBtn);

    await submitForm(url, submitFormData, submitBtn, originalText);
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

    // Open create building modal
    openCreateModal() {
      console.log("Opening create building modal...");
      isEditMode = false;
      currentBuildingId = null;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);
      const form = document.getElementById(config.formId);

      if (modalLabel) {
        modalLabel.textContent = "Thêm tòa nhà";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Lưu';
      }

      if (form) {
        form.reset();
      }

      FormUtils.clearErrors();
    },

    // Open edit building modal
    async openEditModal(buildingId) {
      buildingId = parseInt(buildingId);

      isEditMode = true;
      currentBuildingId = buildingId;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);

      if (modalLabel) {
        modalLabel.textContent = "Chỉnh sửa tòa nhà";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Cập nhật';
      }

      FormUtils.clearErrors();

      // Show modal
      ModalUtils.show(`${config.modalPrefix}Modal`);

      try {
        // Load building data
        const building = await fetchBuilding(buildingId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log("Loaded building data:", building);
        } // Populate form with building data
        populateForm(building);
      } catch (error) {
        showNotification("error", "Lỗi: " + error.message);
        ModalUtils.hide(`${config.modalPrefix}Modal`);
      }
    },

    // View building details
    async viewEntityDetails(buildingId) {
      buildingId = parseInt(buildingId);

      // Show the modal first
      ModalUtils.show(`${config.modalPrefix}DetailModal`);

      // Show loading state
      TemplateUtils.showLoading(
        `${config.modalPrefix}DetailContent`,
        `${config.modalPrefix}DetailLoadingTemplate`
      );

      try {
        const building = await fetchBuilding(buildingId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log(
            `Loaded ${config.entityName} data for details:`,
            building
          );
        }

        // Prepare template data
        const templateData = prepareDetailTemplateData(building);

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

    // Handle success response (for external use like delete operations)
    handleSuccessResponse: handleSuccessResponse,

    // Handle error response (for external use like delete operations)
    handleErrorResponse: handleErrorResponse,
  };
})();

// Global functions for building operations
window.openCreateBuildingModal = function () {
  BuildingOperations.openCreateModal();
};

window.openEditBuildingModal = function (buildingId) {
  BuildingOperations.openEditModal(buildingId);
};

window.viewBuildingDetails = function (buildingId) {
  BuildingOperations.viewEntityDetails(buildingId);
};

window.openDeleteBuildingModal = function (button) {
  const buildingId = button.getAttribute("data-building-id");
  const buildingName = button.getAttribute("data-building-name");

  document.getElementById("buildingToDelete").textContent = buildingName;

  // Store the building ID for the delete function instead of setting form action
  document
    .getElementById("deleteBuildingForm")
    .setAttribute("data-building-id", buildingId);
};

// Function to handle building deletion via AJAX
async function performDeleteBuilding(buildingId) {
  console.log("Attempting to delete building with ID:", buildingId);

  try {
    // Get CSRF token with multiple fallback options
    let csrfToken = null;

    // Try to get from meta tag first
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
      csrfToken = csrfMeta.getAttribute("content");
    }

    // Fallback 1: try to get from hidden input in delete form
    if (!csrfToken) {
      const csrfInput = document.querySelector(
        '#deleteBuildingForm input[name="csrf_token"]'
      );
      if (csrfInput) {
        csrfToken = csrfInput.value;
      }
    }

    // Fallback 2: try to get from any hidden input with name csrf_token
    if (!csrfToken) {
      const csrfInputAny = document.querySelector('input[name="csrf_token"]');
      if (csrfInputAny) {
        csrfToken = csrfInputAny.value;
      }
    }

    // Fallback 3: try to get from element with id csrfToken
    if (!csrfToken) {
      const csrfInputId = document.getElementById("csrfToken");
      if (csrfInputId) {
        csrfToken = csrfInputId.value;
      }
    }

    console.log(
      "Building delete - CSRF Token found:",
      csrfToken ? "Yes" : "No"
    );
    console.log("Building delete - CSRF Token value:", csrfToken);

    // Prepare form data with CSRF token
    const formData = new FormData();
    if (csrfToken) {
      formData.append("csrf_token", csrfToken);
    }

    const headers = {
      "X-Requested-With": "XMLHttpRequest",
    };

    const response = await fetch(`/buildings/${buildingId}/delete`, {
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
      // Hide the modal first
      const deleteModal = bootstrap.Modal.getInstance(
        document.getElementById("deleteBuildingModal")
      );
      if (deleteModal) {
        deleteModal.hide();
      }

      // Show success notification
      if (typeof window.showNotification === "function") {
        window.showNotification(
          "success",
          data.message || "Xóa tòa nhà thành công"
        );
      } else {
        console.log("SUCCESS: " + (data.message || "Xóa tòa nhà thành công"));
      }

      // Reload page to refresh data
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      if (typeof window.showNotification === "function") {
        window.showNotification(
          "danger",
          data.message || "Không thể xóa tòa nhà"
        );
      } else {
        alert(data.message || "Không thể xóa tòa nhà");
      }
    }
  } catch (error) {
    console.error("Error deleting building:", error);
    if (typeof window.showNotification === "function") {
      window.showNotification("danger", "Lỗi kết nối. Vui lòng thử lại.");
    } else {
      alert("Lỗi kết nối. Vui lòng thử lại.");
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  BuildingOperations.init();

  // Handle delete form submission
  const deleteForm = document.getElementById("deleteBuildingForm");
  if (deleteForm) {
    deleteForm.addEventListener("submit", function (e) {
      e.preventDefault(); // Prevent default form submission
      const buildingId = this.getAttribute("data-building-id");
      if (buildingId) {
        performDeleteBuilding(buildingId);
      }
    });
  }
});

// Export to global scope for backward compatibility
window.BuildingOperations = BuildingOperations;

// Global function wrappers for template compatibility
window.openCreateBuildingModal = function () {
  BuildingOperations.openCreateModal();
};

window.openEditBuildingModal = function (buildingId) {
  BuildingOperations.openEditModal(buildingId);
};

window.viewBuildingDetails = function (buildingId) {
  BuildingOperations.viewEntityDetails(buildingId);
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  BuildingOperations.init();
});

// Initialize building operations - moved to avoid temporal dead zone issues
// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  BuildingOperations.init();
});
