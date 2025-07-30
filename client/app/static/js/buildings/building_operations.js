// Building management JavaScript functions
let isEditMode = false;

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
 * Building data management utilities
 */
const BuildingDataUtils = {
  /**
   * Fetch building data from server
   */
  async fetchBuilding(buildingId) {
    const response = await fetch(`/buildings/${buildingId}`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });

    const apiResponse = await response.json();
    console.log("Fetched building API response:", apiResponse);

    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Failed to fetch building data");
    }

    // Backend returns: {success, message, data: {building: {...}}, status_code}
    // We want just the building object
    return apiResponse.data.building;
  },  

  /**
   * Populate form fields with building data
   */
  populateForm(building) {
    const fieldMap = {
      buildingName: building.building_name,
      description: building.description
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
  },
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
  },
};

// Function to open create building modal
function openCreateBuildingModal() {
  isEditMode = false;
  currentBuildingId = null;
  document.getElementById("buildingModalLabel").textContent =
    "Thêm tòa nhà mới";
  document.getElementById("saveBuildingBtn").innerHTML =
    '<i class="fas fa-save"></i> Lưu';
  document.getElementById("buildingForm").reset();
  document.getElementById("buildingId").value = "";

  // Enable all fields for create mode
  const buildingNameField = document.getElementById("buildingName");

  if (buildingNameField) {
    buildingNameField.disabled = false;
    buildingNameField.style.backgroundColor = ""; // Reset background
  }

  clearFormErrors();
}

// Function to open edit building modal
async function openEditBuildingModal(buildingId) {
  // Convert string to number if needed
  buildingId = parseInt(buildingId);

  isEditMode = true;
  currentBuildingId = buildingId;
  document.getElementById("buildingModalLabel").textContent =
    "Chỉnh sửa tòa nhà";
  document.getElementById("saveBuildingBtn").innerHTML =
    '<i class="fas fa-save"></i> Cập nhật';
  document.getElementById("buildingId").value = buildingId;

  clearFormErrors();

  // Show modal
  ModalUtils.show("buildingModal");

  try {
    // Load building data
    const building = await BuildingDataUtils.fetchBuilding(buildingId);
    console.log("Loaded building data:", building);

    // Populate form with building data
    BuildingDataUtils.populateForm(building);
  } catch (error) {
    showNotification("error", "Lỗi: " + error.message);
    ModalUtils.hide("buildingModal");
  }
}

// Function to view building details
async function viewBuildingDetails(buildingId) {
  // Convert string to number if needed
  buildingId = parseInt(buildingId);

  // Show the modal first
  ModalUtils.show("buildingDetailModal");

  // Show loading state
  TemplateUtils.showLoading(
    "buildingDetailContent",
    "buildingDetailLoadingTemplate"
  );

  try {
    const building = await BuildingDataUtils.fetchBuilding(buildingId);
    console.log("Loaded building data for details:", building);

    // Prepare template data
    const templateData = {
      building_id: building.building_id || "N/A",
      building_name: building.building_name || "N/A",
      description: building.description || "Không có mô tả",
      room_count: building.total_rooms || 0,
      available_rooms: building.available_rooms || 0,
      created_at: building.created_at
        ? new Date(building.created_at).toLocaleString("vi-VN")
        : "Chưa có",
    };


    // Render and display template
    const renderedTemplate = TemplateUtils.render(
      "buildingDetailTemplate",
      templateData
    );

    document.getElementById("buildingDetailContent").innerHTML =
      renderedTemplate;
  } catch (error) {
    console.error("Error fetching building data:", error);
    TemplateUtils.showError(
      "buildingDetailContent",
      "buildingDetailErrorTemplate",
      error.message || "Có lỗi xảy ra khi tải thông tin tòa nhà"
    );
  }
}

// Function to open delete building modal
function openDeleteBuildingModal(button) {
  const buildingId = button.getAttribute("data-building-id");
  const buildingName = button.getAttribute("data-building-name");

  document.getElementById("buildingToDelete").textContent = buildingName;
  document.getElementById(
    "deleteBuildingForm"
  ).action = `/buildings/${buildingId}/delete`;
}

/**
 * Handle form submission with proper error handling and UI feedback
 */
async function submitBuildingForm(
  url,
  formData,
  submitBtn,
  originalButtonText
) {
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
  ModalUtils.hide("buildingModal");

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

  const buildingForm = document.getElementById("buildingForm");
  if (buildingForm) {
    buildingForm.addEventListener("submit", function (e) {
      e.preventDefault();

      console.log(
        "Form submitted, isEditMode:",
        isEditMode,
        "currentBuildingId:",
        currentBuildingId
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

      const url = isEditMode
        ? `/buildings/${currentBuildingId}/edit`
        : "/buildings/create";
      console.log("Submitting to URL:", url);

      // Disable submit button
      const submitBtn = document.getElementById("saveBuildingBtn");
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

      submitBuildingForm(url, formData, submitBtn, originalText);
    });
  }

  // Handle building modal events (legacy support)
  const buildingModal = document.getElementById("buildingModal");
  if (buildingModal) {
    buildingModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (button) {
        const isEdit = button.classList.contains("edit-building");

        if (isEdit) {
          const buildingId = button.getAttribute("data-id");
          if (buildingId) {
            openEditBuildingModal(buildingId);
          }
        } else {
          openCreateBuildingModal();
        }
      }
    });
  }

  // Handle delete building modal (legacy support)
  const deleteBuildingModal = document.getElementById("deleteBuildingModal");
  if (deleteBuildingModal) {
    deleteBuildingModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (button) {
        openDeleteBuildingModal(button);
      }
    });
  }
});
