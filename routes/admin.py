from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from routes.auth import role_required
from models import db, User, Student, Faculty, Course, Enrollment, Assignment, AssignmentSubmission, Attendance, Quiz, QuizResult, Announcement
from sqlalchemy import func
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('Admin')
def dashboard():
    # Statistics calculations
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_courses = Course.query.count()
    total_assignments = Assignment.query.count()
    total_quiz_attempts = QuizResult.query.count()

    # Average attendance percentage
    total_att = Attendance.query.count()
    present_att = Attendance.query.filter_by(status='Present').count()
    avg_attendance = round((present_att / total_att * 100), 1) if total_att > 0 else 0

    # Top performing students based on average quiz marks
    top_students_data = db.session.query(
        Student, 
        User.full_name,
        func.avg(QuizResult.marks).label('avg_marks')
    ).join(User, Student.user_id == User.user_id)\
     .join(QuizResult, Student.student_id == QuizResult.student_id)\
     .group_by(Student.student_id)\
     .order_by(db.desc('avg_marks'))\
     .limit(5).all()

    # Formatted list of top students
    top_students = []
    for s, name, avg_m in top_students_data:
        top_students.append({
            'name': name,
            'roll_number': s.roll_number,
            'department': s.department,
            'avg_marks': round(float(avg_m), 1)
        })

    # Recent announcements
    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_courses=total_courses,
        total_assignments=total_assignments,
        total_quiz_attempts=total_quiz_attempts,
        avg_attendance=avg_attendance,
        top_students=top_students,
        recent_announcements=recent_announcements
    )

