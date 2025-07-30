from datetime import date, datetime

from app.extensions import db


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
