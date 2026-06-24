from models.db import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)

    # Relationships
    course = db.relationship('Course', back_populates='quizzes')
    questions = db.relationship('QuizQuestion', back_populates='quiz', cascade="all, delete-orphan")
    results = db.relationship('QuizResult', back_populates='quiz', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.title}>"

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

    # Relationships
    quiz = db.relationship('Quiz', back_populates='questions')

    def __repr__(self):
        return f"<QuizQuestion {self.question_id} Quiz:{self.quiz_id}>"

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    __table_args__ = (db.UniqueConstraint('quiz_id', 'student_id', name='_quiz_student_uc'),)

    # Relationships
    quiz = db.relationship('Quiz', back_populates='results')
    student = db.relationship('Student', back_populates='quiz_results')

    def __repr__(self):
        return f"<QuizResult Student:{self.student_id} Quiz:{self.quiz_id} Marks:{self.marks}>"
