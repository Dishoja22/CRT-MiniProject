# B.Tech Mini-Project Report: MRLMS

---

## 📄 CERTIFICATE

This is to certify that the project report entitled **"Multi-Role Learning Management System (MRLMS)"** is a bona fide work carried out by **[Student Name]** in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science & Engineering** during the academic year 2026.

**Project Guide:**  
[Faculty Name / Designation]  

---

## 📝 ABSTRACT

The rapid digitization of academic institutions has created a critical need for centralized, secure, and intuitive platforms to coordinate learning workflows. The **Multi-Role Learning Management System (MRLMS)** is a web-based educational portal built to address this need by providing role-segregated panels for **Administrators**, **Faculty**, and **Students**. 

Developed using **Python Flask** for backend orchestration, **MySQL** for relational persistence, and **Bootstrap 5** for interactive visual templates, the system automates core academic tasks. Administrators manage student/faculty registries, construct course mappings, and audit reports. Faculty take session-based attendance, upload course slides, evaluate homework, and configure online tests. Students access materials, submit assignments, attempt quizzes with real-time scoring, and track attendance levels. 

Security features like **Role-Based Access Control (RBAC)** wrappers, password hashing, file upload format whitelisting, and output escaping are implemented to mitigate common vulnerabilities. Real-time visual analysis is generated on the administrator panel through 8 dynamic charts using **Chart.js** connected to RESTful JSON APIs. 

---

## 🤝 ACKNOWLEDGEMENTS

I express my deep gratitude to our project guide, **[Faculty Name]**, for their continuous encouragement and invaluable guidance throughout this work. 

I also thank the Head of the Department, Computer Science & Engineering, and the institution's leadership for providing the infrastructure and resources necessary to successfully complete this project.

---

