from app.extensions import db
from datetime import datetime, date


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


class Contract(db.Model):
    __tablename__ = 'contracts'
    
    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.registration_id'), nullable=False, unique=True)
    contract_code = db.Column(db.String(50), unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registration = db.relationship('Registration', back_populates='contract')
    payments = db.relationship('Payment', back_populates='contract', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contract {self.contract_code} - {self.start_date} to {self.end_date}>'
    
    @property
    def is_active(self):
        """Kiểm tra hợp đồng có đang hiệu lực không"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_expired(self):
        """Kiểm tra hợp đồng đã hết hạn chưa"""
        return date.today() > self.end_date
    
    @property
    def days_remaining(self):
        """Số ngày còn lại của hợp đồng"""
        if self.is_expired:
            return 0
        return (self.end_date - date.today()).days
    
    @property
    def duration_months(self):
        """Thời hạn hợp đồng tính theo tháng"""
        return (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
    
    @property
    def total_paid(self):
        """Tổng số tiền đã thanh toán"""
        return sum(payment.amount for payment in self.payments if payment.status == 'confirmed')
    
    @property
    def pending_payments(self):
        """Danh sách các khoản thanh toán đang chờ xác nhận"""
        return [payment for payment in self.payments if payment.status == 'pending']


class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.contract_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # 'bank_transfer', 'cash'
    status = db.Column(db.String(50), default='pending')  # 'pending', 'confirmed', 'failed'
    proof_image_url = db.Column(db.String(255))  # URL ảnh chụp màn hình giao dịch
    confirmed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    # Relationships
    contract = db.relationship('Contract', back_populates='payments')
    confirmed_by = db.relationship('User', backref='confirmed_payments')
    
    def __repr__(self):
        return f'<Payment {self.payment_id} - Amount: {self.amount}, Status: {self.status}>'
    
    @property
    def is_pending(self):
        """Kiểm tra thanh toán có đang chờ xác nhận không"""
        return self.status == 'pending'
    
    @property
    def is_confirmed(self):
        """Kiểm tra thanh toán đã được xác nhận chưa"""
        return self.status == 'confirmed'
    
    @property
    def is_failed(self):
        """Kiểm tra thanh toán bị thất bại chưa"""
        return self.status == 'failed'
    
    @property
    def payment_method_display(self):
        """Hiển thị phương thức thanh toán dễ đọc"""
        method_map = {
            'bank_transfer': 'Chuyển khoản ngân hàng',
            'cash': 'Tiền mặt'
        }
        return method_map.get(self.payment_method, self.payment_method)