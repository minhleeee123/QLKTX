# JavaScript Refactoring Documentation

## Overview
This refactoring reduces code duplication across the user, room, and building operation modules by extracting common functionality into shared utilities and a base operations class.

## New File Structure

### Shared Utilities (`/static/js/shared/`)

#### `shared-utils.js`
Contains reusable utility modules:
- **TemplateUtils**: Template rendering and manipulation
- **ModalUtils**: Bootstrap modal management
- **CSRFUtils**: CSRF token handling
- **NotificationUtils**: Cross-page notification storage
- **FormUtils**: Form validation and error handling
- **APIUtils**: Common API request patterns
- **ValidationUtils**: Input validation helpers

#### `base-operations.js`
Contains the `BaseOperations` class that provides:
- Common CRUD operation patterns
- Form submission handling
- Modal management
- Error handling
- Response processing

## Refactored Files

### `user_operations.js`
- **Before**: 500+ lines with duplicate utilities
- **After**: ~200 lines, extends `BaseOperations`
- **Key Features**:
  - Password validation for user creation
  - Field disabling in edit mode (email, studentId)
  - Role badge styling helpers

### `room_operations.js`
- **Before**: 580+ lines with duplicate utilities
- **After**: ~220 lines, extends `BaseOperations`
- **Key Features**:
  - Building and room type dropdown loading
  - Room status badge styling
  - Field disabling in edit mode (roomNumber, buildingId)

### `building_operations.js`
- **Before**: 510+ lines with duplicate utilities
- **After**: ~180 lines, extends `BaseOperations`
- **Key Features**:
  - Simple building management
  - Legacy modal event support

## Benefits of Refactoring

### 1. **Reduced Code Duplication**
- Eliminated ~800 lines of duplicate code
- Shared utilities used across all modules
- Single source of truth for common operations

### 2. **Improved Maintainability**
- Bug fixes in shared utilities benefit all modules
- Consistent error handling and API patterns
- Easier to add new entity types

### 3. **Better Organization**
- Clear separation of concerns
- Entity-specific logic isolated in respective classes
- Shared logic centralized in utility modules

### 4. **Enhanced Extensibility**
- Easy to add new entity operations by extending `BaseOperations`
- Pluggable validation and form handling
- Configurable field behavior per entity

## Usage Guide

### Including Scripts
Always include shared utilities before specific operation scripts:

```html
<!-- Include shared utilities FIRST -->
<script src="/static/js/shared/shared-utils.js"></script>
<script src="/static/js/shared/base-operations.js"></script>

<!-- Then include specific operation scripts -->
<script src="/static/js/users/user_operations.js"></script>
<script src="/static/js/rooms/room_operations.js"></script>
<script src="/static/js/buildings/building_operations.js"></script>
```

### Creating New Entity Operations

```javascript
class NewEntityOperations extends BaseOperations {
  constructor() {
    super({
      entityName: 'entity',
      entityNameDisplay: 'thực thể', 
      baseUrl: '/entities',
      modalPrefix: 'entity',
      formId: 'entityForm',
      submitButtonId: 'saveEntityBtn'
    });
  }

  // Override methods as needed
  populateForm(entity) {
    // Entity-specific form population
  }

  prepareDetailTemplateData(entity) {
    // Entity-specific template data preparation
  }
}
```

### Using Utility Functions

```javascript
// CSRF handling
const formData = CSRFUtils.createFormDataWithToken();

// Form validation
const isValid = ValidationUtils.isValidEmail(email);
const passwordResult = ValidationUtils.validatePassword(password);

// Notifications
NotificationUtils.storeForRedirect('success', 'Operation completed!');

// API calls
const data = await APIUtils.get('/api/endpoint');
const result = await APIUtils.post('/api/endpoint', formData);

// Form utilities
FormUtils.clearErrors();
FormUtils.displayErrors(errors);
FormUtils.setSubmitButtonLoading(button);
```

## Backward Compatibility

### Legacy Function Support
The refactored files maintain backward compatibility by providing legacy function wrappers:

```javascript
// Legacy functions still work but delegate to new utilities
function createFormDataWithCSRF() {
  return CSRFUtils.createFormDataWithToken();
}

function storeNotificationForRedirect(type, message) {
  NotificationUtils.storeForRedirect(type, message);
}
```

### Migration Path
1. Update HTML templates to include shared utilities
2. Test existing functionality
3. Gradually adopt new utility functions
4. Remove legacy function calls when ready

## Performance Improvements

### Reduced Bundle Size
- Eliminated duplicate code (~800 lines removed)
- Shared utilities loaded once, cached by browser
- Smaller individual module files

### Better Caching
- Shared utilities can be cached separately
- Entity-specific code changes don't invalidate shared cache
- More efficient browser resource utilization

## Testing Considerations

### Unit Testing
- Shared utilities can be tested independently
- Base operations class provides consistent testing patterns
- Entity-specific logic isolated for focused testing

### Integration Testing
- Test shared utility integration with each entity type
- Verify legacy function compatibility
- Test modal and form interactions

## Future Enhancements

### Potential Improvements
1. **TypeScript Migration**: Add type safety to shared utilities
2. **ES6 Modules**: Convert to modern module system
3. **Test Coverage**: Add comprehensive unit tests
4. **Performance Monitoring**: Add metrics for operation performance
5. **Accessibility**: Enhance ARIA support in modal utilities

### Extension Points
- Add more validation utilities as needed
- Extend API utilities for different response formats
- Add more form utilities for complex form interactions
- Create specialized utilities for file uploads, date handling, etc.

## Migration Checklist

- [x] Create shared utility modules
- [x] Create base operations class
- [x] Refactor user operations
- [x] Refactor room operations  
- [x] Refactor building operations
- [x] Maintain backward compatibility
- [x] Document usage patterns
- [ ] Update HTML templates to include shared scripts
- [ ] Test all existing functionality
- [ ] Remove console.log statements for production
- [ ] Add comprehensive error handling
- [ ] Performance testing and optimization
