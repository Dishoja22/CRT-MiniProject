-- Multi-Role Learning Management System (MRLMS) Database Schema
-- Compatible with MySQL 8.0+

CREATE DATABASE IF NOT EXISTS mrlms_db;
USE mrlms_db;

-- --------------------------------------------------------
-- Table: Users
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Student') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Students
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    section VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Faculty
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Courses
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    description TEXT,
    faculty_id INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Enrollments
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: StudyMaterials
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS study_materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Assignments
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    due_date DATETIME NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: AssignmentSubmissions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS assignment_submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    marks INT DEFAULT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_submission (assignment_id, student_id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Attendance
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    UNIQUE KEY unique_attendance (student_id, course_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Quizzes
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    total_marks INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: QuizQuestions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: QuizResults
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,
    marks INT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_result (quiz_id, student_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table: Announcements
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ========================================================
-- SAMPLE SEED DATA
-- Note: Password hashes correspond to 'password123' using Werkzeug PBKDF2 method.
-- ========================================================

-- Insert Users
INSERT INTO users (user_id, full_name, email, password, role) VALUES
(1, 'System Administrator', 'admin@mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Admin'),
(2, 'Dr. Sarah Jenkins', 'sarah.jenkins@mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Faculty'),
(3, 'Prof. Alan Turing', 'alan.turing@mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Faculty'),
(4, 'Jane Doe', 'jane.doe@student.mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Student'),
(5, 'John Smith', 'john.smith@student.mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Student'),
(6, 'Bob Johnson', 'bob.johnson@student.mrlms.edu', 'pbkdf2:sha256:600000$aTfH4w8Z$fb6b28a8d116239fe240ee4286134fb3e33e8a3b5b6cf793a3886f4a8b7593c6', 'Student');

-- Insert Faculty details
INSERT INTO faculty (faculty_id, user_id, department, designation) VALUES
(1, 2, 'Computer Science', 'Associate Professor'),
(2, 3, 'Information Technology', 'Professor & Head');

-- Insert Student details
INSERT INTO students (student_id, user_id, roll_number, department, year, section) VALUES
(1, 4, 'CS2023001', 'Computer Science', 3, 'A'),
(2, 5, 'CS2023002', 'Computer Science', 3, 'A'),
(3, 6, 'IT2023001', 'Information Technology', 3, 'B');

-- Insert Courses
INSERT INTO courses (course_id, course_name, description, faculty_id) VALUES
(1, 'Database Management Systems (DBMS)', 'Core course on relational databases, SQL, normalization, and indexing principles.', 1),
(2, 'Design and Analysis of Algorithms', 'Core algorithms course covering greedy method, divide & conquer, and dynamic programming.', 2),
(3, 'Web Development Technologies', 'Advanced concepts of full-stack development, frameworks, and APIs.', 1);

-- Insert Enrollments
INSERT INTO enrollments (student_id, course_id) VALUES
(1, 1), -- Jane in DBMS
(1, 3), -- Jane in Web Dev
(2, 1), -- John in DBMS
(2, 2), -- John in Algorithms
(3, 2), -- Bob in Algorithms
(3, 3); -- Bob in Web Dev

-- Insert Study Materials
INSERT INTO study_materials (material_id, course_id, title, file_path, upload_date) VALUES
(1, 1, 'Introduction to SQL', 'intro_to_sql.pdf', NOW()),
(2, 1, 'ER Diagram Tutorial', 'er_tutorial.pdf', NOW()),
(3, 2, 'Dynamic Programming notes', 'dp_notes.pdf', NOW());

-- Insert Assignments
INSERT INTO assignments (assignment_id, course_id, title, description, due_date) VALUES
(1, 1, 'SQL Joins & Subqueries', 'Write SQL queries using JOIN and Nested Queries. Submit PDF.', '2026-07-10 23:59:59'),
(2, 2, 'Dynamic Programming Knapsack', 'Implement 0/1 Knapsack solution and analyze time complexity.', '2026-07-15 23:59:59');

-- Insert Submissions
INSERT INTO assignment_submissions (submission_id, assignment_id, student_id, file_path, marks, submitted_at) VALUES
(1, 1, 1, 'sub_jane_sql.pdf', 90, NOW()),
(2, 1, 2, 'sub_john_sql.pdf', NULL, NOW()); -- Pending grading

-- Insert Attendance
INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES
(1, 1, '2026-06-20', 'Present'),
(1, 1, '2026-06-21', 'Present'),
(1, 1, '2026-06-22', 'Absent'),
(2, 1, '2026-06-20', 'Present'),
(2, 1, '2026-06-21', 'Present'),
(2, 1, '2026-06-22', 'Present'),
(3, 2, '2026-06-22', 'Present');

-- Insert Quizzes
INSERT INTO quizzes (quiz_id, course_id, title, total_marks) VALUES
(1, 1, 'Relational Algebra Quiz', 10),
(2, 2, 'Asymptotic Notations', 10);

-- Insert Questions
INSERT INTO quiz_questions (question_id, quiz_id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES
(1, 1, 'Which operation is used to select tuples from a relation?', 'Projection', 'Selection', 'Join', 'Intersection', 'B'),
(2, 1, 'Which of the following is not a binary operation in Relational Algebra?', 'Project', 'Union', 'Set Difference', 'Cartesian Product', 'A'),
(3, 2, 'What is the time complexity of Quick Sort in the worst case?', 'O(N log N)', 'O(N)', 'O(N^2)', 'O(1)', 'C');

-- Insert Quiz Results
INSERT INTO quiz_results (result_id, quiz_id, student_id, marks, submitted_at) VALUES
(1, 1, 1, 10, NOW()),
(2, 1, 2, 5, NOW());

-- Insert Announcements
INSERT INTO announcements (announcement_id, title, message, created_at) VALUES
(1, 'Welcome to the New Academic Semester!', 'Welcome back students and faculty! Wishing you a very successful and productive semester ahead.', NOW()),
(2, 'End Semester Exam Schedule', 'The end semester examination dates have been announced. Please refer to the academic calendar for details.', NOW());
