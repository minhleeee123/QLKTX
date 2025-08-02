/**
 * Shared Utility Functions
 * Common utilities used across different operation modules
 */

/**
 * Template utilities for rendering dynamic content
 */
const TemplateUtils = {
  /**
   * Replace template placeholders with data
   * @param {string} templateId - ID of the template element
   * @param {Object} data - Data object to replace placeholders
   * @returns {string} Rendered template string
   */
  render(templateId, data) {
    let template = document.getElementById(templateId).innerHTML;

    Object.entries(data).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      template = template.replaceAll(placeholder, value || "");
    });

    return template;
  },

  /**
   * Show loading template in container
   * @param {string} containerId - ID of container element
   * @param {string} loadingTemplateId - ID of loading template
   */
  showLoading(containerId, loadingTemplateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(loadingTemplateId).innerHTML;
    if (container && template) {
      container.innerHTML = template;
    }
  },

  /**
   * Show error template in container
   * @param {string} containerId - ID of container element
   * @param {string} errorTemplateId - ID of error template
   * @param {string} message - Error message to display
   */
  showError(containerId, errorTemplateId, message) {
    const container = document.getElementById(containerId);
    if (container) {
      const template = this.render(errorTemplateId, { message });
      container.innerHTML = template;
    }
  },
};

/**
 * Modal management utilities for Bootstrap modals
 */
const ModalUtils = {
  /**
   * Show modal with proper cleanup handling
   * @param {string} modalId - ID of the modal element
   * @param {Function} cleanupCallback - Optional cleanup callback
   * @returns {Object} Bootstrap modal instance
   */
  show(modalId, cleanupCallback = null) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
      console.error(`Modal element with ID '${modalId}' not found`);
      return null;
    }

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
   * @param {string} modalId - ID of the modal element
   */
  hide(modalId) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
      console.error(`Modal element with ID '${modalId}' not found`);
      return;
    }

    const modal = bootstrap.Modal.getInstance(modalElement);
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

/**
 * CSRF token management utilities
 */
const CSRFUtils = {
  /**
   * Get CSRF token from various sources
   * @returns {string} CSRF token or empty string
   */
  getToken() {
    const token =
      document.getElementById("csrfToken")?.value ||
      document.querySelector("meta[name=csrf-token]")?.getAttribute("content") ||
      document.querySelector("input[name=csrf_token]")?.value ||
      "";

    if (process.env.NODE_ENV === 'development') {
      console.log(
        "CSRF Token found:",
        token ? "Yes" : "No",
        token ? "(length: " + token.length + ")" : ""
      );
    }
    
    return token;
  },

  /**
   * Create FormData with CSRF token
   * @returns {FormData} FormData object with CSRF token
   */
  createFormDataWithToken() {
    const formData = new FormData();
    const csrfToken = this.getToken();
    if (csrfToken) {
      formData.append("csrf_token", csrfToken);
    }
    return formData;
  },

  /**
   * Add CSRF token to existing FormData if not present
   * @param {FormData} formData - FormData object to add token to
   * @returns {FormData} FormData with CSRF token
   */
  ensureTokenInFormData(formData) {
    const csrfToken = this.getToken();
    if (csrfToken && !formData.has("csrf_token")) {
      formData.append("csrf_token", csrfToken);
    }
    return formData;
  }
};

/**
 * Notification storage utilities for cross-page messaging
 */
const NotificationUtils = {
  /**
   * Store notification for display after redirect
   * @param {string} type - Notification type (success, error, warning, etc.)
   * @param {string} message - Notification message
   */
  storeForRedirect(type, message) {
    const notification = { type, message };
    sessionStorage.setItem('pendingNotification', JSON.stringify(notification));
  },

  /**
   * Retrieve and display stored notification, then clear it
   * @param {Function} showNotificationFn - Function to show notifications
   */
  showStored(showNotificationFn) {
    const storedNotification = sessionStorage.getItem('pendingNotification');
    if (storedNotification) {
      try {
        const notification = JSON.parse(storedNotification);
        if (typeof showNotificationFn === 'function') {
          showNotificationFn(notification.type, notification.message);
        } else {
          console.log(`${notification.type.toUpperCase()}: ${notification.message}`);
        }
        sessionStorage.removeItem('pendingNotification');
      } catch (error) {
        console.error('Error parsing stored notification:', error);
        sessionStorage.removeItem('pendingNotification');
      }
    }
  },

  /**
   * Clear any pending notifications
   */
  clearStored() {
    sessionStorage.removeItem('pendingNotification');
  }
};

