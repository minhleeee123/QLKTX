from flask_login import UserMixin

class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_data):
        self.id = user_data.get('user_id')
        self.email = user_data.get('email')
        self.full_name = user_data.get('full_name')
        self.role = user_data.get('role')
        self.phone_number = user_data.get('phone_number')
        self.student_id = user_data.get('student_id')
        self._active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
        self._data = user_data  # Store all raw data

    def get_id(self):
        """Return the user ID as a unicode string"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Return True if the user is active"""
        return self._active
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.role == 'staff'
    
    def is_student(self):
        """Check if user is student"""
        return self.role == 'student'
    
    def is_management(self):
        """Check if user is management"""
        return self.role == 'management'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return self._data
