from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from routes.auth import role_required
from models import db, Course, Enrollment, StudyMaterial, Assignment, AssignmentSubmission, Attendance, Quiz, QuizQuestion, QuizResult, Announcement
from werkzeug.utils import secure_filename
from datetime import datetime
import os

student_bp = Blueprint('student', __name__, url_prefix='/student')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@student_bp.route('/dashboard')
@login_required
@role_required('Student')
def dashboard():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for('auth.logout'))

    # Enrolled Courses
    enrollments = Enrollment.query.filter_by(student_id=student.student_id).all()
    enrolled_courses = [e.course for e in enrollments]
    total_courses = len(enrolled_courses)
    course_ids = [c.course_id for c in enrolled_courses]

    # Attendance Percentage
    total_att = Attendance.query.filter_by(student_id=student.student_id).count()
    present_att = Attendance.query.filter_by(student_id=student.student_id, status='Present').count()
    attendance_pct = round((present_att / total_att * 100), 1) if total_att > 0 else 100

    # Pending Assignments (due date in the future and not submitted yet)
    pending_assignments_count = 0
    recent_assignments = []
    if course_ids:
        # Get all assignments in enrolled courses
        all_assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
        # Find those without submission
        submissions = AssignmentSubmission.query.filter_by(student_id=student.student_id).all()
        submitted_ids = [s.assignment_id for s in submissions]
        
        pending_assignments = [a for a in all_assignments if a.assignment_id not in submitted_ids and a.due_date > datetime.now()]
        pending_assignments_count = len(pending_assignments)
        
        # Recent 5 assignments due
        recent_assignments = sorted(all_assignments, key=lambda x: x.due_date)[:5]

    # Quiz scores
    quiz_results = QuizResult.query.filter_by(student_id=student.student_id).all()
    quiz_scores = [{
        'quiz_title': r.quiz.title,
        'course_name': r.quiz.course.course_name,
        'score': r.marks,
        'total': r.quiz.total_marks,
        'percentage': round((r.marks / r.quiz.total_marks * 100), 1) if r.quiz.total_marks > 0 else 0
    } for r in quiz_results]

    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    return render_template(
        'student/dashboard.html',
        total_courses=total_courses,
        attendance_pct=attendance_pct,
        pending_assignments_count=pending_assignments_count,
        quiz_scores=quiz_scores,
        recent_assignments=recent_assignments,
        recent_announcements=recent_announcements
    )

# --------------------------------------------------------
# Courses List & Study Materials
# --------------------------------------------------------
@student_bp.route('/courses')
@login_required
@role_required('Student')
def courses():
    student = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=student.student_id).all()
    enrolled_courses = [e.course for e in enrollments]
    return render_template('student/courses.html', courses=enrolled_courses)

@student_bp.route('/courses/<int:course_id>/materials')
@login_required
@role_required('Student')
def course_details(course_id):
    student = current_user.student_profile
    # Verify enrollment
    enrollment = Enrollment.query.filter_by(student_id=student.student_id, course_id=course_id).first_or_404()
    course = enrollment.course
    materials = StudyMaterial.query.filter_by(course_id=course_id).all()
    
    # Get assignments
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    submissions = AssignmentSubmission.query.filter_by(student_id=student.student_id).all()
    submissions_map = {s.assignment_id: s for s in submissions}

    # Get quizzes
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    results = QuizResult.query.filter_by(student_id=student.student_id).all()
    results_map = {r.quiz_id: r for r in results}

    return render_template(
        'student/course_details.html',
        course=course,
        materials=materials,
        assignments=assignments,
        submissions_map=submissions_map,
        quizzes=quizzes,
        results_map=results_map
    )

