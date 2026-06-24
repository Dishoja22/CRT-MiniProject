from models.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Admin', 'Faculty', 'Student', name='user_roles'), nullable=False)

    # Relationships
    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete-orphan")
    faculty_profile = db.relationship('Faculty', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
