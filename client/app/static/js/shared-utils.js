/**
 * Shared Utilities for Application Operations
 * This file contains utility functions used across different operation modules
 */

/**
 * Template utilities for rendering Handlebars templates
 */
window.TemplateUtils = {
  /**
   * Render a template with data
   * @param {string} templateId - The ID of the template element
   * @param {object} data - Data to populate the template
   * @returns {string} Rendered HTML
   */
  render(templateId, data) {
    const templateElement = document.getElementById(templateId);
    if (!templateElement) {
      console.error(`Template with ID '${templateId}' not found`);
      return "";
    }

    const templateSource = templateElement.innerHTML;
    
    // Check if Handlebars is available
    if (typeof Handlebars !== 'undefined') {
      const template = Handlebars.compile(templateSource);
      return template(data);
    } else {
      // Simple template replacement if Handlebars is not available
      let html = templateSource;
      Object.keys(data).forEach(key => {
        const regex = new RegExp(`{{${key}}}`, 'g');
        html = html.replace(regex, data[key] || '');
      });
      return html;
    }
  },

  /**
   * Show loading state in a container
   * @param {string} containerId - ID of the container to show loading in
   * @param {string} loadingTemplateId - ID of the loading template
   */
  showLoading(containerId, loadingTemplateId) {
    const container = document.getElementById(containerId);
    const loadingTemplate = document.getElementById(loadingTemplateId);
    
    if (container && loadingTemplate) {
      container.innerHTML = loadingTemplate.innerHTML;
    } else {
      // Fallback loading HTML
      container.innerHTML = `
        <div class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Đang tải...</span>
          </div>
          <p class="mt-2">Đang tải thông tin...</p>
        </div>
      `;
    }
  },

  /**
   * Show error state in a container
   * @param {string} containerId - ID of the container to show error in
   * @param {string} errorTemplateId - ID of the error template
   * @param {string} errorMessage - Error message to display
   */
  showError(containerId, errorTemplateId, errorMessage) {
    const container = document.getElementById(containerId);
    const errorTemplate = document.getElementById(errorTemplateId);
    
    if (container) {
      if (errorTemplate) {
        const templateData = { error_message: errorMessage };
        container.innerHTML = this.render(errorTemplateId, templateData);
      } else {
        // Fallback error HTML
        container.innerHTML = `
          <div class="alert alert-danger text-center">
            <i class="fas fa-exclamation-triangle mb-2"></i>
            <p class="mb-0">${errorMessage}</p>
          </div>
        `;
      }
    }
  }
};

/**
 * Modal utilities for managing Bootstrap modals
 */
window.ModalUtils = {
  /**
   * Show a modal
   * @param {string} modalId - ID of the modal to show
   */
  show(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
      // Check if Bootstrap modal is available
      if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      } else if (typeof $ !== 'undefined' && $.fn.modal) {
        // jQuery Bootstrap modal fallback
        $(`#${modalId}`).modal('show');
      } else {
        // Manual show fallback
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        document.body.classList.add('modal-open');
      }
    }
  },

  /**
   * Hide a modal and ensure proper cleanup
   * @param {string} modalId - ID of the modal to hide
   */
  hide(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
      try {
        // Check if Bootstrap modal is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          const modal = bootstrap.Modal.getInstance(modalElement);
          if (modal) {
            modal.hide();
          } else {
            // If no instance exists, create one and hide it
            const newModal = new bootstrap.Modal(modalElement);
            newModal.hide();
          }
        } else if (typeof $ !== 'undefined' && $.fn.modal) {
          // jQuery Bootstrap modal fallback
          $(`#${modalId}`).modal('hide');
        } else {
          // Manual hide fallback
          modalElement.style.display = 'none';
          modalElement.classList.remove('show');
          document.body.classList.remove('modal-open');
        }
        
        // Additional cleanup for backdrop issues
        this.cleanupBackdrop();
        
      } catch (error) {
        console.warn('Error hiding modal, performing manual cleanup:', error);
        this.forceCleanup(modalId);
      }
    }
  },

  /**
   * Clean up modal backdrop and body classes
   */
  cleanupBackdrop() {
    // Remove any lingering backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
      backdrop.remove();
    });

    // Remove modal-open class from body if no modals are visible
    const visibleModals = document.querySelectorAll('.modal.show');
    if (visibleModals.length === 0) {
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }
  },

  /**
   * Force cleanup when normal modal hide fails
   * @param {string} modalId - ID of the modal to cleanup
   */
  forceCleanup(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
      // Force hide the modal
      modalElement.style.display = 'none';
      modalElement.classList.remove('show');
      modalElement.setAttribute('aria-hidden', 'true');
      modalElement.removeAttribute('aria-modal');
    }

    // Clean up backdrop and body
    this.cleanupBackdrop();
    
    // Reset body scroll
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  },

  /**
   * Check if any modal is currently open
   * @returns {boolean} True if any modal is open
  /**
   * Check if any modal is currently open
   * @returns {boolean} True if any modal is open
   */
  isAnyModalOpen() {
    const visibleModals = document.querySelectorAll('.modal.show');
    return visibleModals.length > 0;
  },

  /**
   * Initialize global modal event listeners for cleanup
   */
  initGlobalListeners() {
    // Add escape key listener
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && this.isAnyModalOpen()) {
        this.cleanupBackdrop();
      }
    });

    // Add click listener for backdrop cleanup
    document.addEventListener('click', (event) => {
      if (event.target && event.target.classList.contains('modal-backdrop')) {
        this.cleanupBackdrop();
      }
    });

    // Listen for Bootstrap modal events
    document.addEventListener('hidden.bs.modal', () => {
      // Small delay to ensure Bootstrap has finished its cleanup
      setTimeout(() => {
        this.cleanupBackdrop();
      }, 50);
    });
  }
};

