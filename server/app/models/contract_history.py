from datetime import datetime

from app.extensions import db


class ContractHistory(db.Model):
    __tablename__ = 'contract_history'
    
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.contract_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'created', 'updated', 'renewed', 'terminated'
    old_value = db.Column(db.Text)  # JSON string của giá trị cũ
    new_value = db.Column(db.Text)  # JSON string của giá trị mới
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = db.relationship('Contract', backref='history')
    user = db.relationship('User', backref='contract_actions')
    
    def __repr__(self):
        return f'<ContractHistory {self.history_id} - Contract: {self.contract_id}, Action: {self.action}>'

    @property
    def action_display(self):
        """Hiển thị hành động dễ đọc"""
        action_map = {
            'created': 'Tạo mới',
            'updated': 'Cập nhật',
            'renewed': 'Gia hạn',
            'terminated': 'Chấm dứt',
            'approved': 'Duyệt',
            'rejected': 'Từ chối'
        }
        return action_map.get(self.action, self.action)
        return action_map.get(self.action, self.action)
