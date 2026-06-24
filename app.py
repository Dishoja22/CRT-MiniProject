import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from config import Config
from models import db, User, Student, Faculty, Course, Enrollment, StudyMaterial, Assignment, AssignmentSubmission, Attendance, Quiz, QuizQuestion, QuizResult, Announcement
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.faculty import faculty_bp
from routes.student import student_bp
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(student_bp)

    # Global page routes
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Custom context processor for current year and alerts
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Register HTTP error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403, error_message="Access Forbidden - You don't have authorization."), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message="Page Not Found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_message="Internal Server Error - Something went wrong."), 500

    # Ensure database tables exist and seed mock data on startup
    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    # If users table is empty, seed mock records
    if User.query.first() is None:
        print("Seeding database with default records...")
        
        # 1. Users & Passwords (password123 hashed)
        admin = User(full_name='System Administrator', email='admin@mrlms.edu', role='Admin')
        admin.set_password('password123')
        
        f1 = User(full_name='Dr. Sarah Jenkins', email='sarah.jenkins@mrlms.edu', role='Faculty')
        f1.set_password('password123')
        
        f2 = User(full_name='Prof. Alan Turing', email='alan.turing@mrlms.edu', role='Faculty')
        f2.set_password('password123')
        
        s1 = User(full_name='Jane Doe', email='jane.doe@student.mrlms.edu', role='Student')
        s1.set_password('password123')
        
        s2 = User(full_name='John Smith', email='john.smith@student.mrlms.edu', role='Student')
        s2.set_password('password123')
        
        s3 = User(full_name='Bob Johnson', email='bob.johnson@student.mrlms.edu', role='Student')
        s3.set_password('password123')
        
        db.session.add_all([admin, f1, f2, s1, s2, s3])
        db.session.flush()

        # 2. Profiles
        faculty1 = Faculty(user_id=f1.user_id, department='Computer Science', designation='Associate Professor')
        faculty2 = Faculty(user_id=f2.user_id, department='Information Technology', designation='Professor & Head')
        
        student1 = Student(user_id=s1.user_id, roll_number='CS2023001', department='Computer Science', year=3, section='A')
        student2 = Student(user_id=s2.user_id, roll_number='CS2023002', department='Computer Science', year=3, section='A')
        student3 = Student(user_id=s3.user_id, roll_number='IT2023001', department='Information Technology', year=3, section='B')
        
        db.session.add_all([faculty1, faculty2, student1, student2, student3])
        db.session.flush()

        # 3. Courses
        c1 = Course(course_name='Database Management Systems (DBMS)', description='Core course on relational databases, SQL, normalization, and indexing.', faculty_id=faculty1.faculty_id)
        c2 = Course(course_name='Design and Analysis of Algorithms', description='Core algorithms course covering greedy method, dynamic programming, and graphs.', faculty_id=faculty2.faculty_id)
        c3 = Course(course_name='Web Development Technologies', description='Advanced concepts of modern frontend styling, Flask backend, and REST APIs.', faculty_id=faculty1.faculty_id)
        
        db.session.add_all([c1, c2, c3])
        db.session.flush()

        # 4. Enrollments
        db.session.add_all([
            Enrollment(student_id=student1.student_id, course_id=c1.course_id),
            Enrollment(student_id=student1.student_id, course_id=c3.course_id),
            Enrollment(student_id=student2.student_id, course_id=c1.course_id),
            Enrollment(student_id=student2.student_id, course_id=c2.course_id),
            Enrollment(student_id=student3.student_id, course_id=c2.course_id),
            Enrollment(student_id=student3.student_id, course_id=c3.course_id),
        ])

        # 5. Study Materials
        db.session.add_all([
            StudyMaterial(course_id=c1.course_id, title='Introduction to SQL', file_path='intro_to_sql.pdf'),
            StudyMaterial(course_id=c1.course_id, title='ER Diagram Tutorial', file_path='er_tutorial.pdf'),
            StudyMaterial(course_id=c2.course_id, title='Dynamic Programming Notes', file_path='dp_notes.pdf'),
            StudyMaterial(course_id=c3.course_id, title='Flask REST API Architecture', file_path='flask_api_guide.pdf')
        ])

        # 6. Assignments & Submissions
        a1 = Assignment(course_id=c1.course_id, title='SQL Joins & Subqueries', description='Write SQL queries using JOIN and Nested queries. Submit PDF.', due_date=datetime.now() + timedelta(days=7))
        a2 = Assignment(course_id=c2.course_id, title='Dynamic Programming Knapsack', description='Implement 0/1 Knapsack solution and analyze time complexity.', due_date=datetime.now() + timedelta(days=14))
        a3 = Assignment(course_id=c3.course_id, title='Flask REST API Development', description='Develop a secure Flask API with registration and login endpoints. Submit a ZIP file.', due_date=datetime.now() + timedelta(days=5))
        db.session.add_all([a1, a2, a3])
        db.session.flush()

        sub1 = AssignmentSubmission(assignment_id=a1.assignment_id, student_id=student1.student_id, file_path='sub_jane_sql.pdf', marks=92)
        sub2 = AssignmentSubmission(assignment_id=a1.assignment_id, student_id=student2.student_id, file_path='sub_john_sql.pdf', marks=None)
        sub3 = AssignmentSubmission(assignment_id=a3.assignment_id, student_id=student1.student_id, file_path='sub_jane_flask.zip', marks=95)
        db.session.add_all([sub1, sub2, sub3])

        # 7. Quizzes, Questions & Results
        q1 = Quiz(course_id=c1.course_id, title='Relational Algebra Quiz', total_marks=10)
        q2 = Quiz(course_id=c2.course_id, title='Asymptotic Notations', total_marks=10)
        q3 = Quiz(course_id=c3.course_id, title='Web Protocols & Flask APIs', total_marks=10)
        db.session.add_all([q1, q2, q3])
        db.session.flush()

        qq1 = QuizQuestion(quiz_id=q1.quiz_id, question='Which operation is used to select tuples from a relation?', option_a='Projection', option_b='Selection', option_c='Join', option_d='Intersection', correct_answer='B')
        qq2 = QuizQuestion(quiz_id=q1.quiz_id, question='Which of the following is not a binary operation in Relational Algebra?', option_a='Project', option_b='Union', option_c='Set Difference', option_d='Cartesian Product', correct_answer='A')
        qq3 = QuizQuestion(quiz_id=q2.quiz_id, question='What is the time complexity of Quick Sort in the worst case?', option_a='O(N log N)', option_b='O(N)', option_c='O(N^2)', option_d='O(1)', correct_answer='C')
        qq4 = QuizQuestion(quiz_id=q3.quiz_id, question='What does HTTP status code 404 represent?', option_a='Internal Server Error', option_b='Forbidden', option_c='Not Found', option_d='Bad Request', correct_answer='C')
        qq5 = QuizQuestion(quiz_id=q3.quiz_id, question='Which HTTP method is typically used to create a resource on a server?', option_a='GET', option_b='POST', option_c='PUT', option_d='DELETE', correct_answer='B')
        db.session.add_all([qq1, qq2, qq3, qq4, qq5])

        qr1 = QuizResult(quiz_id=q1.quiz_id, student_id=student1.student_id, marks=10)
        qr2 = QuizResult(quiz_id=q1.quiz_id, student_id=student2.student_id, marks=5)
        qr3 = QuizResult(quiz_id=q3.quiz_id, student_id=student1.student_id, marks=10)
        db.session.add_all([qr1, qr2, qr3])

        # 8. Attendance Records
        for day in [5, 4, 3, 2, 1]:
            date_val = (datetime.now() - timedelta(days=day)).date()
            db.session.add_all([
                # DBMS
                Attendance(student_id=student1.student_id, course_id=c1.course_id, attendance_date=date_val, status='Present' if day != 2 else 'Absent'),
                Attendance(student_id=student2.student_id, course_id=c1.course_id, attendance_date=date_val, status='Present'),
                # Algorithms
                Attendance(student_id=student2.student_id, course_id=c2.course_id, attendance_date=date_val, status='Present' if day != 4 else 'Absent'),
                Attendance(student_id=student3.student_id, course_id=c2.course_id, attendance_date=date_val, status='Present' if day != 1 else 'Absent'),
                # Web Dev
                Attendance(student_id=student1.student_id, course_id=c3.course_id, attendance_date=date_val, status='Present'),
                Attendance(student_id=student3.student_id, course_id=c3.course_id, attendance_date=date_val, status='Present' if day != 3 else 'Absent')
            ])

        # 9. Announcements
        db.session.add_all([
            Announcement(title='Welcome to the MRLMS Portal!', message='Welcome to the new academic year portals. Please explore your respective dashboards and register for classes.'),
            Announcement(title='End Semester Examinations', message='The final assessment timetables will be posted by the controller office shortly. Keep tracking this board.')
        ])

        db.session.commit()
        print("Database seeded successfully!")

app = create_app()

if __name__ == '__main__':
    # Ensure static uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
