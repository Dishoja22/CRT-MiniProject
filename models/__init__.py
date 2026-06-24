from models.db import db

# Import models to ensure they register on metadata
from models.user import User
from models.student import Student
from models.faculty import Faculty
from models.course import Course, Enrollment, StudyMaterial
from models.attendance import Attendance
from models.assignment import Assignment, AssignmentSubmission
from models.quiz import Quiz, QuizQuestion, QuizResult
from models.announcement import Announcement
