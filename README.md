# 🎓 ExamAlloc — Examination Hall Allocation System

An automated system that allocates students to examination halls and assigns optimal seating arrangements with zero same-subject adjacency conflicts.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Running the Application](#-running-the-application)
- [Default Login Credentials](#-default-login-credentials)
- [Using the Sample CSVs](#-using-the-sample-csvs)
- [CSV Format Reference](#-csv-format-reference)
- [How the Allocation Algorithm Works](#-how-the-allocation-algorithm-works)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- **Automated Hall Allocation** — System decides which student goes to which hall, maximizing subject mixing
- **Automated Seating** — 2D grid placement with zero same-subject adjacency (left, right, top, bottom)
- **Two Modes:**
  - **Hall + Seating Allocation** — Upload students CSV + halls CSV → system assigns halls AND seats
  - **Seating Only** — Upload pre-assigned CSV (students already have hall info) → system assigns seats within halls
- **Real-time Seating Visualization** — Color-coded interactive grid with tooltips
- **Cross-Hall Search** — Search any roll number, auto-navigates to correct hall and highlights the seat
- **Collision Detection** — Prevents double-booking halls or students on same date/time
- **PDF & CSV Export** — Vivid color-coded seating charts and allocation reports
- **Role-Based Access** — Admin, Faculty, Student portals with distinct dashboards
- **Invigilator Assignment** — Assign faculty to halls per exam session
- **Student Portal** — Students log in to view their seat assignments with highlighted hall maps

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Django 5.x, Django REST Framework |
| **Frontend** | React 18, Vite, Tailwind CSS, Radix UI, Framer Motion |
| **Database** | SQLite (zero config, included) |
| **PDF Generation** | ReportLab |
| **Icons** | Lucide React |
| **HTTP Client** | Axios |

---

## 📁 Project Structure

```
ExamAlloc/
├── backend/                  # Django backend
│   ├── exam_alloc/           # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── allocation/           # Main application
│   │   ├── models.py         # 9 database models
│   │   ├── views.py          # 25+ API views
│   │   ├── serializers.py    # DRF serializers
│   │   ├── validators.py     # CSV validation & parsing
│   │   ├── engine.py         # 3-phase allocation algorithm
│   │   ├── exporters.py      # PDF & CSV report generators
│   │   ├── permissions.py    # Role-based permissions
│   │   └── urls.py           # API URL routes
│   ├── manage.py
│   └── db.sqlite3            # Auto-created on first migrate
│
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── api/              # Axios client & endpoint functions
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/           # Radix-based primitives (Button, Badge, Dialog, etc.)
│   │   │   ├── SeatingGrid.jsx
│   │   │   ├── StatsCard.jsx
│   │   │   └── PageHeader.jsx
│   │   ├── context/          # AuthContext
│   │   ├── hooks/            # useAuth hook
│   │   ├── layouts/          # DashboardLayout + Sidebar
│   │   ├── pages/            # 8 page components
│   │   └── lib/              # Utility functions
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── csvs/                     # Sample CSV data files
│   ├── 1000_students_for_hall_and_seating_allocation.csv
│   ├── halls_mixed.csv
│   └── 1000_students_with_hall_pre_specified.csv
│
└── README.md
```

---

## 📦 Prerequisites

Make sure you have the following installed on your system:

| Tool | Version | Check Command |
|------|---------|--------------|
| **Python** | 3.10 or higher | `python3 --version` |
| **pip** | Latest | `pip --version` |
| **Node.js** | 18 or higher | `node --version` |
| **npm** | 9 or higher | `npm --version` |
| **Git** | Any | `git --version` |

### Installing Prerequisites (if not installed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git
```

**macOS (with Homebrew):**
```bash
brew install python3 node git
```

**Windows:**
- Python: Download from [python.org](https://www.python.org/downloads/) (check "Add to PATH")
- Node.js: Download from [nodejs.org](https://nodejs.org/) (LTS version)
- Git: Download from [git-scm.com](https://git-scm.com/)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/amansaikrishna/Exam-Allocation-System/tree/main
cd ExamAlloc
```

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python3 -m venv env

# Activate virtual environment
# Linux/macOS:
source env/bin/activate
# Windows (Command Prompt):
env\Scripts\activate
# Windows (PowerShell):
env\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations allocation
python manage.py migrate

# Create the admin superuser
python manage.py shell -c "
from allocation.models import User
from django.contrib.auth.hashers import make_password
if not User.objects.filter(username='admin').exists():
    User.objects.create(
        username='admin',
        password=make_password('admin123'),
        role='ADMIN',
        is_superuser=True,
        is_staff=True,
        first_name='Admin'
    )
    print('Admin user created.')
else:
    print('Admin user already exists.')
"
```

---

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# If you encounter peer dependency warnings, run:
npm install --legacy-peer-deps
```

---

## ▶️ Running the Application

You need **two terminals** running simultaneously:

### Terminal 1 — Backend (Django)

```bash
cd backend
source env/bin/activate        # Linux/macOS
# env\Scripts\activate         # Windows

python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

### Terminal 2 — Frontend (React)

```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

> **Open your browser and go to** → **http://localhost:3000**

---

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Students** | `<roll_number_lowercase>` | `<roll_number>@<first_4_chars_of_name>` |

Student accounts are **auto-created** after running an allocation. For example, if student roll number is `25001D5101` and name is `Aarav Sharma`:
- **Username:** `25001d5101`
- **Password:** `25001d5101@aara`

---

## 📊 Using the Sample CSVs

The `csvs/` folder contains three ready-to-use CSV files:

### Mode 1: Hall + Seating Allocation (Recommended)

Use when you want the system to **decide which hall each student goes to** AND assign seats.

| File | Purpose |
|------|---------|
| `1000_students_for_hall_and_seating_allocation.csv` | 1000 students with roll number, name, subject, class |
| `halls_mixed.csv` | Multiple halls with varying capacities and grid sizes |

**Steps:**
1. Login as **admin** → Go to **New Allocation**
2. Select mode: **Students + Halls** (separate CSVs)
3. Upload `1000_students_for_hall_and_seating_allocation.csv` as **Students CSV**
4. Upload `halls_mixed.csv` as **Halls CSV**
5. Click **Next** → Select/filter students → Click **Next**
6. Set exam date, time from, time to
7. Optionally assign invigilators to halls
8. Click **Allocate & Generate**
9. View the seating layout, export PDF/CSV

---

### Mode 2: Seating Only (Pre-assigned Halls)

Use when students are **already assigned to halls** and you only need the system to assign seats within each hall.

| File | Purpose |
|------|---------|
| `1000_students_with_hall_pre_specified.csv` | 1000 students with hall already specified in the CSV |

**Steps:**
1. Login as **admin** → Go to **New Allocation**
2. Select mode: **Combined CSV**
3. Upload `1000_students_with_hall_pre_specified.csv` as **Combined CSV**
4. Click **Next** → Select/filter students → Click **Next**
5. Set exam date, time from, time to
6. Click **Allocate & Generate**
7. View the seating layout, export PDF/CSV

---

## 📄 CSV Format Reference

### Students CSV (for Hall + Seating mode)

| Column | Required | Description |
|--------|----------|-------------|
| `student_id` | ✅ | Unique roll number (aliases: `roll_no`, `roll_number`) |
| `name` | ✅ | Student full name (aliases: `student_name`) |
| `subject_code` | ✅ | Subject code like CS101 (aliases: `subject`) |
| `class` | ❌ | Class/section like "1st Year CSE" (aliases: `student_class`) |

**Example:**
```csv
student_id,name,subject_code,class
25001D5101,Aarav Sharma,CS101,1st Year CSE
25001D4101,Aditi Patel,EC101,1st Year ECE
25001D5102,Rahul Kumar,CS101,1st Year CSE
```

### Halls CSV

| Column | Required | Description |
|--------|----------|-------------|
| `hall_id` | ✅ | Unique hall identifier (aliases: `hall`, `hall_name`) |
| `capacity` | ✅ | Maximum seats, integer > 0 (aliases: `cap`) |
| `rows` | ❌ | Grid rows (auto-calculated if omitted) |
| `columns` | ❌ | Grid columns (auto-calculated if omitted) |

**Example:**
```csv
hall_id,capacity,rows,columns
H001,50,5,10
H002,60,6,10
AUDITORIUM,200,20,10
```

### Combined CSV (for Seating Only mode)

Contains both student data and hall assignment in a single file. The system reads hall info from the data.

```csv
student_id,name,subject_code,class,hall_id,hall_capacity,hall_rows,hall_columns
25001D5101,Aarav Sharma,CS101,1st Year CSE,H001,50,5,10
25001D4101,Aditi Patel,EC101,1st Year ECE,H001,50,5,10
```

---

## 🧠 How the Allocation Algorithm Works

ExamAlloc uses a **3-Phase Greedy Algorithm with Constraint-Based Swapping**:

### Phase 1: Hall Allocation (Round-Robin)
- Groups students by subject
- Distributes students across halls evenly using round-robin
- For each student, picks the hall with the **least count** of that subject → maximizes mixing

### Phase 2: Subject Interleaving
- Within each hall, arranges students so subjects alternate:
  `[CSE, ECE, EEE, MECH, CSE, ECE, EEE, MECH, ...]`

### Phase 3: Constraint-Based Seating (Snake + Swap)
- Places students in a snake (boustrophedon) traversal pattern
- For each seat, checks 4 neighbors (left, right, top, bottom)
- If same-subject adjacency detected, searches ahead up to 100 positions for a better student
- Swaps and places → zero violations with 2+ subjects

**Performance:** 1000 students + 20 halls → under 500ms

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login |
| POST | `/api/auth/logout/` | Logout |
| GET | `/api/auth/me/` | Current user |
| POST | `/api/csv/upload/students/` | Upload students CSV |
| POST | `/api/csv/upload/halls/` | Upload halls CSV |
| POST | `/api/csv/upload/combined/` | Upload combined CSV |
| GET | `/api/csv/` | List all CSVs |
| POST | `/api/sessions/create/` | Create allocation |
| GET | `/api/sessions/` | List sessions |
| GET | `/api/sessions/{id}/` | Session detail |
| GET | `/api/sessions/{id}/hall-layout/{pk}/` | Hall 2D grid |
| GET | `/api/export/csv/{id}/` | Download CSV report |
| GET | `/api/export/pdf/{id}/` | Download PDF seating chart |
| GET | `/api/students/` | List students |
| GET | `/api/students/search/?q=` | Search student |
| GET | `/api/my-allocations/` | Student's own seats |
| GET | `/api/dashboard/` | Dashboard stats |

---

## 🔧 Troubleshooting

### Backend Issues

**`ModuleNotFoundError: No module named 'rest_framework'`**
```bash
cd backend
source env/bin/activate
pip install djangorestframework
```

**`ModuleNotFoundError: No module named 'reportlab'`**
```bash
pip install reportlab
```

**`ModuleNotFoundError: No module named 'corsheaders'`**
```bash
pip install django-cors-headers
```

**Port 8000 already in use:**
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
# Or use a different port
python manage.py runserver 8001
```

**Database errors after model changes:**
```bash
python manage.py makemigrations allocation
python manage.py migrate
```

---

### Frontend Issues

**`npm install` fails with peer dependency errors:**
```bash
npm install --legacy-peer-deps
```

**`npm run dev` shows "port 3000 in use":**
```bash
# Use a different port
npx vite --port 3001
```

**API calls return 403 Forbidden:**
- Make sure backend is running on port 8000
- Check that `vite.config.js` has the proxy configured:
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://127.0.0.1:8000'
  }
}
```

**Blank page after login:**
- Clear browser cache and localStorage
- Open DevTools console for errors
- Ensure backend is running and accessible

---

### General

**Reset everything from scratch:**
```bash
# Backend
cd backend
rm db.sqlite3
python manage.py makemigrations allocation
python manage.py migrate
# Re-create admin (run the shell command from Backend Setup above)

# Frontend
cd frontend
rm -rf node_modules
npm install
```

---

## 📝 License

This project was built for an academic hackathon.

---

<div align="center">
  <b>Built with ❤️ using Django + React</b>
</div>
