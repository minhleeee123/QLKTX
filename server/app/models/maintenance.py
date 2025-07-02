from app.extensions import db
from datetime import datetime


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')  # 'pending', 'assigned', 'in_progress', 'completed', 'cancelled'
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # ID nhân viên bảo trì được phân công
    completed_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='submitted_maintenance_requests')
    room = db.relationship('Room', backref='maintenance_requests')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_user_id], backref='assigned_maintenance_requests')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.request_id} - {self.title} ({self.status})>'
    
    @property
    def is_pending(self):
        """Kiểm tra yêu cầu có đang chờ xử lý không"""
        return self.status == 'pending'
    
    @property
    def is_assigned(self):
        """Kiểm tra yêu cầu đã được phân công chưa"""
        return self.status == 'assigned'
    
    @property
    def is_in_progress(self):
        """Kiểm tra yêu cầu có đang được xử lý không"""
        return self.status == 'in_progress'
    
    @property
    def is_completed(self):
        """Kiểm tra yêu cầu đã hoàn thành chưa"""
        return self.status == 'completed'
    
    @property
    def is_cancelled(self):
        """Kiểm tra yêu cầu bị hủy chưa"""
        return self.status == 'cancelled'
    
    @property
    def status_display(self):
        """Hiển thị trạng thái bằng tiếng Việt"""
        status_map = {
            'pending': 'Chờ xử lý',
            'assigned': 'Đã phân công',
            'in_progress': 'Đang xử lý',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def days_since_request(self):
        """Số ngày kể từ khi tạo yêu cầu"""
        return (datetime.utcnow() - self.request_date).days
    
    @property
    def is_urgent(self):
        """Kiểm tra yêu cầu có khẩn cấp không (quá 3 ngày chưa xử lý)"""
        return self.is_pending and self.days_since_request > 3