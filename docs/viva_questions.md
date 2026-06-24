# MRLMS Project Viva Voce: Q&A Prep Sheet

This document contains 25+ comprehensive questions and answers covering the architecture, code implementation, database configuration, security features, and dependencies of the Multi-Role Learning Management System.

---

## 💻 Section 1: Python Flask Framework & Blueprints

### Q1: What is the benefit of using Flask Blueprints in this project?
**Answer**: Blueprints allow us to modularize our application into distinct components. In this project, we partitioned our routing into four logical Blueprints:
- `auth.py` for login, logout, and registration
- `admin.py` for administrative CRUD operations
- `faculty.py` for teaching-related operations (attendance, material uploads, quiz generation)
- `student.py` for class rooms, downloads, and quiz attempts
This keeps the code clean, avoids a massive `app.py` file, and enables cleaner team collaboration and separate namespaces.

### Q2: How did you implement Role-Based Access Control (RBAC) in Flask?
**Answer**: We wrote a custom decorator `@role_required(roles)` inside `routes/auth.py`. This decorator wraps the standard Flask routing endpoints:
1. It first checks if the user is authenticated via `flask_login.current_user.is_authenticated`.
2. It then inspects `current_user.role`.
3. If the role does not match the list of allowed roles for that route, it flashes a "permission denied" warning and redirects them to their respective role-based dashboard, or returns a `403 Forbidden` error.

### Q3: What is the role of `WSGI` and how does Flask run locally vs in production?
**Answer**: WSGI (Web Server Gateway Interface) is a standard protocol that allows Python web applications to communicate with web servers (like Nginx or Apache). Locally, Flask runs its built-in development server (Werkzeug). In production, Flask should be served behind a WSGI container like `Gunicorn` or `uWSGI` proxy-passed through `Nginx` for speed, concurrency, and security.

### Q4: How are custom error pages handled in this application?
**Answer**: We registered application-level error handlers in `app.py` using `@app.errorhandler()` for codes `403` (Forbidden), `404` (Not Found), and `500` (Internal Server Error). These handlers intercept standard HTTP exceptions, render a themed response inside the `base.html` shell, and supply descriptive messages, improving the overall user experience.

---

## 🗄️ Section 2: Databases & SQLAlchemy ORM

### Q5: What is SQLAlchemy and why did you use it over raw SQL queries?
**Answer**: SQLAlchemy is an Object-Relational Mapper (ORM). It allows us to interact with the database using Python classes (models) and methods instead of writing raw SQL. Benefits include:
- **Database Abstraction**: We can switch from SQLite (for dev) to MySQL (for prod) by changing a single connection URI string in `config.py` without rewriting queries.
- **SQL Injection Prevention**: SQLAlchemy parameterized statements automatically by default, neutralizing input-based SQL injection.
- **Clean Object Mapping**: Retrieving a user's student profile is as simple as accessing `user.student_profile`.

### Q6: How did you solve circular import issues with the database object `db` in Flask?
**Answer**: We isolated the initialization of `db = SQLAlchemy()` into a dedicated file named `models/db.py`. 
Previously, initializing `db` inside `models/__init__.py` while importing models caused circular imports because the models also had to import `db` from `models`. With `models/db.py` only declaring `db`, the models import it directly, and `models/__init__.py` imports the finished classes.

### Q7: Explain the relationship between the `users`, `students`, and `faculty` tables in your database schema.
**Answer**: 
- The `users` table holds primary credentials (name, email, password, role).
- The `students` and `faculty` tables represent role-specific details.
- Both tables have a `user_id` column configured as a Foreign Key referencing `users(user_id)` with a `CASCADE` delete constraint. This ensures that deleting a user account automatically wipes out their student or faculty record. 
- In SQLAlchemy, this is mapped as a one-to-one relationship using `uselist=False`.

### Q8: What does the constraint `db.UniqueConstraint('student_id', 'course_id', 'attendance_date')` accomplish in the `Attendance` table?
**Answer**: This defines a composite unique index constraint. It prevents duplicate roll call records, ensuring that a single student cannot be marked both Present and Absent for the same course on the same day. If a duplicate insert is attempted, the database rejects the transaction.

### Q9: Why is `ondelete='SET NULL'` used for `faculty_id` in the `courses` table?
**Answer**: If a faculty member leaves the institution and their user profile is deleted, we want their assigned courses to remain in our database registry (so student enrollments and records are not lost). Setting `faculty_id` to `SET NULL` keeps the course record active but unassigned.

---

## 🔒 Section 3: Security & Session Management

### Q10: How does `Flask-Login` manage sessions, and what is the "user loader"?
**Answer**: `Flask-Login` handles the user session lifecycle. When a user logs in, their `user_id` is stored in the client-side session cookie. For subsequent requests, the "user loader" callback function (registered with `@login_manager.user_loader` in `app.py`) runs. It queries `User.query.get(int(user_id))` to hydrate the `current_user` object.

### Q11: Explain password hashing in this project. What algorithm is used?
**Answer**: We never store raw passwords. We use `werkzeug.security` which implements password hashing using PBKDF2 with SHA-256 key stretching (or Scrypt depending on system configurations). The hashed value looks like `pbkdf2:sha256:600000$salt$hash`. When a user attempts to log in, `check_password_hash()` compares the hash of the entered text with the stored string.

### Q12: How are files validated during upload to prevent arbitrary code execution (RCE)?
**Answer**: We implement three layers of validation:
1. **Extension Whitelisting**: We check the file extension against a list in `config.py` (`pdf`, `docx`, `ppt`, `png`, `jpg`).
2. **Path Sanitization**: We pass the filename through `secure_filename()` from Werkzeug to strip path traversals (like `../../filename`).
3. **Unique Naming**: We prefix file paths with timestamp strings (like `sub_studentId_assignmentId_timestamp.pdf`) to prevent file collisions and obfuscate server file structures.

### Q13: What is Cross-Site Scripting (XSS) and how does this application prevent it?
**Answer**: XSS occurs when malicious HTML/JS scripts are injected into web input forms and executed on other users' browsers. In MRLMS, Jinja2 template engines auto-escape all variables by default (turning `<script>` into `&lt;script&gt;`), rendering them as static text rather than executing code.

---

## 📈 Section 4: Frontend & Data Analytics

### Q14: How are the Chart.js graphs populated dynamically?
**Answer**: We built a RESTful API endpoint at `/admin/api/analytics` which returns database counts as structured JSON objects (aggregating labels and datasets). When the Administrator Dashboard loads, `static/js/main.js` makes a `fetch()` call to this endpoint, parses the JSON payload, and initializes Chart.js canvas elements.

### Q15: How did you implement persistent Dark Mode?
**Answer**: We toggle the `data-theme` attribute on the root HTML node (`<html>`) using vanilla JS. In our CSS, we use CSS variables (like `--bg-primary` and `--text-primary`) that change value based on the presence of `[data-theme="light"]`. The choice is saved in `localStorage` so the user's preference is remembered across page reloads.

### Q16: How does Chart.js handle redrawing when the user toggles light/dark theme?
**Answer**: Since the canvas charts require custom fonts and grid colors corresponding to the dark or light theme, we save the active chart objects in an object wrapper `activeCharts`. When the theme toggle is clicked, `window.renderDashboardCharts()` is re-invoked, which calls `.destroy()` on the active chart instances and redraws them with the new font and line colors.
