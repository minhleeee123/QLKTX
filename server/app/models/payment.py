from datetime import datetime

from app.extensions import db


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
        return method_map.get(self.payment_method, self.payment_method)