# --------------------------------------------------------
# Assignment Submission
# --------------------------------------------------------
@student_bp.route('/assignments/submit/<int:assignment_id>', methods=['POST'])
@login_required
@role_required('Student')
def submit_assignment(assignment_id):
    student = current_user.student_profile
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify enrollment in course
    enrollment = Enrollment.query.filter_by(student_id=student.student_id, course_id=assignment.course_id).first_or_404()

    # Check if already submitted
    existing_sub = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student.student_id).first()
    if existing_sub:
        flash("You have already submitted this assignment.", "warning")
        return redirect(url_for('student.course_details', course_id=assignment.course_id))

    file = request.files.get('file')
    if not file or file.filename == '':
        flash("No file selected.", "danger")
        return redirect(url_for('student.course_details', course_id=assignment.course_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique file naming scheme: sub_studentID_assignmentID_timestamp.ext
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"sub_{student.student_id}_{assignment_id}_{int(datetime.now().timestamp())}.{file_ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure folders exist
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        file.save(upload_path)

        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student.student_id,
            file_path=unique_filename
        )
        db.session.add(submission)
        db.session.commit()
        flash("Assignment submitted successfully!", "success")
    else:
        flash("Invalid file extension. Please upload PDF, DOCX, PPT or images.", "danger")

    return redirect(url_for('student.course_details', course_id=assignment.course_id))

# --------------------------------------------------------
# Quiz Attempt
# --------------------------------------------------------
@student_bp.route('/quizzes/attempt/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@role_required('Student')
def attempt_quiz(quiz_id):
    student = current_user.student_profile
    quiz = Quiz.query.get_or_404(quiz_id)

    # Verify enrollment
    enrollment = Enrollment.query.filter_by(student_id=student.student_id, course_id=quiz.course_id).first_or_404()

    # Check if already attempted
    existing_result = QuizResult.query.filter_by(quiz_id=quiz_id, student_id=student.student_id).first()
    if existing_result:
        flash("You have already attempted this quiz.", "warning")
        return redirect(url_for('student.course_details', course_id=quiz.course_id))

    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        flash("This quiz doesn't have any questions yet.", "warning")
        return redirect(url_for('student.course_details', course_id=quiz.course_id))

    if request.method == 'POST':
        # Grade the attempt
        score = 0
        for q in questions:
            user_answer = request.form.get(f'question_{q.question_id}')
            if user_answer == q.correct_answer:
                # Assuming 1 mark per question or dynamic weighting
                score += 1

        # Scale score to quiz total marks if needed
        # In a B.Tech mini project, a simple questions-count equals total marks or we scale it
        # Let's scale it so score aligns: (score / questions_count) * total_marks
        scaled_score = int(round((score / len(questions)) * quiz.total_marks))

        # Save QuizResult
        result = QuizResult(
            quiz_id=quiz_id,
            student_id=student.student_id,
            marks=scaled_score
        )
        db.session.add(result)
        db.session.commit()

        flash(f"Quiz completed! You scored {scaled_score}/{quiz.total_marks} marks.", "success")
        return redirect(url_for('student.course_details', course_id=quiz.course_id))

    return render_template('student/quiz_attempt.html', quiz=quiz, questions=questions)

# --------------------------------------------------------
# Detailed Attendance Report
# --------------------------------------------------------
@student_bp.route('/attendance')
@login_required
@role_required('Student')
def attendance():
    student = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=student.student_id).all()
    
    # Calculate detailed attendance stats per course
    attendance_report = []
    for e in enrollments:
        total = Attendance.query.filter_by(student_id=student.student_id, course_id=e.course_id).count()
        present = Attendance.query.filter_by(student_id=student.student_id, course_id=e.course_id, status='Present').count()
        pct = round((present / total * 100), 1) if total > 0 else 100
        attendance_report.append({
            'course_name': e.course.course_name,
            'total_classes': total,
            'present': present,
            'absent': total - present,
            'percentage': pct
        })

    # Fetch recent logs
    recent_logs = Attendance.query.filter_by(student_id=student.student_id).order_by(Attendance.attendance_date.desc()).limit(15).all()

    return render_template('student/attendance.html', attendance_report=attendance_report, recent_logs=recent_logs)

# --------------------------------------------------------
# Detailed Marks Report
# --------------------------------------------------------
@student_bp.route('/marks')
@login_required
@role_required('Student')
def marks():
    student = current_user.student_profile
    
    # Fetch assignment submissions
    submissions = AssignmentSubmission.query.filter_by(student_id=student.student_id).all()

    # Fetch quiz results
    quiz_results = QuizResult.query.filter_by(student_id=student.student_id).all()

    return render_template('student/marks.html', submissions=submissions, quiz_results=quiz_results)