/**
 * CSRF token utilities
 */
window.CSRFUtils = {
  /**
   * Get CSRF token from meta tag
   * @returns {string|null} CSRF token
   */
  getToken() {
    // Try meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    let token = metaTag ? metaTag.getAttribute("content") : null;

    // If not found in meta tag, try hidden input field
    if (!token) {
      const hiddenInput = document.getElementById("csrfToken");
      token = hiddenInput ? hiddenInput.value : null;
    }

    // Debug logging (only in development)
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      console.log("CSRFUtils.getToken() - Meta tag found:", !!metaTag);
      console.log(
        "CSRFUtils.getToken() - Hidden input found:",
        !!document.getElementById("csrfToken")
      );
      console.log("CSRFUtils.getToken() - Token value:", token);
    }

    return token;
  },

  /**
   * Create FormData with CSRF token
   * @returns {FormData} FormData object with CSRF token
   */
  createFormDataWithToken() {
    const formData = new FormData();
    const token = this.getToken();

    // Debug logging (only in development)
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      console.log(
        "CSRFUtils.createFormDataWithToken() - Token retrieved:",
        token
      );
    }

    if (token) {
      formData.append("csrf_token", token);
    }
    return formData;
  },

  /**
   * Ensure CSRF token is in FormData
   * @param {FormData} formData - FormData to add token to
   */
  ensureTokenInFormData(formData) {
    if (!formData.has('csrf_token')) {
      const token = this.getToken();
      if (token) {
        formData.append('csrf_token', token);
      }
    }
  }
};

/**
 * Notification utilities
 */
window.NotificationUtils = {
  /**
   * Store notification for redirect
   * @param {string} type - Notification type
   * @param {string} message - Notification message
   */
  storeForRedirect(type, message) {
    sessionStorage.setItem('flash_message', JSON.stringify({ type, message }));
  },

  /**
   * Show stored notification
   * @param {function} showNotificationFn - Function to call to show notification
   */
  showStored(showNotificationFn) {
    const stored = sessionStorage.getItem('flash_message');
    if (stored) {
      try {
        const { type, message } = JSON.parse(stored);
        showNotificationFn(type, message);
        sessionStorage.removeItem('flash_message');
      } catch (e) {
        console.error('Error parsing stored notification:', e);
      }
    }
  }
};

/**
 * Form utilities
 */
