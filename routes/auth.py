from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from models import db, User, Student

auth_bp = Blueprint('auth', __name__)

# Custom decorator for role-based authorization
def role_required(roles):
    if isinstance(roles, str):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                # Redirect to their respective dashboard
                if current_user.role == 'Admin':
                    return redirect(url_for('admin.dashboard'))
                elif current_user.role == 'Faculty':
                    return redirect(url_for('faculty.dashboard'))
                elif current_user.role == 'Student':
                    return redirect(url_for('student.dashboard'))
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'Faculty':
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        if user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'Faculty':
            return redirect(url_for('faculty.dashboard'))
        elif user.role == 'Student':
            return redirect(url_for('student.dashboard'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        roll_number = request.form.get('roll_number')
        department = request.form.get('department')
        year = request.form.get('year')
        section = request.form.get('section')

        # Simple validation
        if not email or not full_name or not password or not roll_number:
            flash('Please fill out all required fields.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'danger')
            return redirect(url_for('auth.register'))

        existing_roll = Student.query.filter_by(roll_number=roll_number).first()
        if existing_roll:
            flash('Roll number already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Create new student user
        new_user = User(full_name=full_name, email=email, role='Student')
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.flush()  # Get the new_user.user_id before commit

        # Create Student profile
        new_student = Student(
            user_id=new_user.user_id,
            roll_number=roll_number,
            department=department,
            year=int(year) if year else 1,
            section=section if section else 'A'
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
