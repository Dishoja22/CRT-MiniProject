# Resume Project Description: MRLMS

This document provides ready-to-use project descriptions, bullet points, and key technical phrases for student resumes, LinkedIn profiles, and placement portfolios.

---

## 🛠️ Tech Stack Keywords
**Languages**: Python, SQL, JavaScript, HTML5, CSS3  
**Frameworks & Libraries**: Flask, Bootstrap 5, Chart.js, SQLAlchemy ORM, Werkzeug  
**Database**: MySQL, SQLite  
**Developer Tools**: Git, Visual Studio Code, Postman  

---

## 📝 Option 1: Detailed Resume Section (Recommended)

### **Multi-Role Learning Management System (MRLMS)** | Python, Flask, MySQL, Bootstrap 5, Chart.js
- Developed a complete database-driven Learning Management System featuring dedicated dashboards for Administrators, Faculty, and Students to manage academic workflows.
- Implemented **Role-Based Access Control (RBAC)** using custom Python decorators and **Flask-Login** session management to isolate panel accesses.
- Engineered an automated grading core for multiple-choice quizzes, scoring responses in real-time and updating student grade books instantly.
- Built a secure file validation pipeline checking file size, whitelisting extensions (`pdf`, `docx`, `ppt`, `images`), and sanitizing filenames using **Werkzeug Security** to prevent Arbitrary Code Execution (RCE) and path traversal attacks.
- Configured a flexible database layer using **Flask-SQLAlchemy ORM**, supporting local SQLite instances for development and migrating to MySQL schemas via PyMySQL connection strings.
- Designed 8 interactive reporting charts using **Chart.js** mapped to RESTful JSON APIs, displaying institutional trends in enrollment, session attendance, and academic performances.
- Integrated persistent **Dark Mode** using CSS variables and HTML custom data attributes, saving user preferences using HTML5 local storage API.

---

## 📝 Option 2: Short Resume Section (Single Column Layouts)

### **Multi-Role Learning Management System (MRLMS)** *(Python, Flask, MySQL, Bootstrap 5, Chart.js)*
- Engineered a web-based portal facilitating role-based panel operations (Admin/Faculty/Student) using Flask Blueprints and SQLAlchemy.
- Secured user endpoints using Werkzeug PBKDF2 password hashing, secure file whitelisting validation, and custom RBAC route interceptors.
- Designed 8 responsive analytical dashboards using Chart.js displaying real-time metrics on attendance shortage, course enrollments, and quiz distributions.
- Integrated coursework upload managers, attendance registries, and MCQs test modules supporting automated grade book scoring.

---

## 🚀 Key Achievements to Mention in Interviews
- **Circular Dependency Resolution**: Explain how you separated the SQLAlchemy database object into `models/db.py` to decouple metadata declarations and fix circular dependencies.
- **RESTful Architecture**: Mention that the charts are not hardcoded; they query a custom REST API endpoint (`/admin/api/analytics`) that yields database aggregations as clean JSON payloads.
- **Dynamic Database Support**: Emphasize that the system detects environment flags and switches between local file-backed SQLite database (perfect for quick local demos) and enterprise-grade MySQL database servers.
- **Security-First Approach**: Highlight details like parameterized ORM transactions preventing SQL injection, Jinja2 auto-escaping neutralizing XSS vectors, and custom routing wrappers stopping panel bypasses.
