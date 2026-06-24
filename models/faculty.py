from models.db import db

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='faculty_profile')
    courses = db.relationship('Course', back_populates='faculty')

    def __repr__(self):
        return f"<Faculty {self.designation} in {self.department}>"
