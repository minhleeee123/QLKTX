/**
 * Base Operations Module
 * Common patterns and utilities for entity operations (CRUD)
 */

/**
 * Base class for entity operations
 */
class BaseOperations {
  constructor(config) {
    this.entityName = config.entityName; // e.g., 'user', 'room', 'building'
    this.entityNameDisplay = config.entityNameDisplay; // e.g., 'người dùng', 'phòng', 'tòa nhà'
    this.baseUrl = config.baseUrl; // e.g., '/users', '/rooms', '/buildings'
    this.modalPrefix = config.modalPrefix; // e.g., 'user', 'room', 'building'
    this.formId = config.formId; // e.g., 'userForm', 'roomForm', 'buildingForm'
    this.submitButtonId = config.submitButtonId; // e.g., 'saveUserBtn'
    
    // State management
    this.isEditMode = false;
    this.currentEntityId = null;
    
    // Bind methods to preserve context
    this.handleFormSubmit = this.handleFormSubmit.bind(this);
    this.handleSuccessResponse = this.handleSuccessResponse.bind(this);
    this.handleErrorResponse = this.handleErrorResponse.bind(this);
  }

  /**
   * Initialize the operations (set up event listeners, etc.)
   */
  init() {
    this.setupFormSubmission();
    this.setupStoredNotifications();
  }

  /**
   * Set up form submission handling
   */
  setupFormSubmission() {
    const form = document.getElementById(this.formId);
    if (form) {
      form.addEventListener("submit", this.handleFormSubmit);
    }
  }

  /**
   * Set up stored notification display
   */
  setupStoredNotifications() {
    // Check for and display any stored notifications from redirects
    // Use a safer approach that checks if showNotification method exists
    const showNotificationFn = (type, message) => {
      if (typeof this.showNotification === 'function') {
        this.showNotification(type, message);
      } else {
        console.log(`${type.toUpperCase()}: ${message}`);
      }
    };
    NotificationUtils.showStored(showNotificationFn);
  }

  /**
   * Handle form submission
   * @param {Event} e - Form submit event
   */
  async handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Ensure CSRF token is included
    CSRFUtils.ensureTokenInFormData(formData);

