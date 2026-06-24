# MRLMS System Diagrams

This document contains Mermaid-based system diagrams for the Multi-Role Learning Management System. These diagrams render dynamically in markdown viewers that support Mermaid syntax.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o| students : "has student profile"
    users ||--o| faculty : "has faculty profile"
    users ||--o| announcements : "author"
    
    faculty ||--o{ courses : "teaches"
    
    students ||--o{ enrollments : "registers"
    courses ||--o{ enrollments : "has enrolled"
    
    courses ||--o{ study_materials : "contains"
    
    courses ||--o{ assignments : "allocates"
    students ||--o{ assignment_submissions : "submits"
    assignments ||--o{ assignment_submissions : "has submissions"
    
    students ||--o{ attendance : "marked for"
    courses ||--o{ attendance : "logs attendance"
    
    courses ||--o{ quizzes : "conducts"
    quizzes ||--o{ quiz_questions : "contains"
    
    students ||--o{ quiz_results : "obtains"
    quizzes ||--o{ quiz_results : "records marks"

    users {
        int user_id PK
        string full_name
        string email
        string password
        enum role
    }

    students {
        int student_id PK
        int user_id FK
        string roll_number UK
        string department
        int year
        string section
    }

    faculty {
        int faculty_id PK
        int user_id FK
        string department
        string designation
    }

    courses {
        int course_id PK
        string course_name
        text description
        int faculty_id FK
    }

    enrollments {
        int enrollment_id PK
        int student_id FK
        int course_id FK
    }

    study_materials {
        int material_id PK
        int course_id FK
        string title
        string file_path
        timestamp upload_date
    }

    assignments {
        int assignment_id PK
        int course_id FK
        string title
        text description
        datetime due_date
    }

    assignment_submissions {
        int submission_id PK
        int assignment_id FK
        int student_id FK
        string file_path
        int marks
        timestamp submitted_at
    }

    attendance {
        int attendance_id PK
        int student_id FK
        int course_id FK
        date attendance_date
        enum status
    }

    quizzes {
        int quiz_id PK
        int course_id FK
        string title
        int total_marks
    }

    quiz_questions {
        int question_id PK
        int quiz_id FK
        text question
        string option_a
        string option_b
        string option_c
        string option_d
        char correct_answer
    }

    quiz_results {
        int result_id PK
        int quiz_id FK
        int student_id FK
        int marks
        timestamp submitted_at
    }

    announcements {
        int announcement_id PK
        string title
        text message
        timestamp created_at
    }
```

---

## 2. Use Case Diagram

```mermaid
graph TD
    subgraph Users
        Admin[Administrator]
        Fac[Faculty Staff]
        Stud[Student]
    end

    subgraph MRLMS Use Cases
        UC1(Login & Session Management)
        UC2(Manage Student Registry)
        UC3(Manage Faculty Registry)
        UC4(Create & Assign Courses)
        UC5(Broadcast Announcements)
        UC6(View Analytics Dashboard)
        UC7(Upload Study Materials)
        UC8(Mark Daily Attendance)
        UC9(Create Assignments & Grade Submissions)
        UC10(Create MCQs Quizzes)
        UC11(Download Study Materials)
        UC12(Submit Homework Assignments)
        UC13(Attempt Interactive Quizzes)
        UC14(View Personal Attendance & Marks)
    end

    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6

    Fac --> UC1
    Fac --> UC7
    Fac --> UC8
    Fac --> UC9
    Fac --> UC10
    Fac --> UC5

    Stud --> UC1
    Stud --> UC11
    Stud --> UC12
    Stud --> UC13
    Stud --> UC14
```

---

## 3. System Architecture Diagram

```mermaid
graph TD
    subgraph Presentation Layer (Client Side)
        UI[Web Browser - HTML5/CSS3/Bootstrap 5]
        Chart[Chart.js Rendering Engine]
    end

    subgraph Application Layer (Flask Backend)
        Blueprint[Flask Blueprints]
        Auth[Authentication & Flask-Login Manager]
        ORM[SQLAlchemy ORM Mapping]
        RouteAdmin[Admin routes CRUD]
        RouteFac[Faculty routes grading/upload]
        RouteStud[Student routes homework/quiz]
    end

    subgraph Data Layer (Database)
        MySQL[(MySQL Production DB)]
        SQLite[(SQLite Development DB)]
    end

    UI --> Blueprint
    Chart --> RouteAdmin
    Blueprint --> Auth
    Auth --> ORM
    RouteAdmin --> ORM
    RouteFac --> ORM
    RouteStud --> ORM
    ORM --> MySQL
    ORM --> SQLite
```

---

## 4. Data Flow Diagram (DFD)

### Level 0: Context DFD
```mermaid
graph LR
    Student[Student User] -->|Attempts quiz, submits homework| MRLMS((MRLMS Core System))
    Faculty[Faculty User] -->|Uploads materials, grades homework, marks attendance| MRLMS
    Admin[Administrator] -->|Manages students, faculty, courses, announcements| MRLMS
    
    MRLMS -->|Delivers study resources, quiz grades, logs| Student
    MRLMS -->|Displays course listings, grading dashboards| Faculty
    MRLMS -->|Displays institutional report statistics & analytics| Admin
```

### Level 1: Functional DFD
```mermaid
graph TD
    S[Student] -->|Login credentials| P1[1.0 Authentication & Session]
    F[Faculty] -->|Login credentials| P1
    A[Admin] -->|Login credentials| P1

    P1 -->|Query / Verify| D1[(Users Store)]
    D1 -->|Active session context| P1

    A -->|Manage profiles| P2[2.0 Admin Management Panel]
    P2 -->|CRUD writes| D2[(Students & Faculty Stores)]
    P2 -->|Write course assignments| D3[(Courses Store)]

    F -->|Record status| P3[3.0 Faculty Classroom Operations]
    P3 -->|Upload lecture slides| D4[(Materials Store)]
    P3 -->|Log daily present lists| D5[(Attendance Store)]
    P3 -->|Write quiz question banks| D6[(Quizzes Store)]

    S -->|Download notes| P4[4.0 Student Learning Desk]
    D4 -->|Serve files| P4
    S -->|Submit assignments| P4
    P4 -->|Write files/links| D7[(Submissions Store)]
    S -->|Submit MCQ answers| P4
    P4 -->|Check keys & log score| D8[(Quiz Results Store)]

    P3 -->|Access homework files & grade| D7
```

---

## 5. Sequence Diagram: Student Quiz Attempt & Auto-Evaluation

```mermaid
sequenceDiagram
    actor Student
    participant UI as Web Browser (Student Dashboard)
    participant Route as Flask Router (student_bp)
    participant DB as SQLite / MySQL Database
    participant Eval as Grading Core (Auto-Evaluation)

    Student->>UI: Clicks "Attempt Quiz"
    UI->>Route: GET /student/quizzes/attempt/<quiz_id>
    Route->>DB: Query enrollment & attempt status
    DB-->>Route: Enrolled = True, Attempted = False
    Route->>DB: Query quiz questions & options
    DB-->>Route: Return Question sets
    Route-->>UI: Render quiz_attempt.html MCQ Form
    Student->>UI: Ticks options & clicks "Submit"
    UI->>Route: POST /student/quizzes/attempt/<quiz_id> (answers form)
    Route->>Eval: Execute auto-evaluation checklist
    loop For each question
        Eval->>Eval: Match selected option with correct_answer
    end
    Eval->>Route: Return scaled marks score
    Route->>DB: INSERT into quiz_results (marks, timestamp)
    DB-->>Route: Transaction commit success
    Route-->>UI: Redirect with Flash success msg
    UI-->>Student: Display scored marks (e.g. 8/10)
```
