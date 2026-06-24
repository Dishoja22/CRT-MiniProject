from models.db import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', name='attendance_status'), nullable=False)

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'attendance_date', name='_student_course_date_uc'),)

    # Relationships
    student = db.relationship('Student', back_populates='attendance_records')
    course = db.relationship('Course', back_populates='attendance_records')

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Course:{self.course_id} Date:{self.attendance_date} Status:{self.status}>"
