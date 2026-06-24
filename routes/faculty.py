from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from routes.auth import role_required
from models import db, Course, Enrollment, StudyMaterial, Assignment, AssignmentSubmission, Attendance, Quiz, QuizQuestion, QuizResult, Announcement, Student
from werkzeug.utils import secure_filename
from sqlalchemy import func
import os
from datetime import datetime

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@faculty_bp.route('/dashboard')
@login_required
@role_required('Faculty')
def dashboard():
    faculty = current_user.faculty_profile
    if not faculty:
        flash("Faculty profile not found.", "danger")
        return redirect(url_for('auth.logout'))

    courses = Course.query.filter_by(faculty_id=faculty.faculty_id).all()
    course_ids = [c.course_id for c in courses]

    # Total Courses
    total_courses = len(courses)

    # Students Enrolled
    students_enrolled = 0
    if course_ids:
        students_enrolled = Enrollment.query.filter(Enrollment.course_id.in_(course_ids)).count()

    # Assignments Created
    assignments_created = 0
    if course_ids:
        assignments_created = Assignment.query.filter(Assignment.course_id.in_(course_ids)).count()

    # Quiz performance (average grade)
    quiz_perf = 0
    if course_ids:
        quiz_avg = db.session.query(func.avg(QuizResult.marks)).join(Quiz, QuizResult.quiz_id == Quiz.quiz_id)\
            .filter(Quiz.course_id.in_(course_ids)).scalar()
        quiz_total = db.session.query(func.sum(Quiz.total_marks)).join(QuizResult, QuizResult.quiz_id == Quiz.quiz_id)\
            .filter(Quiz.course_id.in_(course_ids)).scalar()
        
        if quiz_avg and quiz_total:
            # Simple average score percentage
            results = QuizResult.query.join(Quiz).filter(Quiz.course_id.in_(course_ids)).all()
            total_earned = sum([r.marks for r in results])
            total_possible = sum([r.quiz.total_marks for r in results])
            quiz_perf = round((total_earned / total_possible * 100), 1) if total_possible > 0 else 0

    # Attendance Summary
    att_summary = 0
    if course_ids:
        total_att = Attendance.query.filter(Attendance.course_id.in_(course_ids)).count()
        present_att = Attendance.query.filter(Attendance.course_id.in_(course_ids), Attendance.status == 'Present').count()
        att_summary = round((present_att / total_att * 100), 1) if total_att > 0 else 100

    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    return render_template(
        'faculty/dashboard.html',
        total_courses=total_courses,
        students_enrolled=students_enrolled,
        assignments_created=assignments_created,
        quiz_perf=quiz_perf,
        att_summary=att_summary,
        courses=courses,
        recent_announcements=recent_announcements
    )

