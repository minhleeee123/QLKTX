from datetime import datetime

from app.extensions import db


class Registration(db.Model):
    __tablename__ = 'registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'approved', 'rejected'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', backref='registrations')
    room = db.relationship('Room', backref='registrations')
    contract = db.relationship('Contract', back_populates='registration', uselist=False)
    
    def __repr__(self):
        return f'<Registration {self.registration_id} - Student: {self.student_id}, Room: {self.room_id}, Status: {self.status}>'
    
    @property
    def is_pending(self):
        """Kiểm tra đơn đăng ký có đang chờ xử lý không"""
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        """Kiểm tra đơn đăng ký đã được duyệt chưa"""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Kiểm tra đơn đăng ký bị từ chối chưa"""
        return self.status == 'rejected'
        return self.status == 'rejected'
