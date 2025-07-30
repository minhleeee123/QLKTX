// Function to open create user modal
function openCreateUserModal() {
  isEditMode = false;
  currentUserId = null;
  document.getElementById("userModalLabel").textContent = "Thêm người dùng";
  document.getElementById("saveUserBtn").innerHTML =
    '<i class="fas fa-save"></i> Lưu';
  document.getElementById("userForm").reset();
  document.getElementById("passwordSection").style.display = "block";
  document.getElementById("password").required = true;
  document.getElementById("confirmPassword").required = true;
}

// Function to open edit user modal
async function openEditUserModal(userId) {
  // Convert string to number if needed
  userId = parseInt(userId);

  isEditMode = true;
  currentUserId = userId;
  document.getElementById("userModalLabel").textContent = "Chỉnh sửa người dùng";
  document.getElementById("saveUserBtn").innerHTML = '<i class="fas fa-save"></i> Cập nhật';
  document.getElementById("passwordSection").style.display = "none";
  document.getElementById("password").required = false;
  document.getElementById("confirmPassword").required = false;

  // Show modal
  const modal = ModalUtils.show("userModal");

  try {
    // Load user data
    const user = await UserDataUtils.fetchUser(userId);
    console.log("Loaded user data:", user);
    
    // Populate form with user data
    UserDataUtils.populateForm(user);
  } catch (error) {
    alert("Lỗi: " + error.message);
    ModalUtils.hide("userModal");
  }
}

// Function to view user details
async function viewUserDetails(userId) {
  // Convert string to number if needed
  userId = parseInt(userId);

  // Show the modal first
  ModalUtils.show("userDetailModal");

  // Show loading state
  TemplateUtils.showLoading("userDetailContent", "userDetailLoadingTemplate");

  try {
    const user = await UserDataUtils.fetchUser(userId);
    
    // Prepare template data
    const templateData = {
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
        : "Chưa có"
    };

    // Render and display template
    const renderedTemplate = TemplateUtils.render("userDetailTemplate", templateData);
    document.getElementById("userDetailContent").innerHTML = renderedTemplate;
    
  } catch (error) {
    console.error("Error fetching user data:", error);
    TemplateUtils.showError(
      "userDetailContent", 
      "userDetailErrorTemplate", 
      error.message || "Có lỗi xảy ra khi tải thông tin người dùng"
    );
  }
}

// Helper function to get role text
function getRoleText(role) {
  const roleMap = {
    admin: "Quản trị viên",
    management: "Quản lý",
    student: "Sinh viên",
    staff: "Nhân viên",
  };
  return roleMap[role] || role;
}

// Helper function to get role badge class
function getRoleBadgeClass(role) {
  const roleClassMap = {
    admin: "bg-danger",
    management: "bg-warning text-dark",
    student: "bg-primary",
    staff: "bg-info text-dark",
  };
  return roleClassMap[role] || "bg-secondary";
}

// Delete user function
function deleteUser(userId, userName) {
  // Convert string to number if needed
  userId = parseInt(userId);

  if (confirm(`Bạn có chắc chắn muốn xóa người dùng "${userName}"?`)) {
    // Create FormData with CSRF token
    const formData = createFormDataWithCSRF();

    fetch(`/users/${userId}/delete`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    })
      .then((response) => handleResponse(response))
      .then((data) => handleSuccessResponse(data))
      .catch((error) => handleErrorResponse(error));
  }
}

// Handle form submission when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  const userForm = document.getElementById("userForm");
  if (userForm) {
    userForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const userData = {};

      for (let [key, value] of formData.entries()) {
        userData[key] = value;
      }

      // Convert is_active to boolean
      userData.is_active = userData.is_active === "true";

      // Validate passwords for create mode
      if (!isEditMode) {
        if (userData.password !== userData.confirm_password) {
          showNotification("danger", "Mật khẩu xác nhận không khớp!");
          return;
        }

        if (userData.password.length < 6) {
          showNotification("danger", "Mật khẩu phải có ít nhất 6 ký tự!");
          return;
        }
      }

      // Remove confirm_password from data
      delete userData.confirm_password;

      // Create FormData object with user data and CSRF token
      const submitFormData = createFormDataWithCSRF();

      // Add user data to form
      Object.keys(userData).forEach((key) => {
        if (userData[key] !== null && userData[key] !== undefined) {
          submitFormData.append(key, userData[key]);
        }
      });

      const url = isEditMode ? `/users/${currentUserId}/edit` : "/users/create";
      const method = "POST";

      // Disable submit button
      const submitBtn = document.getElementById("saveUserBtn");
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

      submitUserForm(url, submitFormData, submitBtn, originalText);
    });
  }
});

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
  }
};

/**
 * User data management utilities
 */
const UserDataUtils = {
  /**
   * Fetch user data from server
   */
  async fetchUser(userId) {
    const response = await fetch(`/users/${userId}`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });
    
    const data = await response.json();
    console.log(response)
    console.log("Fetched user data:", data);
    
    if (!data.success) {
      throw new Error(data.message || "Failed to fetch user data");
    }
    
    // Backend returns: {success, message, data: {user: {...}}, status_code}
    // We want just the user object
    return data.user;
  },

  /**
   * Populate form fields with user data
   */
  populateForm(user) {
    const fieldMap = {
      fullName: user.full_name,
      email: user.email,
      phoneNumber: user.phone_number,
      studentId: user.student_id,
      role: user.role,
      isActive: user.is_active ? "true" : "false"
    };

    Object.entries(fieldMap).forEach(([fieldId, value]) => {
      const element = document.getElementById(fieldId);
      if (element) {
        element.value = value || "";
      }
    });
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

/**
 * Handle form submission with proper error handling and UI feedback
 */
async function submitUserForm(url, formData, submitBtn, originalButtonText) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    });

    const data = await handleResponse(response);
    handleSuccessResponse(data);
  } catch (error) {
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
  if (data.success) {
    closeModalAndRedirect(data.redirect);
  } else {
    if (data.redirect) {
      window.location.href = data.redirect;
    } else {
      showNotification("danger", "Lỗi: " + data.message);
    }
  }
}

/**
 * Handle error response
 */
function handleErrorResponse(error) {
  console.error("Error during fetch:", error);
  showNotification("danger", "Có lỗi xảy ra: " + error.message);
}

/**
 * Close modal and redirect or reload page
 */
function closeModalAndRedirect(redirectUrl) {
  ModalUtils.hide("userModal");
  
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
  return (
    document.getElementById("csrfToken")?.value ||
    document.querySelector("meta[name=csrf-token]")?.getAttribute("content") ||
    ""
  );
}