/**
 * Form utilities for common form operations
 */
const FormUtils = {
  /**
   * Clear form errors
   * @param {string} [containerSelector] - Optional container selector to limit scope
   */
  clearErrors(containerSelector = null) {
    const container = containerSelector ? document.querySelector(containerSelector) : document;
    const errorElements = container.querySelectorAll(".text-danger.small");
    errorElements.forEach((element) => {
      element.textContent = "";
    });
  },

  /**
   * Display form errors
   * @param {Object} errors - Object with field names as keys and error messages as values
   * @param {string} [containerSelector] - Optional container selector to limit scope
   */
  displayErrors(errors, containerSelector = null) {
    this.clearErrors(containerSelector);

    for (const [field, message] of Object.entries(errors)) {
      const errorElement = document.getElementById(field + "Error");
      if (errorElement) {
        errorElement.textContent = message;
      }
    }
  },

  /**
   * Reset submit button to original state
   * @param {HTMLElement} button - Button element to reset
   * @param {string} originalText - Original button text/HTML
   */
  resetSubmitButton(button, originalText) {
    if (button) {
      button.disabled = false;
      button.innerHTML = originalText;
    }
  },

  /**
   * Set submit button to loading state
   * @param {HTMLElement} button - Button element to set loading
   * @param {string} [loadingText] - Custom loading text
   */
  setSubmitButtonLoading(button, loadingText = 'Đang xử lý...') {
    if (button) {
      button.disabled = true;
      button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
    }
  }
};

/**
 * API utilities for common API operations
 */
const APIUtils = {
  /**
   * Handle fetch response and parse JSON
   * @param {Response} response - Fetch response object
   * @returns {Promise<Object>} Parsed JSON response
   */
  async handleResponse(response) {
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
  },

  /**
   * Standard fetch with common headers
   * @param {string} url - URL to fetch
   * @param {Object} [options] - Fetch options
   * @returns {Promise<Response>} Fetch response
   */
  async fetch(url, options = {}) {
    const defaultHeaders = {
      "X-Requested-With": "XMLHttpRequest",
    };

    const config = {
      headers: { ...defaultHeaders, ...options.headers },
      ...options
    };

    return fetch(url, config);
  },

  /**
   * GET request with JSON response handling
   * @param {string} url - URL to fetch
   * @param {Object} [options] - Additional fetch options
   * @returns {Promise<Object>} Parsed JSON response
   */
  async get(url, options = {}) {
    const response = await this.fetch(url, {
      method: 'GET',
      headers: { "Content-Type": "application/json" },
      ...options
    });
    return this.handleResponse(response);
  },

  /**
   * POST request with form data
   * @param {string} url - URL to post to
   * @param {FormData} formData - Form data to send
   * @param {Object} [options] - Additional fetch options
   * @returns {Promise<Object>} Parsed JSON response
   */
  async post(url, formData, options = {}) {
    const response = await this.fetch(url, {
      method: 'POST',
      body: formData,
      ...options
    });
    return this.handleResponse(response);
  }
};

/**
 * Validation utilities
 */
const ValidationUtils = {
  /**
   * Validate email format
   * @param {string} email - Email to validate
   * @returns {boolean} Whether email is valid
   */
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * Validate password strength
   * @param {string} password - Password to validate
   * @param {number} [minLength=6] - Minimum password length
   * @returns {Object} Validation result with isValid and message
   */
  validatePassword(password, minLength = 6) {
    if (!password || password.length < minLength) {
      return {
        isValid: false,
        message: `Mật khẩu phải có ít nhất ${minLength} ký tự!`
      };
    }
    return { isValid: true, message: "" };
  },

  /**
   * Check if passwords match
   * @param {string} password - Original password
   * @param {string} confirmPassword - Confirmation password
   * @returns {Object} Validation result with isValid and message
   */
  validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
      return {
        isValid: false,
        message: "Mật khẩu xác nhận không khớp!"
      };
    }
    return { isValid: true, message: "" };
  }
};

// Export utilities for use in other modules
if (typeof window !== 'undefined') {
  window.TemplateUtils = TemplateUtils;
  window.ModalUtils = ModalUtils;
  window.CSRFUtils = CSRFUtils;
  window.NotificationUtils = NotificationUtils;
  window.FormUtils = FormUtils;
  window.APIUtils = APIUtils;
  window.ValidationUtils = ValidationUtils;
}
