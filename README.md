# 📚 Student Dashboard — Flask Web Application

The **Student Dashboard** is a web application built using **Flask** that allows students to create their personalized dashboards, make notes, share PDFs, and interact with other students' work. It’s a collaborative platform designed to help students stay organized, share resources, and track their progress.

### Key Features:
- **User Registration & Authentication**: Secure login/signup system for each student.
- **Personalized Dashboards**: Each student can have their own dashboard with an overview of their work.
- **PDF Uploads & Downloads**: Students can upload PDFs of their work, assignments, or notes, and others can download them.
- **Notes Section**: Each student can add and manage their own notes to keep track of assignments or class work.
- **Student Interaction**: Students can view and download resources shared by others.

---

## 🚀 Features

### 1. **Student Profiles and Dashboards**
- Students can create and update their profiles.
- Dashboard contains links to **Notes**, **Uploaded Files**, and a **To-Do List**.

### 2. **PDF Uploads**
- Upload any course-related PDFs (assignments, projects, notes).
- PDF uploads are categorized by subject or course, making it easy for students to find relevant resources.

### 3. **Notes Section**
- A section where students can make personal notes or class notes.
- Notes are private by default but can be shared with others if desired.

### 4. **File Sharing and Download**
- Students can view and download files uploaded by other students.
- Files are shared in a structured way with metadata like course name, subject, and description for easy access.

### 5. **Search & Filter**
- The app allows students to search for specific PDFs or notes by keywords, subject, or file type.

---

## 🧰 Tech Stack

| Layer      | Technology           |
|------------|----------------------|
| Backend    | Flask (Python)       |
| Frontend   | HTML, CSS, Bootstrap |
| Database   | SQLite or PostgreSQL |
| Authentication | Flask-Login for user sessions |
| File Handling | Flask-Uploads for file management |

---

## 📂 Project Structure

```plaintext
/Fileholder
│   ├── app.py               # Flask application
│   ├── Procfile              # API routes and logic (student profile, file upload, etc.)
│   └── templates/           # HTML templates (dashboard, login, notes, etc.)
│   └── static/              # CSS, JS, and other static assets
├── requirements.txt         # Python dependencies
└── README.md
```bash
clone https://github.com/yourusername/Fileholder.git
cd Fileholder

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt


