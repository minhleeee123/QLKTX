document.addEventListener('DOMContentLoaded', function () {
    const roleSelect = document.getElementById('role');
    const studentIdField = document.getElementById('studentIdField');
    const studentIdInput = document.getElementById('studentId');

    // Function to toggle student ID field visibility
    function toggleStudentIdField() {
        if (roleSelect.value === 'student') {
            studentIdField.style.display = 'block';
            studentIdInput.required = true;
        } else {
            studentIdField.style.display = 'none';
            studentIdInput.required = false;
            studentIdInput.value = ''; // Clear the value when hidden
            // Clear any error messages
            const errorDiv = document.getElementById('studentIdError');
            if (errorDiv) {
                errorDiv.textContent = '';
            }
        }
    }

    // Listen for role changes
    roleSelect.addEventListener('change', toggleStudentIdField);

    // Check initial state when modal is shown
    document.getElementById('userModal').addEventListener('shown.bs.modal', function () {
        toggleStudentIdField();
    });

    // Reset field visibility when modal is hidden
    document.getElementById('userModal').addEventListener('hidden.bs.modal', function () {
        studentIdField.style.display = 'none';
        studentIdInput.required = false;
    });
});
