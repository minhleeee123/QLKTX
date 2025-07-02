from app.extensions import db


class Building(db.Model):
    __tablename__ = 'buildings'
    
    building_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_name = db.Column(db.String(100), nullable=False)
    
    # Relationship với Room
    rooms = db.relationship('Room', backref='building', lazy=True)
    
    def __repr__(self):
        return f'<Building {self.building_name}>'


class RoomType(db.Model):
    __tablename__ = 'room_types'
    
    room_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(100), nullable=False)  # 'Phòng 4 người', 'Phòng 6 người', 'Phòng dịch vụ'
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationship với Room
    rooms = db.relationship('Room', backref='room_type', lazy=True)
    
    def __repr__(self):
        return f'<RoomType {self.type_name} - {self.capacity} người>'


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