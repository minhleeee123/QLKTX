from app.extensions import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    role_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship('User', back_populates='role')


class User(db.Model):
    __tablename__ = 'users'
    user_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id       = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number  = db.Column(db.String(15))
    student_id    = db.Column(db.String(20), unique=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    role = db.relationship('Role', back_populates='users')
