from app.extensions import db


class RoomType(db.Model):
    __tablename__ = 'room_types'
    
    room_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(100), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationship với Room
    rooms = db.relationship('Room', backref='room_type', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RoomType {self.type_name} - {self.capacity} người>'
    
    def to_dict(self):
        """Convert room type object to dictionary"""
        return {
            'room_type_id': self.room_type_id,
            'type_name': self.type_name,
            'capacity': self.capacity,
            'price': float(self.price),
            'total_rooms': len(self.rooms)
        }
    
    def to_dict_simple(self):
        """Convert room type object to simple dictionary for dropdowns"""
        return {
            'room_type_id': self.room_type_id,
            'type_name': self.type_name,
            'capacity': self.capacity,
            'price': float(self.price)
        }
    
    @classmethod
    def create_room_type(cls, data):
        """Create a new room type"""
        room_type = cls(
            type_name=data.get('type_name'),
            capacity=data.get('capacity'),
            price=data.get('price')
        )
        db.session.add(room_type)
        db.session.commit()
        return room_type
    
    def update_room_type(self, data):
        """Update room type information"""
        if 'type_name' in data:
            self.type_name = data['type_name']
        if 'capacity' in data:
            self.capacity = data['capacity']
        if 'price' in data:
            self.price = data['price']
        
        db.session.commit()
        return self
    
    def delete_room_type(self):
        """Delete room type"""
        db.session.delete(self)
        db.session.commit()
    
    @property
    def room_count(self):
        """Get total number of rooms with this type"""
        return len(self.rooms)
    
    @property
    def available_rooms_count(self):
        """Get number of available rooms with this type"""
        return len([room for room in self.rooms if room.status == 'available'])
    
    @property
    def occupied_rooms_count(self):
        """Get number of occupied rooms with this type"""
        return len([room for room in self.rooms if room.status == 'occupied'])