    // Log form data for debugging in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`${this.entityName} form submitted, isEditMode:`, this.isEditMode, `current${this.entityName}Id:`, this.currentEntityId);
      console.log("Form data entries:");
      for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
      }
    }

    const url = this.isEditMode 
      ? `${this.baseUrl}/${this.currentEntityId}/edit` 
      : `${this.baseUrl}/create`;

    // Set button to loading state
    const submitBtn = document.getElementById(this.submitButtonId);
    const originalText = submitBtn ? submitBtn.innerHTML : '';
    FormUtils.setSubmitButtonLoading(submitBtn);

    try {
      await this.submitForm(url, formData, submitBtn, originalText);
    } catch (error) {
      console.error(`${this.entityName} submission error:`, error);
      this.handleErrorResponse(error);
      FormUtils.resetSubmitButton(submitBtn, originalText);
    }
  }

  /**
   * Submit form data to server
   * @param {string} url - URL to submit to
   * @param {FormData} formData - Form data to submit
   * @param {HTMLElement} submitBtn - Submit button element
   * @param {string} originalButtonText - Original button text
   */
  async submitForm(url, formData, submitBtn, originalButtonText) {
    try {
      const apiResponse = await APIUtils.post(url, formData);
      this.handleSuccessResponse(apiResponse);
    } catch (error) {
      this.handleErrorResponse(error);
    } finally {
      FormUtils.resetSubmitButton(submitBtn, originalButtonText);
    }
  }

  /**
   * Handle successful API response
   * @param {Object} data - API response data
   */
  handleSuccessResponse(data) {
    if (data.success) {
      // Store notification for after redirect
      NotificationUtils.storeForRedirect(
        "success",
        data.message || "Thao tác thành công!"
      );
      this.closeModalAndRedirect(data.redirect);
    } else {
      if (data.errors) {
        FormUtils.displayErrors(data.errors);
      } else {
        this.showNotification("error", "Lỗi: " + (data.message || "Có lỗi xảy ra"));
      }
    }
  }

  /**
   * Handle error response
   * @param {Error} error - Error object
   */
  handleErrorResponse(error) {
    console.error(`Error during ${this.entityName} operation:`, error);
    this.showNotification("error", "Có lỗi xảy ra: " + error.message);
  }

  /**
   * Close modal and redirect or reload page
   * @param {string} [redirectUrl] - Optional redirect URL
   */
  closeModalAndRedirect(redirectUrl) {
    ModalUtils.hide(`${this.modalPrefix}Modal`);

    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      window.location.reload();
    }
  }

  /**
   * Open create modal
   * @param {Object} [options] - Additional options for modal setup
   */
  openCreateModal(options = {}) {
    this.isEditMode = false;
    this.currentEntityId = null;
    
    const modalLabel = document.getElementById(`${this.modalPrefix}ModalLabel`);
    const saveBtn = document.getElementById(this.submitButtonId);
    const form = document.getElementById(this.formId);
    
    if (modalLabel) {
      modalLabel.textContent = options.title || `Thêm ${this.entityNameDisplay}`;
    }
    
    if (saveBtn) {
      saveBtn.innerHTML = options.saveButtonText || '<i class="fas fa-save"></i> Lưu';
    }
    
    if (form) {
      form.reset();
    }

    // Enable all fields for create mode
    this.toggleFieldsForMode('create', options.disabledFields);
    
    FormUtils.clearErrors();
    
    // Call custom setup if provided
    if (options.customSetup) {
      options.customSetup.call(this);
    }
  }

  /**
   * Open edit modal
   * @param {number|string} entityId - ID of entity to edit
   * @param {Object} [options] - Additional options for modal setup
   */
  async openEditModal(entityId, options = {}) {
    entityId = parseInt(entityId);
    
    this.isEditMode = true;
    this.currentEntityId = entityId;
    
    const modalLabel = document.getElementById(`${this.modalPrefix}ModalLabel`);
    const saveBtn = document.getElementById(this.submitButtonId);
    
    if (modalLabel) {
      modalLabel.textContent = options.title || `Chỉnh sửa ${this.entityNameDisplay}`;
    }
    
    if (saveBtn) {
      saveBtn.innerHTML = options.saveButtonText || '<i class="fas fa-save"></i> Cập nhật';
    }

    // Disable non-updatable fields in edit mode
    this.toggleFieldsForMode('edit', options.disabledFields);
    
    FormUtils.clearErrors();
    
    // Call custom setup if provided
    if (options.customSetup) {
      await options.customSetup.call(this, entityId);
    }

    // Show modal
    ModalUtils.show(`${this.modalPrefix}Modal`);

    try {
      // Load entity data
      const entity = await this.fetchEntity(entityId);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`Loaded ${this.entityName} data:`, entity);
      }

      // Populate form with entity data
      this.populateForm(entity);
    } catch (error) {
      this.showNotification("error", "Lỗi: " + error.message);
      ModalUtils.hide(`${this.modalPrefix}Modal`);
    }
  }

  /**
   * View entity details in modal
   * @param {number|string} entityId - ID of entity to view
   * @param {Object} [options] - Additional options for detail view
   */
  async viewEntityDetails(entityId, options = {}) {
    entityId = parseInt(entityId);

    // Show the modal first
    ModalUtils.show(`${this.modalPrefix}DetailModal`);

    // Show loading state
    TemplateUtils.showLoading(
      `${this.modalPrefix}DetailContent`,
      `${this.modalPrefix}DetailLoadingTemplate`
    );

    try {
      const entity = await this.fetchEntity(entityId);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`Loaded ${this.entityName} data for details:`, entity);
      }

      // Prepare template data
      const templateData = this.prepareDetailTemplateData(entity, options);

      // Render and display template
      const renderedTemplate = TemplateUtils.render(
        `${this.modalPrefix}DetailTemplate`,
        templateData
      );
      
      document.getElementById(`${this.modalPrefix}DetailContent`).innerHTML = renderedTemplate;
    } catch (error) {
      console.error(`Error fetching ${this.entityName} data:`, error);
      TemplateUtils.showError(
        `${this.modalPrefix}DetailContent`,
        `${this.modalPrefix}DetailErrorTemplate`,
        error.message || `Có lỗi xảy ra khi tải thông tin ${this.entityNameDisplay}`
      );
    }
  }

  /**
   * Toggle field states based on mode (create/edit)
   * @param {string} mode - 'create' or 'edit'
   * @param {Array} [customDisabledFields] - Custom list of fields to disable in edit mode
   */
  toggleFieldsForMode(mode, customDisabledFields = []) {
    const fieldsToToggle = customDisabledFields.length > 0 
      ? customDisabledFields 
      : this.getDefaultDisabledFieldsForEdit();

    fieldsToToggle.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (field) {
        if (mode === 'edit') {
          field.disabled = true;
          field.style.backgroundColor = "#f8f9fa";
        } else {
          field.disabled = false;
          field.style.backgroundColor = "";
        }
      }
    });
  }

  /**
   * Get default fields to disable in edit mode
   * Override in subclasses as needed
   * @returns {Array} Array of field IDs to disable in edit mode
   */
  getDefaultDisabledFieldsForEdit() {
    return [];
  }

  /**
   * Fetch entity data from server
   * Override in subclasses
   * @param {number} entityId - ID of entity to fetch
   * @returns {Promise<Object>} Entity data
   */
  async fetchEntity(entityId) {
    const apiResponse = await APIUtils.get(`${this.baseUrl}/${entityId}`);
    
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || `Failed to fetch ${this.entityName} data`);
    }

    // Most APIs return: {success, message, data: {entityName: {...}}, status_code}
    return apiResponse.data[this.entityName];
  }

  /**
   * Populate form with entity data
   * Override in subclasses
   * @param {Object} entity - Entity data to populate form with
   */
  populateForm(entity) {
    // Override in subclasses
    console.warn(`populateForm method not implemented for ${this.entityName}`);
  }

  /**
   * Prepare template data for detail view
   * Override in subclasses
   * @param {Object} entity - Entity data
   * @param {Object} options - Additional options
   * @returns {Object} Template data
   */
  prepareDetailTemplateData(entity, options = {}) {
    // Override in subclasses
    console.warn(`prepareDetailTemplateData method not implemented for ${this.entityName}`);
    return entity;
  }

  /**
   * Show notification
   * Override to use your notification system
   * @param {string} type - Notification type
   * @param {string} message - Notification message
   */
  showNotification(type, message) {
    // Override in subclasses to use your notification system
    console.log(`${type.toUpperCase()}: ${message}`);
  }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.BaseOperations = BaseOperations;
}
