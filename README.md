# Multi-Role Learning Management System (MRLMS)

A complete, production-ready, database-driven Multi-Role Learning Management System (MRLMS) designed for educational institutions. This application features dedicated panels for **Administrators**, **Faculty**, and **Students** with robust role-based access controls, interactive dashboard analytics, and learning features. 

Developed as a showcase B.Tech Mini Project, placement portfolio, and GitHub showcase.

---

## 🌟 Key Features

### 🔑 Authentication & Security
- **Role-Based Access Control (RBAC)**: Custom routing decorators preventing cross-panel access.
- **Session Management**: Persistent sessions using `Flask-Login` with secure "Remember Me" functionality.
- **Cryptographic Protections**: Password hashing using Werkzeug security (`PBKDF2:SHA256`).
- **File Validation**: Renaming and filtering uploaded files by extension (`pdf`, `docx`, `ppt`, `png`, `jpg`) to prevent exploits.

### 👑 Administrator Dashboard
- **Curriculum Management**: Create courses and dynamically assign/change course instructors.
- **Member Management**: Complete CRUD operations for Students and Faculty registries.
- **Broadcast System**: Publish and remove global bulletin board announcements.
- **Academic Reporting**: Overview tables for attendance ratings, assignment submit statistics, and average quiz marks.
- **Institutional Analytics**: Complete suite of 8 interactive Chart.js graphs mapping academic trends.

### 🎓 Faculty Learning Room
- **Course Administration**: Upload lecture notes, slides, and syllabus files.
- **Attendance Registry**: Record daily student attendance statuses (Present/Absent).
- **Homework Manager**: Set up assignments with specific due dates, view submissions, download student work files, and grade submissions.
- **Online Tests**: Create multiple-choice quizzes, add question sets, and view attempt histories.

### 👨‍🎓 Student Learning Desk
- **Course Portal**: View enrolled courses, download learning resources, and monitor grades.
- **File Submission**: Upload coursework documents directly matching faculty deadlines.
- **Interactive Quizzes**: Attempt quizzes in real-time with instant auto-evaluation and score recording.
- **Attendance Tracker**: Visual progress bars monitoring minimum criteria (75%) and detailed session logs.

---

## 📊 Analytics Dashboard (Chart.js Charts)
The Administrator Dashboard includes 8 distinct analytical charts:
1. **Student Enrollment Trends**: Annual/Year-wise enrollment metrics.
2. **Attendance Trends**: Average attendance distribution across courses.
3. **Assignment Submission Rates**: Completed vs pending homework.
4. **Quiz Performance Analysis**: Average scoring rate per quiz.
5. **Course Popularity Analysis**: Subject enrollment counts.
6. **Student Performance Analysis**: Score distribution classifications.
7. **Department-wise Analytics**: Student counts per academic department.
8. **Faculty Performance Analytics**: Number of classes assigned per lecturer.

---

## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js, Bootstrap Icons
- **Backend**: Python Flask, Flask Blueprints, Flask-Login, Flask-SQLAlchemy
- **Database**: MySQL (Production) / SQLite (Development Fallback)

---

## 📂 Project Structure
```
MRLMS/
│
├── app.py                  # Main Application Driver & Mock Seeding
├── config.py               # SQLite & MySQL Configurations
├── requirements.txt        # Backend Python Packages
├── database.sql            # MySQL Schema DDL & Seed Inserts
│
├── models/                 # SQLAlchemy Database Models
│   ├── __init__.py         # Imports db and binds metadata
│   ├── db.py               # Shared SQLAlchemy instance (fixes circular imports)
│   ├── user.py             # User authentication model
│   ├── student.py          # Student roll-number and profile
│   ├── faculty.py          # Faculty designation and details
│   ├── course.py           # Courses, Enrollments, and Study Materials
│   ├── attendance.py       # Present/Absent records
│   ├── assignment.py       # Homework titles and submissions
│   ├── quiz.py             # MCQs and Quiz result models
│   └── announcement.py     # Global bulletins board
│
├── routes/                 # Flask Blueprints & Role Routing
│   ├── __init__.py
│   ├── auth.py             # Login, logout, and registration
│   ├── admin.py            # Administrative CRUD & JSON Chart APIs
│   ├── faculty.py          # Lecture, attendance, and quiz creator
│   └── student.py          # Download materials, submit homework, take tests
│
├── static/                 # Static Assets
│   ├── css/
│   │   └── styles.css      # Glassmorphism, Dark Theme, and animations
│   ├── js/
│   │   └── main.js        # Theme toggles & Chart.js renderer
│   └── uploads/            # Submissions & materials uploads folder
│
├── templates/              # Jinja2 HTML Templates
│   ├── base.html           # Universal shell (sidebar, navbar, themes)
│   ├── login.html          # Authentication logins screen
│   ├── register.html       # Student self-registration form
│   ├── admin/              # Admin pages (dashboard, registry, reports)
│   ├── faculty/            # Faculty pages (materials, attendance, grading)
│   └── student/            # Student pages (materials download, quiz attempt, grades)
│
└── docs/                   # Complete Academic Project Documentation
    ├── diagrams.md         # Mermaid Diagrams (ERD, Use Case, DFD, Sequence)
    ├── project_report.md   # 30+ Pages Mini Project Report Doc
    ├── ppt_content.md      # 15 Slides presentation deck outline
    ├── viva_questions.md   # 25+ Viva Q&A prep sheets
    ├── resume_description.md# Resume bullets and keywords
    └── deployment_guide.md # Multi-environment installation guide
```

---

## 🚀 Quick Setup (SQLite)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MRLMS
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```
   *Note: On first startup, the application automatically builds database tables under `mrlms.db` and populates them with rich, interactive mock data.*

4. **Access the portal**:
   Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 🔒 Default Logins (Seed Credentials)
All passwords correspond to **`password123`**:
- **Admin**: `admin@mrlms.edu`
- **Faculty 1**: `sarah.jenkins@mrlms.edu`
- **Faculty 2**: `alan.turing@mrlms.edu`
- **Student 1**: `jane.doe@student.mrlms.edu`
- **Student 2**: `john.smith@student.mrlms.edu`
- **Student 3**: `bob.johnson@student.mrlms.edu`
