from app.extensions import db


class Building(db.Model):
    __tablename__ = "buildings"

    building_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_name = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(10), nullable=False)  # 'male', 'female', 'all'

    # Relationship với Room
    rooms = db.relationship(
        "Room", backref="building", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Building {self.building_name}>"

    def to_dict(self):
        """Convert building object to dictionary"""
        return {
            "building_id": self.building_id,
            "building_name": self.building_name,
            "gender": self.gender,
            "total_rooms": len(self.rooms),
            "available_rooms": self.available_rooms_count,
            "occupied_rooms": self.occupied_rooms_count,
        }

    def to_dict_simple(self):
        """Convert building object to simple dictionary for dropdowns"""
        return {
            "building_id": self.building_id,
            "building_name": self.building_name,
            "gender": self.gender,
        }

    @classmethod
    def create_building(cls, data):
        """Create a new building"""
        building = cls(
            building_name=data.get("building_name"), gender=data.get("gender", "all")
        )
        db.session.add(building)
        db.session.commit()
        return building

    def update_building(self, data):
        """Update building information"""
        if "building_name" in data:
            self.building_name = data["building_name"]

        db.session.commit()
        return self

    def delete_building(self):
        """Delete building"""
        db.session.delete(self)
        db.session.commit()

    @property
    def room_count(self):
        """Get total number of rooms in building"""
        return len(self.rooms)

    @property
    def available_rooms_count(self):
        """Get number of available rooms in building"""
        return len([room for room in self.rooms if room.status == "available"])

    @property
    def occupied_rooms_count(self):
        """Get number of occupied rooms in building"""
        return len([room for room in self.rooms if room.current_occupancy > 0])