# --------------------------------------------------------
# CRUD Students
# --------------------------------------------------------
@admin_bp.route('/students', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_students():
    if request.method == 'POST':
        # Create student action
        action = request.form.get('action')
        if action == 'add':
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            password = request.form.get('password', 'student123')
            roll_number = request.form.get('roll_number')
            department = request.form.get('department')
            year = request.form.get('year', type=int)
            section = request.form.get('section')

            if User.query.filter_by(email=email).first():
                flash("Email already exists.", "danger")
                return redirect(url_for('admin.manage_students'))
            if Student.query.filter_by(roll_number=roll_number).first():
                flash("Roll Number already exists.", "danger")
                return redirect(url_for('admin.manage_students'))

            user = User(full_name=full_name, email=email, role='Student')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            student = Student(user_id=user.user_id, roll_number=roll_number, department=department, year=year, section=section)
            db.session.add(student)
            db.session.commit()
            flash("Student added successfully!", "success")
        
        elif action == 'edit':
            student_id = request.form.get('student_id', type=int)
            student = Student.query.get_or_404(student_id)
            user = student.user

            user.full_name = request.form.get('full_name')
            user.email = request.form.get('email')
            student.roll_number = request.form.get('roll_number')
            student.department = request.form.get('department')
            student.year = request.form.get('year', type=int)
            student.section = request.form.get('section')

            db.session.commit()
            flash("Student details updated successfully!", "success")

        return redirect(url_for('admin.manage_students'))

    students = Student.query.all()
    return render_template('admin/students.html', students=students)

@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    db.session.delete(user) # Cascades to student
    db.session.commit()
    flash("Student deleted successfully.", "success")
    return redirect(url_for('admin.manage_students'))

# --------------------------------------------------------
# CRUD Faculty
# --------------------------------------------------------
@admin_bp.route('/faculty', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_faculty():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            password = request.form.get('password', 'faculty123')
            department = request.form.get('department')
            designation = request.form.get('designation')

            if User.query.filter_by(email=email).first():
                flash("Email already exists.", "danger")
                return redirect(url_for('admin.manage_faculty'))

            user = User(full_name=full_name, email=email, role='Faculty')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            faculty = Faculty(user_id=user.user_id, department=department, designation=designation)
            db.session.add(faculty)
            db.session.commit()
            flash("Faculty member added successfully!", "success")
            
        elif action == 'edit':
            faculty_id = request.form.get('faculty_id', type=int)
            faculty = Faculty.query.get_or_404(faculty_id)
            user = faculty.user

            user.full_name = request.form.get('full_name')
            user.email = request.form.get('email')
            faculty.department = request.form.get('department')
            faculty.designation = request.form.get('designation')

            db.session.commit()
            flash("Faculty details updated successfully!", "success")

        return redirect(url_for('admin.manage_faculty'))

    faculty_list = Faculty.query.all()
    return render_template('admin/faculty.html', faculty_list=faculty_list)

@admin_bp.route('/faculty/delete/<int:faculty_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_faculty(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    user = faculty.user
    db.session.delete(user) # Cascades to faculty
    db.session.commit()
    flash("Faculty deleted successfully.", "success")
    return redirect(url_for('admin.manage_faculty'))

# --------------------------------------------------------
# CRUD Courses
# --------------------------------------------------------
@admin_bp.route('/courses', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_courses():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            course_name = request.form.get('course_name')
            description = request.form.get('description')
            faculty_id = request.form.get('faculty_id', type=int)
            if faculty_id == 0:
                faculty_id = None

            course = Course(course_name=course_name, description=description, faculty_id=faculty_id)
            db.session.add(course)
            db.session.commit()
            flash("Course created successfully!", "success")
            
        elif action == 'edit':
            course_id = request.form.get('course_id', type=int)
            course = Course.query.get_or_404(course_id)
            course.course_name = request.form.get('course_name')
            course.description = request.form.get('description')
            
            fac_id = request.form.get('faculty_id', type=int)
            course.faculty_id = fac_id if fac_id != 0 else None

            db.session.commit()
            flash("Course updated successfully!", "success")

        return redirect(url_for('admin.manage_courses'))

    courses = Course.query.all()
    faculty_list = Faculty.query.all()
    return render_template('admin/courses.html', courses=courses, faculty_list=faculty_list)

@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully.", "success")
    return redirect(url_for('admin.manage_courses'))

# --------------------------------------------------------
# Manage Announcements
# --------------------------------------------------------
@admin_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_announcements():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = request.form.get('title')
            message = request.form.get('message')
            
            ann = Announcement(title=title, message=message)
            db.session.add(ann)
            db.session.commit()
            flash("Announcement posted successfully!", "success")
            
        elif action == 'delete':
            announcement_id = request.form.get('announcement_id', type=int)
            ann = Announcement.query.get_or_404(announcement_id)
            db.session.delete(ann)
            db.session.commit()
            flash("Announcement deleted successfully.", "success")
            
        return redirect(url_for('admin.manage_announcements'))

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

# --------------------------------------------------------
# Reports Module
# --------------------------------------------------------
@admin_bp.route('/reports')
@login_required
@role_required('Admin')
def reports():
    # Gather academic summary data for reports screen
    courses = Course.query.all()
    student_count = Student.query.count()
    
    # Calculate attendance percentages for courses
    attendance_report = []
    for c in courses:
        total = Attendance.query.filter_by(course_id=c.course_id).count()
        present = Attendance.query.filter_by(course_id=c.course_id, status='Present').count()
        percentage = round((present / total * 100), 1) if total > 0 else 100
        attendance_report.append({
            'course_name': c.course_name,
            'total_classes': total,
            'avg_attendance': percentage
        })

    # Calculate assignment submission details
    assignment_report = []
    assignments = Assignment.query.all()
    for a in assignments:
        total_enrolled = Enrollment.query.filter_by(course_id=a.course_id).count()
        submissions = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id).count()
        graded = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id).filter(AssignmentSubmission.marks.isnot(None)).count()
        rate = round((submissions / total_enrolled * 100), 1) if total_enrolled > 0 else 0
        assignment_report.append({
            'title': a.title,
            'course': a.course.course_name,
            'enrolled': total_enrolled,
            'submissions': submissions,
            'graded': graded,
            'submission_rate': rate
        })

    # Quiz performance report
    quiz_report = []
    quizzes = Quiz.query.all()
    for q in quizzes:
        attempts = QuizResult.query.filter_by(quiz_id=q.quiz_id).count()
        avg_score = db.session.query(func.avg(QuizResult.marks)).filter_by(quiz_id=q.quiz_id).scalar() or 0
        quiz_report.append({
            'title': q.title,
            'course': q.course.course_name,
            'total_attempts': attempts,
            'max_marks': q.total_marks,
            'average_marks': round(float(avg_score), 1)
        })

    return render_template(
        'admin/reports.html',
        attendance_report=attendance_report,
        assignment_report=assignment_report,
        quiz_report=quiz_report
    )

# --------------------------------------------------------
# JSON Analytics API for Chart.js
# --------------------------------------------------------
@admin_bp.route('/api/analytics')
@login_required
@role_required('Admin')
def api_analytics():
    # 1. Student Enrollment Trends (by Year)
    enrollment_trends_data = db.session.query(
        Student.year, func.count(Student.student_id)
    ).group_by(Student.year).order_by(Student.year).all()
    
    enrollment_trends = {
        "labels": [f"Year {y[0]}" for y in enrollment_trends_data],
        "data": [y[1] for y in enrollment_trends_data]
    }

    # 2. Attendance Trends (Present vs Absent for top courses)
    courses = Course.query.all()
    attendance_labels = [c.course_name[:15] + '...' if len(c.course_name) > 15 else c.course_name for c in courses]
    attendance_data = []
    for c in courses:
        total = Attendance.query.filter_by(course_id=c.course_id).count()
        present = Attendance.query.filter_by(course_id=c.course_id, status='Present').count()
        percentage = round((present / total * 100), 1) if total > 0 else 0
        attendance_data.append(percentage)
    
    attendance_trends = {
        "labels": attendance_labels,
        "data": attendance_data
    }

    # 3. Assignment Submission Rates
    assignments = Assignment.query.all()
    assign_labels = [a.title[:15] + '...' if len(a.title) > 15 else a.title for a in assignments]
    assign_rates = []
    for a in assignments:
        total_students = Enrollment.query.filter_by(course_id=a.course_id).count()
        subs = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id).count()
        rate = round((subs / total_students * 100), 1) if total_students > 0 else 0
        assign_rates.append(rate)

    assignment_submissions = {
        "labels": assign_labels,
        "data": assign_rates
    }

    # 4. Quiz Performance Analysis (Avg Score vs Total Score)
    quizzes = Quiz.query.all()
    quiz_labels = [q.title[:15] + '...' if len(q.title) > 15 else q.title for q in quizzes]
    quiz_avg = []
    for q in quizzes:
        avg_score = db.session.query(func.avg(QuizResult.marks)).filter_by(quiz_id=q.quiz_id).scalar() or 0
        percentage = round((float(avg_score) / q.total_marks * 100), 1) if q.total_marks > 0 else 0
        quiz_avg.append(percentage)

    quiz_performance = {
        "labels": quiz_labels,
        "data": quiz_avg
    }

    # 5. Course Popularity Analysis (Enrolled count)
    courses_popularity_data = db.session.query(
        Course.course_name, func.count(Enrollment.enrollment_id)
    ).outerjoin(Enrollment, Course.course_id == Enrollment.course_id)\
     .group_by(Course.course_id).all()
     
    course_popularity = {
        "labels": [c[0][:15] + '...' if len(c[0]) > 15 else c[0] for c in courses_popularity_data],
        "data": [c[1] for c in courses_popularity_data]
    }

    # 6. Student Performance Analysis (Histogram of quiz scores range 0-40, 40-70, 70-100)
    quiz_results = QuizResult.query.all()
    low, mid, high = 0, 0, 0
    for r in quiz_results:
        percentage = (r.marks / r.quiz.total_marks * 100) if r.quiz.total_marks > 0 else 0
        if percentage < 50:
            low += 1
        elif percentage < 80:
            mid += 1
        else:
            high += 1

    student_performance = {
        "labels": ["Below 50%", "50% - 80%", "Above 80%"],
        "data": [low, mid, high]
    }

    # 7. Department-wise Analytics (Student Count)
    dept_data = db.session.query(
        Student.department, func.count(Student.student_id)
    ).group_by(Student.department).all()

    department_analytics = {
        "labels": [d[0] for d in dept_data],
        "data": [d[1] for d in dept_data]
    }

    # 8. Faculty Performance Analytics (Number of courses assigned)
    faculty_data = db.session.query(
        User.full_name, func.count(Course.course_id)
    ).join(Faculty, User.user_id == Faculty.user_id)\
     .outerjoin(Course, Faculty.faculty_id == Course.faculty_id)\
     .group_by(Faculty.faculty_id).all()

    faculty_analytics = {
        "labels": [f[0].split()[-1] if f[0] else "Faculty" for f in faculty_data], # Use last name
        "data": [f[1] for f in faculty_data]
    }

    return jsonify({
        "enrollments": enrollment_trends,
        "attendance": attendance_trends,
        "assignments": assignment_submissions,
        "quizzes": quiz_performance,
        "popularity": course_popularity,
        "performance": student_performance,
        "departments": department_analytics,
        "faculty": faculty_analytics
    })