window.FormUtils = {
  /**
   * Display form errors
   * @param {object} errors - Object with field errors
   */
  displayErrors(errors) {
    // Clear existing errors
    this.clearErrors();

    Object.keys(errors).forEach(field => {
      const fieldElement = document.getElementById(field);
      const errorMessages = Array.isArray(errors[field]) ? errors[field] : [errors[field]];
      
      if (fieldElement) {
        fieldElement.classList.add('is-invalid');
        
        // Create error feedback element
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = errorMessages.join(', ');
        
        // Insert after the field
        fieldElement.parentNode.insertBefore(feedback, fieldElement.nextSibling);
      }
    });
  },

  /**
   * Clear form errors
   */
  clearErrors() {
    // Remove invalid classes
    document.querySelectorAll('.is-invalid').forEach(element => {
      element.classList.remove('is-invalid');
    });

    // Remove error feedback elements
    document.querySelectorAll('.invalid-feedback').forEach(element => {
      element.remove();
    });
  },

  /**
   * Set submit button to loading state
   * @param {HTMLElement} button - Button element
   */
  setSubmitButtonLoading(button) {
    if (button) {
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Đang xử lý...';
    }
  },

  /**
   * Reset submit button to original state
   * @param {HTMLElement} button - Button element
   * @param {string} originalText - Original button text
   */
  resetSubmitButton(button, originalText) {
    if (button) {
      button.disabled = false;
      button.innerHTML = originalText;
    }
  }
};

/**
 * API utilities for making HTTP requests
 */
window.APIUtils = {
  /**
   * Handle API response
   * @param {Response} response - Fetch response object
   * @returns {Promise} Parsed JSON response
   */
  async handleResponse(response) {
    try {
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return data;
    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new Error(`Invalid JSON response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Make GET request
   * @param {string} url - Request URL
   * @returns {Promise} API response
   */
  async get(url) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      // Check if response is ok
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Expected JSON response but received: ${contentType || 'unknown'}. Response: ${text.substring(0, 100)}...`);
      }

      return await response.json();
    } catch (error) {
      // Only log detailed errors in development
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.error('API GET Error:', error);
      }
      throw new Error(`API GET request failed: ${error.message}`);
    }
  },

  /**
   * Make POST request
   * @param {string} url - Request URL
   * @param {FormData|object} data - Request data
   * @returns {Promise} API response
   */
  async post(url, data) {
    try {
      const headers = {
        'X-Requested-With': 'XMLHttpRequest'
      };

      // Don't set Content-Type for FormData, let browser set it
      let body = data;
      if (!(data instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        body = JSON.stringify(data);
      }

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body
      });

      // Check if response is ok
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Expected JSON response but received: ${contentType || 'unknown'}. Response: ${text.substring(0, 100)}...`);
      }

      return await response.json();
    } catch (error) {
      // Only log detailed errors in development
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.error('API POST Error:', error);
      }
      throw new Error(`API POST request failed: ${error.message}`);
    }
  }
};

/**
 * Validation utilities
 */
window.ValidationUtils = {
  /**
   * Validate password confirmation
   * @param {string} password - Password
   * @param {string} confirmPassword - Confirm password
   * @returns {object} Validation result
   */
  validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
      return {
        isValid: false,
        message: "Mật khẩu và xác nhận mật khẩu không khớp"
      };
    }
    return { isValid: true };
  },

  /**
   * Validate password strength
   * @param {string} password - Password to validate
   * @returns {object} Validation result
   */
  validatePassword(password) {
    if (!password || password.length < 6) {
      return {
        isValid: false,
        message: "Mật khẩu phải có ít nhất 6 ký tự"
      };
    }
    return { isValid: true };
  }
};

console.log("Shared utilities loaded successfully");

// Initialize modal cleanup listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  if (window.ModalUtils && typeof window.ModalUtils.initGlobalListeners === 'function') {
    window.ModalUtils.initGlobalListeners();
  }
});

// Global function to manually clean up stuck modals (for debugging)
window.cleanupStuckModals = function() {
  console.log('Manually cleaning up stuck modals...');
  if (window.ModalUtils) {
    window.ModalUtils.cleanupBackdrop();
    // Also hide any visible modals
    const visibleModals = document.querySelectorAll('.modal.show');
    visibleModals.forEach(modal => {
      window.ModalUtils.forceCleanup(modal.id);
    });
  }
};

// Global function to test API endpoints (for debugging)
window.testAPIEndpoint = async function(url) {
  console.log(`Testing API endpoint: ${url}`);
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    console.log(`Response status: ${response.status} ${response.statusText}`);
    console.log(`Response headers:`, response.headers);
    
    const contentType = response.headers.get('content-type');
    console.log(`Content-Type: ${contentType}`);
    
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      console.log(`Response data:`, data);
      return data;
    } else {
      const text = await response.text();
      console.log(`Response text (first 500 chars):`, text.substring(0, 500));
      return text;
    }
  } catch (error) {
    console.error(`API test failed:`, error);
    return error;
  }
};