## 🗂️ TABLE OF CONTENTS
1. [Chapter 1: Introduction](#chapter-1-introduction)
2. [Chapter 2: Literature Survey & System Analysis](#chapter-2-literature-survey--system-analysis)
3. [Chapter 3: System Requirement Specifications (SRS)](#chapter-3-system-requirement-specifications-srs)
4. [Chapter 4: System Design & UML Modeling](#chapter-4-system-design--uml-modeling)
5. [Chapter 5: Implementation & Code Highlights](#chapter-5-implementation--code-highlights)
6. [Chapter 6: Testing & Experimental Results](#chapter-6-testing--experimental-results)
7. [Chapter 7: Conclusion & Future Scope](#chapter-7-conclusion--future-scope)
8. [References](#references)

---

## Chapter 1: Introduction

### 1.1 Overview
An educational Learning Management System (LMS) acts as the backbone of institutional communications. By digitizing documents, attendance sheets, and quizzes, systems reduce paper trails and enhance efficiency. However, many legacy platforms lack clean role definitions or expose databases to vulnerabilities. MRLMS introduces a secure MVC-modeled educational portal with granular user roles.

### 1.2 Project Objectives
- Create a multi-role workspace (Admin, Faculty, Student) with secure panel isolation.
- Enforce cryptographic protection for passwords and uploaded files.
- Enable automatic evaluation for MCQ quizzes to streamline grading.
- Integrate Chart.js interactive dashboards mapping student and faculty metrics.
- Support both local SQLite development databases and production MySQL/PostgreSQL stores.

### 1.3 Project Scope
The system handles user enrollment, course registry, study materials sharing, session roll call, homework assignments, online tests, and dashboard analytics. It is designed for medium-sized departments or colleges and runs efficiently on cloud architectures or local staging servers.

---

## Chapter 2: Literature Survey & System Analysis

### 2.1 Existing Systems vs Proposed System

#### Existing Systems (e.g. Traditional portals, paper registries)
- **Manual Attendance**: Prone to recording errors and hard to audit.
- **Scattered Sharing**: Files shared on chat apps lack organization and search controls.
- **Manual Exam Evaluation**: Grading multiple quizzes manually is time-consuming for staff.
- **Security Deficiencies**: Lack of input checks makes systems vulnerable to SQL injection and unauthorized access.

#### Proposed System (MRLMS)
- **Automated Calculations**: Calculates attendance percentages and grade point metrics instantly.
- **Role Isolation**: Restricts views by user type, blocking students from staff panels.
- **Auto-Grading Core**: Grades student quizzes immediately on submission and records scores.
- **Built-in Security**: Parameterized queries, CSRF controls, and strict file validation protect the system.

### 2.2 Feasibility Study
- **Technical Feasibility**: Python Flask and SQL (MySQL/SQLite) are mature, well-documented technologies.
- **Economic Feasibility**: The open-source stack has zero licensing costs.
- **Operational Feasibility**: The responsive Bootstrap 5 interface requires no training for students or faculty.

---

## Chapter 3: System Requirement Specifications (SRS)

### 3.1 Hardware Requirements
- **Server**: CPU Dual Core 2.0 GHz+, 4GB RAM+, 20GB Storage+
- **Client**: Any device with a modern web browser.

### 3.2 Software Requirements
- **Operating System**: Windows / Linux / macOS
- **Development Language**: Python 3.9+
- **Frameworks**: Flask 3.0.0, Bootstrap 5.3.0
- **Database**: SQLite (Development), MySQL 8.0+ / Supabase PostgreSQL (Production)

### 3.3 Functional Requirements
1. **User Authentication**: Secure registration, login, session retention, and logout.
2. **Admin Operations**: Create, update, and delete courses, students, and faculty.
3. **Faculty Workspace**: Mark daily attendance, upload course files, grade assignments, and create quizzes.
4. **Student Desktop**: Access materials, upload homework, take quizzes, and track attendance levels.
5. **Notice Board**: Post and remove announcements.
6. **Analytics Engine**: Render 8 charts tracking student and institutional performance.

---

## Chapter 4: System Design & UML Modeling

*(Note: Visual UML flow diagrams are specified in [diagrams.md](file:///c:/Users/ASUS/OneDrive/Desktop/CRT/docs/diagrams.md))*

### 4.1 Database Table Mappings
The database schema consists of the following tables:
- **`users`**: Central credentials.
- **`students`**: Personal details mapped 1-to-1 to users.
- **`faculty`**: Designations and departments mapped 1-to-1 to users.
- **`courses`**: Course registry assigned to faculty.
- **`enrollments`**: Mappings linking students to courses.
- **`study_materials`**: Syllabus files and lecture notes.
- **`assignments`**: Project tasks and due dates.
- **`assignment_submissions`**: Uploaded student files and grades.
- **`attendance`**: Daily present/absent logs.
- **`quizzes`**: Online test definitions.
- **`quiz_questions`**: Quiz questions and options.
- **`quiz_results`**: Completed scores.
- **`announcements`**: System bulletins.

---

## Chapter 5: Implementation & Code Highlights

### 5.1 Decoupling Database to Avoid Circular Imports
To prevent circular imports, we isolated the SQLAlchemy instance inside `models/db.py`:

```python
# File: models/db.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

Each model file imports `db` from this module instead of the main packages:

```python
# File: models/user.py
from models.db import db
class User(db.Model):
    ...
```

### 5.2 Role Restriction Wrappers
We built a custom decorator to secure routes based on user roles:

```python
# File: routes/auth.py
def role_required(roles):
    if isinstance(roles, str):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash("Unauthorized access attempt.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## Chapter 6: Testing & Experimental Results

### 6.1 Testing Table Summary
- **Authentication**: Verified that incorrect credentials and duplicate registrations are rejected.
- **Access Control**: Checked that students are blocked from administrative paths.
- **File Validation**: Confirmed that files over 16MB or with non-whitelisted extensions are blocked.
- **Quiz Grading**: Verified that student answers are scored correctly and scores are stored in `quiz_results`.

---

## Chapter 7: Conclusion & Future Scope

### 7.1 Conclusion
The MRLMS portal successfully automates academic management for institutions. Combining Python Flask, Bootstrap 5, and SQLAlchemy ORM creates a responsive application. Decoupled configurations make the system easy to scale from development (SQLite) to production (MySQL or Supabase PostgreSQL).

### 7.2 Future Scope
- **Online Meetings**: Integrate virtual classroom meetings (e.g. Zoom API).
- **Plagiarism Checks**: Add text comparison checks for assignment submissions.
- **AI Tutoring**: Integrate chat widgets to answer student questions based on course materials.

---

## References
1. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.
2. MySQL Reference Manual. Database schema design guidelines.
3. Chart.js Documentation. Dynamic client-side visualization.
4. Bootstrap 5 Components guide.
