/**
 * User Operations Manager
 * Simplified approach using module pattern to avoid initialization issues
 */

// User operations module using IIFE (Immediately Invoked Function Expression)
const UserOperations = (function () {
  // Private variables
  let isEditMode = false;
  let currentUserId = null;

  // Configuration
  const config = {
    entityName: "user",
    entityNameDisplay: "người dùng",
    baseUrl: "/users",
    modalPrefix: "user",
    formId: "userForm",
    submitButtonId: "saveUserBtn",
  };

  // Helper functions
  function getRoleText(role) {
    const roleMap = {
      admin: "Quản trị viên",
      management: "Quản lý",
      student: "Sinh viên",
      staff: "Nhân viên",
    };
    return roleMap[role] || role;
  }

  function getRoleBadgeClass(role) {
    const roleClassMap = {
      admin: "bg-danger",
      management: "bg-warning text-dark",
      student: "bg-primary",
      staff: "bg-info text-dark",
    };
    return roleClassMap[role] || "bg-secondary";
  }

  function showNotification(type, message) {
    if (typeof window.showNotification === "function") {
      window.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  // Populate form fields with user data
  function populateForm(user) {
    const fieldMap = {
      fullName: user.full_name,
      email: user.email,
      phoneNumber: user.phone_number,
      studentId: user.student_id,
      role: user.role,
      isActive: user.is_active ? "true" : "false",
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
  }

  // Fetch user data from server
  async function fetchUser(userId) {
    const apiResponse = await APIUtils.get(`${config.baseUrl}/${userId}`);

    if (!apiResponse.success) {
      throw new Error(
        apiResponse.message || `Failed to fetch ${config.entityName} data`
      );
    }

    return apiResponse.data[config.entityName];
  }

  // Prepare template data for user detail view
  function prepareDetailTemplateData(user) {
    return {
      user_id: user.user_id || "N/A",
      full_name: user.full_name || "N/A",
      email: user.email || "N/A",
      phone_number: user.phone_number || "Chưa có",
      student_id: user.student_id || "Chưa có",
      role_badge_class: getRoleBadgeClass(user.role),
      role_text: getRoleText(user.role),
      status_badge_class: user.is_active ? "bg-success" : "bg-secondary",
      status_text: user.is_active ? "Hoạt động" : "Không hoạt động",
      created_at: user.created_at
        ? new Date(user.created_at).toLocaleString("vi-VN")
        : "Chưa có",
    };
  }

  // Toggle field states based on mode
  function toggleFieldsForMode(mode, fieldsToToggle = ["email", "studentId"]) {
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
    console.error("Error during user operation:", error);
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
      console.log("Submitting form to URL:", url);
      console.log("Form data:", Object.fromEntries(formData.entries()));
      const apiResponse = await APIUtils.post(url, formData);
      handleSuccessResponse(apiResponse);
    } catch (error) {
      handleErrorResponse(error);
    } finally {
      FormUtils.resetSubmitButton(submitBtn, originalButtonText);
    }
  }

  // Handle form submission with password validation
  async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const userData = {};

    for (let [key, value] of formData.entries()) {
      userData[key] = value;
    }

    // Convert is_active to boolean
    userData.is_active = userData.is_active === "true";

    // Validate passwords for create mode
    if (!isEditMode) {
      const passwordValidation = ValidationUtils.validatePasswordConfirmation(
        userData.password,
        userData.confirm_password
      );

      if (!passwordValidation.isValid) {
        showNotification("danger", passwordValidation.message);
        return;
      }

      const strengthValidation = ValidationUtils.validatePassword(
        userData.password
      );
      if (!strengthValidation.isValid) {
        showNotification("danger", strengthValidation.message);
        return;
      }
    }

    // Remove confirm_password from data
    delete userData.confirm_password;

    // Create FormData object with user data and CSRF token
    const submitFormData = CSRFUtils.createFormDataWithToken();

    // Add user data to form
    Object.keys(userData).forEach((key) => {
      if (userData[key] !== null && userData[key] !== undefined) {
        submitFormData.append(key, userData[key]);
      }
    });

    // Debug logging (only in development)
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      console.log("FormData contents:");
      for (let [key, value] of submitFormData.entries()) {
        console.log(`  ${key}: ${value}`);
      }
    }

    const url = isEditMode
      ? `${config.baseUrl}/${currentUserId}/edit`
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

    // Open create user modal
    openCreateModal() {
      isEditMode = false;
      currentUserId = null;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);
      const form = document.getElementById(config.formId);

      if (modalLabel) {
        modalLabel.textContent = "Thêm người dùng";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Lưu';
      }

      if (form) {
        form.reset();
      }

      // Show password section for create mode
      const passwordSection = document.getElementById("passwordSection");
      const passwordField = document.getElementById("password");
      const confirmPasswordField = document.getElementById("confirmPassword");

      if (passwordSection) passwordSection.style.display = "block";
      if (passwordField) passwordField.required = true;
      if (confirmPasswordField) confirmPasswordField.required = true;

      // Enable all fields for create mode
      toggleFieldsForMode("create");

      FormUtils.clearErrors();
    },

    // Open edit user modal
    async openEditModal(userId) {
      userId = parseInt(userId);

      isEditMode = true;
      currentUserId = userId;

      const modalLabel = document.getElementById(
        `${config.modalPrefix}ModalLabel`
      );
      const saveBtn = document.getElementById(config.submitButtonId);

      if (modalLabel) {
        modalLabel.textContent = "Chỉnh sửa người dùng";
      }

      if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Cập nhật';
      }

      // Hide password section for edit mode
      const passwordSection = document.getElementById("passwordSection");
      const passwordField = document.getElementById("password");
      const confirmPasswordField = document.getElementById("confirmPassword");

      if (passwordSection) passwordSection.style.display = "none";
      if (passwordField) passwordField.required = false;
      if (confirmPasswordField) confirmPasswordField.required = false;

      // Disable non-updatable fields in edit mode
      toggleFieldsForMode("edit");

      FormUtils.clearErrors();

      // Show modal
      ModalUtils.show(`${config.modalPrefix}Modal`);

      try {
        // Load user data
        const user = await fetchUser(userId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log("Loaded user data:", user);
        }

        // Populate form with user data
        populateForm(user);
      } catch (error) {
        showNotification("error", "Lỗi: " + error.message);
        ModalUtils.hide(`${config.modalPrefix}Modal`);
      }
    },

    // View user details
    async viewEntityDetails(userId) {
      userId = parseInt(userId);

      // Show the modal first
      ModalUtils.show(`${config.modalPrefix}DetailModal`);

      // Show loading state
      TemplateUtils.showLoading(
        `${config.modalPrefix}DetailContent`,
        `${config.modalPrefix}DetailLoadingTemplate`
      );

      try {
        const user = await fetchUser(userId);

        // Debug logging (only in development)
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          console.log(`Loaded ${config.entityName} data for details:`, user);
        }

        // Prepare template data
        const templateData = prepareDetailTemplateData(user);

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

// Export to global scope for backward compatibility
window.UserOperations = UserOperations;

// Global function wrappers for template compatibility
window.openCreateUserModal = function () {
  UserOperations.openCreateModal();
};

window.openEditUserModal = function (userId) {
  UserOperations.openEditModal(userId);
};

window.viewUserDetails = function (userId) {
  UserOperations.viewEntityDetails(userId);
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  UserOperations.init();
});

// Legacy compatibility - these functions are kept for backwards compatibility
// But they now delegate to the utility modules

/**
 * @deprecated Use NotificationUtils.storeForRedirect instead
 */
function storeNotificationForRedirect(type, message) {
  NotificationUtils.storeForRedirect(type, message);
}

/**
 * @deprecated Use NotificationUtils.showStored instead
 */
function showStoredNotification() {
  NotificationUtils.showStored((type, message) => {
    if (typeof window.showNotification === "function") {
      window.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  });
}

/**
 * @deprecated Use CSRFUtils.createFormDataWithToken instead
 */
function createFormDataWithCSRF() {
  return CSRFUtils.createFormDataWithToken();
}

/**
 * @deprecated Use CSRFUtils.getToken instead
 */
function getCSRFToken() {
  return CSRFUtils.getToken();
}
