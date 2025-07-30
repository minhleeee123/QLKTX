from app.extensions import db


class Room(db.Model):
    __tablename__ = 'rooms'

    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_number = db.Column(db.String(10), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.building_id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.room_type_id'), nullable=False)
    status = db.Column(db.String(50), default='available')  # 'available', 'occupied', 'pending_approval', 'maintenance'
    current_occupancy = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Room {self.room_number} - {self.status}>'

    @property
    def is_available(self):
        """Kiểm tra phòng có còn chỗ trống không"""
        return self.status == 'available' and self.current_occupancy < self.room_type.capacity

    @property
    def remaining_capacity(self):
        """Số chỗ còn trống trong phòng"""
        return max(0, self.room_type.capacity - self.current_occupancy)

    @property
    def actual_occupancy(self):
        """Số sinh viên thực tế đang ở trong phòng (từ registrations)"""
        from app.models import Registration
        return Registration.query.filter_by(room_id=self.room_id, status='approved').count()

    @property
    def current_students(self):
        """Danh sách sinh viên hiện tại trong phòng"""
        from app.models import Registration, User
        return db.session.query(User).join(Registration).filter(
            Registration.room_id == self.room_id,
            Registration.status == 'approved'
        ).all()

# Reading room model
