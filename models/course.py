from models.db import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id', ondelete='SET NULL'), nullable=True)

    # Relationships
    faculty = db.relationship('Faculty', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")
    study_materials = db.relationship('StudyMaterial', back_populates='course', cascade="all, delete-orphan")
    assignments = db.relationship('Assignment', back_populates='course', cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', back_populates='course', cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', back_populates='course', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.course_name}>"

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

    # Relationships
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f"<Enrollment Student:{self.student_id} Course:{self.course_id}>"

class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    
    material_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relationships
    course = db.relationship('Course', back_populates='study_materials')

    def __repr__(self):
        return f"<StudyMaterial {self.title}>"