# --------------------------------------------------------
# Course Materials
# --------------------------------------------------------
@faculty_bp.route('/courses/<int:course_id>/materials', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def course_materials(course_id):
    faculty = current_user.faculty_profile
    course = Course.query.filter_by(course_id=course_id, faculty_id=faculty.faculty_id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('file')

        if not title or not file:
            flash("Please specify a title and select a file.", "danger")
            return redirect(url_for('faculty.course_materials', course_id=course_id))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to make filename unique
            unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Ensure upload folder exists
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            
            file.save(upload_path)

            material = StudyMaterial(course_id=course.course_id, title=title, file_path=unique_filename)
            db.session.add(material)
            db.session.commit()
            flash("Study material uploaded successfully!", "success")
        else:
            flash("Allowed file types: PDF, DOC/DOCX, PPT/PPTX, PNG, JPG/JPEG.", "danger")

        return redirect(url_for('faculty.course_materials', course_id=course_id))

    materials = StudyMaterial.query.filter_by(course_id=course.course_id).all()
    return render_template('faculty/materials.html', course=course, materials=materials)

@faculty_bp.route('/materials/delete/<int:material_id>', methods=['POST'])
@login_required
@role_required('Faculty')
def delete_material(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    course_id = material.course_id
    faculty = current_user.faculty_profile
    # Verify course ownership
    if material.course.faculty_id != faculty.faculty_id:
        abort(403)

    # Delete local file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(material)
    db.session.commit()
    flash("Study material deleted successfully.", "success")
    return redirect(url_for('faculty.course_materials', course_id=course_id))

# --------------------------------------------------------
# Attendance Marking
# --------------------------------------------------------
@faculty_bp.route('/courses/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def course_attendance(course_id):
    faculty = current_user.faculty_profile
    course = Course.query.filter_by(course_id=course_id, faculty_id=faculty.faculty_id).first_or_404()
    
    # Enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [e.student for e in enrollments]

    # Select date
    date_str = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    if request.method == 'POST':
        # Attendance submission
        date_str = request.form.get('date')
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Save attendance
        for student in students:
            status = request.form.get(f'attendance_{student.student_id}')
            if status in ['Present', 'Absent']:
                # Update or Insert
                record = Attendance.query.filter_by(
                    student_id=student.student_id,
                    course_id=course_id,
                    attendance_date=attendance_date
                ).first()

                if record:
                    record.status = status
                else:
                    record = Attendance(
                        student_id=student.student_id,
                        course_id=course_id,
                        attendance_date=attendance_date,
                        status=status
                    )
                    db.session.add(record)
        
        db.session.commit()
        flash(f"Attendance recorded for {attendance_date.strftime('%d-%b-%Y')}!", "success")
        return redirect(url_for('faculty.course_attendance', course_id=course_id, date=date_str))

    # Fetch existing records for this date to pre-populate checklist
    existing_records = Attendance.query.filter_by(course_id=course_id, attendance_date=attendance_date).all()
    attendance_map = {r.student_id: r.status for r in existing_records}

    return render_template(
        'faculty/attendance.html',
        course=course,
        students=students,
        selected_date=date_str,
        attendance_map=attendance_map
    )

# --------------------------------------------------------
# Assignments Management
# --------------------------------------------------------
@faculty_bp.route('/courses/<int:course_id>/assignments', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def course_assignments(course_id):
    faculty = current_user.faculty_profile
    course = Course.query.filter_by(course_id=course_id, faculty_id=faculty.faculty_id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')

        if not title or not due_date_str:
            flash("Please fill in the title and due date.", "danger")
            return redirect(url_for('faculty.course_assignments', course_id=course_id))

        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        
        assignment = Assignment(course_id=course.course_id, title=title, description=description, due_date=due_date)
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully!", "success")
        return redirect(url_for('faculty.course_assignments', course_id=course_id))

    assignments = Assignment.query.filter_by(course_id=course.course_id).all()
    return render_template('faculty/assignments.html', course=course, assignments=assignments)

@faculty_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    faculty = current_user.faculty_profile
    if assignment.course.faculty_id != faculty.faculty_id:
        abort(403)

    if request.method == 'POST':
        # Grading action
        submission_id = request.form.get('submission_id', type=int)
        marks = request.form.get('marks', type=int)

        submission = AssignmentSubmission.query.get_or_404(submission_id)
        submission.marks = marks
        db.session.commit()
        flash(f"Submission graded with {marks} marks!", "success")
        return redirect(url_for('faculty.view_submissions', assignment_id=assignment_id))

    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
    # List of enrolled students who haven't submitted yet
    enrolled_students = [e.student for e in Enrollment.query.filter_by(course_id=assignment.course_id).all()]
    submitted_student_ids = [s.student_id for s in submissions]
    pending_students = [s for s in enrolled_students if s.student_id not in submitted_student_ids]

    return render_template(
        'faculty/grade.html',
        assignment=assignment,
        submissions=submissions,
        pending_students=pending_students
    )

# --------------------------------------------------------
# Quizzes Management
# --------------------------------------------------------
@faculty_bp.route('/courses/<int:course_id>/quizzes', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def course_quizzes(course_id):
    faculty = current_user.faculty_profile
    course = Course.query.filter_by(course_id=course_id, faculty_id=faculty.faculty_id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title')
        total_marks = request.form.get('total_marks', type=int)

        if not title or not total_marks:
            flash("Please fill in the title and total marks.", "danger")
            return redirect(url_for('faculty.course_quizzes', course_id=course_id))

        quiz = Quiz(course_id=course.course_id, title=title, total_marks=total_marks)
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz created successfully! Now add questions.", "success")
        return redirect(url_for('faculty.quiz_questions', quiz_id=quiz.quiz_id))

    quizzes = Quiz.query.filter_by(course_id=course.course_id).all()
    return render_template('faculty/quizzes.html', course=course, quizzes=quizzes)

@faculty_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    faculty = current_user.faculty_profile
    if quiz.course.faculty_id != faculty.faculty_id:
        abort(403)

    if request.method == 'POST':
        question_text = request.form.get('question')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_answer = request.form.get('correct_answer')

        if not question_text or not option_a or not option_b or not option_c or not option_d or not correct_answer:
            flash("Please fill out the question and all four options.", "danger")
            return redirect(url_for('faculty.quiz_questions', quiz_id=quiz_id))

        q = QuizQuestion(
            quiz_id=quiz.quiz_id,
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer
        )
        db.session.add(q)
        db.session.commit()
        flash("Question added to quiz!", "success")
        return redirect(url_for('faculty.quiz_questions', quiz_id=quiz_id))

    questions = QuizQuestion.query.filter_by(quiz_id=quiz.quiz_id).all()
    return render_template('faculty/questions.html', quiz=quiz, questions=questions)

@faculty_bp.route('/quizzes/delete/<int:quiz_id>', methods=['POST'])
@login_required
@role_required('Faculty')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course_id = quiz.course_id
    faculty = current_user.faculty_profile
    if quiz.course.faculty_id != faculty.faculty_id:
        abort(403)

    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully.", "success")
    return redirect(url_for('faculty.course_quizzes', course_id=course_id))

# --------------------------------------------------------
# General Announcements
# --------------------------------------------------------
@faculty_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def post_announcements():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        
        ann = Announcement(title=title, message=message)
        db.session.add(ann)
        db.session.commit()
        flash("Announcement posted successfully!", "success")
        return redirect(url_for('faculty.post_announcements'))

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('faculty/announcements.html', announcements=announcements)
