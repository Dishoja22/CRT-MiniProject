from models.db import db

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='student_profile')
    enrollments = db.relationship('Enrollment', back_populates='student', cascade="all, delete-orphan")
    submissions = db.relationship('AssignmentSubmission', back_populates='student', cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', back_populates='student', cascade="all, delete-orphan")
    quiz_results = db.relationship('QuizResult', back_populates='student', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.roll_number} ({self.department})>"
