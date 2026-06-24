from models.db import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)

    # Relationships
    course = db.relationship('Course', back_populates='assignments')
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assignment {self.title}>"

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    marks = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_id', name='_assignment_student_uc'),)

    # Relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('Student', back_populates='submissions')

    def __repr__(self):
        return f"<Submission Student:{self.student_id} Assignment:{self.assignment_id} Marks:{self.marks}>"
