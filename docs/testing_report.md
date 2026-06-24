# Testing & Verification Report

This document records the testing strategy, unit test cases, integration scenarios, boundary checks, and system validations performed on the Multi-Role Learning Management System.

---

## 🎯 1. Testing Methodology

We adopted a hybrid testing strategy combining:
- **Unit Testing**: Testing models, password hashing operations, and blueprint endpoints.
- **Integration Testing**: Verifying role separation overrides (RBAC), multi-step quiz attempts, and homework uploads.
- **Security Testing**: Boundary tests for file sizes, whitelisted formats, and parameter sanity.

---

## 📋 2. Unit Testing Cases

| Test Case ID | Feature Under Test | Input Data / Trigger | Expected Output | Actual Outcome | Status |
|---|---|---|---|---|---|
| **TC-AUTH-01** | Student Self-Registration | Full Name, email, password, roll, department, section | Successful DB insert for both `users` and `students` tables. | As expected. Accounts created successfully. | **PASS** |
| **TC-AUTH-02** | User Registration Duplication | Email or Roll Number already in use | Fail registration, flash error, and redirect to sign up page. | As expected. Double register prevented. | **PASS** |
| **TC-AUTH-03** | Secure Password Hashing | Plain text `password123` | Password converted to secure `pbkdf2:sha256` string in database. | Hashed value stored. Plain password not visible. | **PASS** |
| **TC-AUTH-04** | Authentication Portal | Correct email & password | Set session token, load user, redirect to role-specific dashboard. | Successfully logged in and redirected. | **PASS** |
| **TC-AUTH-05** | Authentication Portal | Incorrect email/password combination | Reject entry, flash generic warning, redirect to login page. | Rejected access. Generic warning shown. | **PASS** |
| **TC-RBAC-01** | Role Panel Separation | Student tries to fetch `/admin/dashboard` | Intercept request, trigger decorator redirect, flash warning. | Blocked student access, redirected to student home. | **PASS** |
| **TC-FILE-01** | Secure File Upload | Submitting `.exe` or `.py` files | Intercept file check, reject upload, and show format list alert. | Blocked upload of incorrect formats. | **PASS** |
| **TC-FILE-02** | File Path Traversal | Filename `../../malicious.pdf` | `secure_filename()` strips traversals to yield `malicious.pdf`. | Clean path saved on server. | **PASS** |
| **TC-QUIZ-01** | Quiz Auto-Evaluation | Submitting MCQ choices | System logs, counts correct hits, saves scaled score to DB. | Graded instantly. Score saved. | **PASS** |
| **TC-QUIZ-02** | Quiz Retake Prevention | Attempting a completed quiz | Detect database entry in `quiz_results`, block attempt route. | Blocked. User score display shown instead. | **PASS** |

---

## ⚙️ 3. Integration Testing Scenarios

### Scenario A: Full Academic Cycle (Course, Quiz, Submissions)
1. **Admin** registers Faculty "Prof. Turing" and Course "Theory of Computation".
2. **Admin** assigns "Prof. Turing" to the course.
3. **Student** registers, logs in, and enters the course room.
4. **Faculty** uploads "Lecture 1 Notes.pdf".
5. **Student** downloads "Lecture 1 Notes.pdf" successfully.
6. **Faculty** launches "Turing Machine Quiz" worth 10 marks.
7. **Student** attempts the quiz, selects answers, and clicks Submit.
8. **System** auto-calculates score (e.g. 10/10) and locks student from retaking.

**Outcome**: **PASS** (Database state commits perfectly across blueprints).

### Scenario B: Role Access Violation Interception
1. Log in as a Student.
2. Manually enter the URL: `http://localhost:5000/admin/students` in the browser tab.
3. **System** triggers the `@role_required(['Admin'])` interceptor.
4. **Student** is redirected to `/student/dashboard` with a warning alert "You do not have permission to access this page."

**Outcome**: **PASS** (Panel isolation holds).

---

## 📐 4. Boundary Value Analysis (BVA)

### 1. Graded Marks Limits
- **Input**: `-5` marks, `105` marks, `95` marks on grading forms.
- **Behavior**: HTML5 numeric boundaries (`min="0" max="100"`) restrict entries. Python DB layers enforce integers.
- **Status**: **PASS**.

### 2. Large File Uploads
- **Input**: File of size `18.5 MB`.
- **Behavior**: Flask config `MAX_CONTENT_LENGTH = 16 * 1024 * 1024` triggers a `413 Request Entity Too Large` error, blocking server overload.
- **Status**: **PASS**.
