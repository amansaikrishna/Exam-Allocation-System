#!/usr/bin/env python3
"""
ExamAlloc — Technical Documentation Generator
"""

import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, HRFlowable,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'ExamAlloc_Technical_Documentation.pdf')


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='DocTitle', fontSize=28, leading=34, alignment=TA_CENTER,
        spaceAfter=6, textColor=colors.HexColor('#0d9488'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='DocSubtitle', fontSize=14, leading=18, alignment=TA_CENTER,
        spaceAfter=30, textColor=colors.HexColor('#64748b'), fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        name='H1', fontSize=22, leading=28, spaceBefore=24, spaceAfter=12,
        textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='H2', fontSize=16, leading=22, spaceBefore=18, spaceAfter=8,
        textColor=colors.HexColor('#0d9488'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='H3', fontSize=13, leading=18, spaceBefore=12, spaceAfter=6,
        textColor=colors.HexColor('#334155'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='Body', fontSize=10, leading=15, spaceAfter=6,
        textColor=colors.HexColor('#334155'), fontName='Helvetica', alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        name='CB', fontSize=8.5, leading=12, spaceAfter=4,
        textColor=colors.HexColor('#1e293b'), fontName='Courier',
        backColor=colors.HexColor('#f1f5f9'), borderWidth=0.5,
        borderColor=colors.HexColor('#e2e8f0'), borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        name='Caption', fontSize=9, leading=12, spaceBefore=4, spaceAfter=12,
        textColor=colors.HexColor('#94a3b8'), fontName='Helvetica-Oblique', alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='BulletBody', fontSize=10, leading=15, spaceAfter=3,
        textColor=colors.HexColor('#334155'), fontName='Helvetica',
        leftIndent=20, bulletIndent=10, bulletFontName='Helvetica', bulletFontSize=10,
    ))
    return styles


def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def divider():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=12, spaceBefore=8)


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), bulletColor=colors.HexColor('#0d9488')) for item in items],
        bulletType='bullet', bulletFontSize=8, leftIndent=20, bulletOffsetY=-1,
    )


# ═══════════════════════════════════════════════
# SECTIONS
# ═══════════════════════════════════════════════

def cover_page(el, S):
    el.append(Spacer(1, 120))
    el.append(Paragraph("ExamAlloc", S['DocTitle']))
    el.append(Paragraph("Examination Hall Allocation System", S['DocSubtitle']))
    el.append(Spacer(1, 20))
    el.append(divider())
    el.append(Spacer(1, 10))
    el.append(Paragraph("Technical Documentation", ParagraphStyle(
        'cover2', fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#334155'), fontName='Helvetica-Bold')))
    el.append(Spacer(1, 30))
    meta = [
        ['Version', '1.0.0'],
        ['Date', datetime.datetime.now().strftime('%d %B %Y')],
        ['Stack', 'Django REST Framework + React + Vite + Tailwind CSS'],
        ['Database', 'SQLite (PostgreSQL compatible)'],
        ['Python', '3.10+'],
        ['Node.js', '18+'],
    ]
    t = Table(meta, colWidths=[140, 300])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    el.append(t)
    el.append(PageBreak())


def section_toc(el, S):
    el.append(Paragraph("Table of Contents", S['H1']))
    el.append(Spacer(1, 8))
    for item in [
        "1. System Overview", "2. Architecture & Tech Stack", "3. Database Schema",
        "4. Allocation Algorithm — Detailed", "5. REST API Reference",
        "6. Frontend Architecture", "7. CSV Specifications",
        "8. Seating Constraint Logic", "9. Performance & Scalability",
        "10. Export System (PDF & CSV)", "11. Authentication & Authorization",
        "12. Edge Cases & Error Handling", "13. Deployment Guide", "14. Testing Strategy",
    ]:
        el.append(Paragraph(item, ParagraphStyle(
            'toci_' + item[:5], fontSize=11, leading=20, leftIndent=20, fontName='Helvetica',
            textColor=colors.HexColor('#334155'),
        )))
    el.append(PageBreak())


def section_overview(el, S):
    el.append(Paragraph("1. System Overview", S['H1']))
    el.append(divider())

    el.append(Paragraph("1.1 Purpose", S['H2']))
    el.append(Paragraph(
        "ExamAlloc is a web-based Examination Hall Allocation System that automates the assignment "
        "of students to examination halls and seats. It ensures zero seating conflicts, enforces "
        "subject separation constraints, and respects hall capacity limits.", S['Body']))

    el.append(Paragraph("1.2 Target Users", S['H2']))
    el.append(bullets([
        "<b>Examination Branch (Admin)</b> — Upload student/hall data, run allocations, export reports",
        "<b>Academic Coordinators / Faculty</b> — View assigned invigilation duties, hall layouts",
        "<b>Students</b> — View personal seat assignments, hall maps",
    ], S['BulletBody']))

    el.append(Paragraph("1.3 Core Features", S['H2']))
    el.append(bullets([
        "Dual CSV upload: separate Students + Halls CSVs (recommended) or combined CSV",
        "Automated hall allocation: system decides which student goes to which hall",
        "Automated seating: 2D grid placement with subject adjacency enforcement",
        "Real-time seating visualization with color-coded subjects and tooltips",
        "Cross-hall student search with auto-navigation and seat highlighting",
        "Collision detection: prevents double-booking halls or students on same date/time",
        "PDF seating charts with color-coded grids and CSV allocation reports",
        "Role-based access: Admin, Faculty, Student with distinct dashboards",
        "Invigilator assignment per hall per exam session",
        "Expandable student allocation history across multiple exam sessions",
        "Performance: 1000 students allocated + seated in under 1 second",
    ], S['BulletBody']))

    el.append(Paragraph("1.4 System Flow", S['H2']))
    flow = [
        ['Step', 'Actor', 'Action', 'System Response'],
        ['1', 'Admin', 'Upload Students CSV', 'Validate, parse, store StudentRecords'],
        ['2', 'Admin', 'Upload Halls CSV', 'Validate, parse, store HallEntries'],
        ['3', 'Admin', 'Select CSVs + filters + schedule', 'Display student count, hall capacity summary'],
        ['4', 'Admin', 'Click "Allocate & Generate"', 'Run 3-phase algorithm, save results'],
        ['5', 'Admin', 'View seating layout', 'Interactive 2D grid with search/filter'],
        ['6', 'Admin', 'Export PDF/CSV', 'Generate downloadable reports'],
        ['7', 'Faculty', 'View duties', 'See assigned halls and sessions'],
        ['8', 'Student', 'Login & view seat', 'See hall, row, column with highlighted grid'],
    ]
    el.append(make_table(flow[0], flow[1:], [35, 55, 170, 220]))
    el.append(PageBreak())


def section_architecture(el, S):
    el.append(Paragraph("2. Architecture & Tech Stack", S['H1']))
    el.append(divider())

    el.append(Paragraph("2.1 High-Level Architecture", S['H2']))
    arch = (
        "CLIENT (Browser): React 18 + Vite + Tailwind CSS + Radix UI\n"
        "  Pages: Dashboard, Allocation Wizard, Students, Student Portal\n"
        "  HTTP Client: Axios with CSRF interceptor\n"
        "         |\n"
        "         | REST API (JSON over HTTP)\n"
        "         |\n"
        "SERVER (Django 5.x + DRF):\n"
        "  Views: Auth, CSV Upload, Allocation Engine, Export (PDF/CSV)\n"
        "  ORM: Django Models + Serializers\n"
        "         |\n"
        "         | SQL\n"
        "         |\n"
        "DATABASE (SQLite / PostgreSQL):\n"
        "  Users, CSVUploads, StudentRecords, HallEntries,\n"
        "  AllocationSessions, Halls, SeatAllocations,\n"
        "  ConstraintViolations, HallInvigilators"
    )
    el.append(Paragraph(arch, S['CB']))

    el.append(Paragraph("2.2 Technology Justification", S['H2']))
    tech = [
        ['Technology', 'Role', 'Why Chosen'],
        ['Django 5.x + DRF', 'Backend API', 'Rapid development, ORM, built-in auth, session management'],
        ['React 18 + Vite', 'Frontend SPA', 'Component reuse, fast HMR, rich ecosystem'],
        ['Tailwind CSS', 'Styling', 'Utility-first, consistent design, no custom CSS files'],
        ['Radix UI', 'UI Primitives', 'Accessible dialog, tabs, tooltip, checkbox - unstyled'],
        ['Framer Motion', 'Animations', 'Smooth transitions for grid hover and page entry'],
        ['ReportLab', 'PDF Generation', 'Python-native, no external service dependency'],
        ['SQLite', 'Database', 'Zero config, sufficient for exam data volumes'],
        ['Axios', 'HTTP Client', 'Interceptors for CSRF tokens, FormData support'],
        ['Lucide React', 'Icons', 'Consistent icon set, tree-shakeable'],
    ]
    el.append(make_table(tech[0], tech[1:], [100, 90, 290]))

    el.append(Paragraph("2.3 Project Structure", S['H2']))
    structure = (
        "ExamAlloc/\n"
        "  backend/\n"
        "    exam_alloc/         - Django project settings\n"
        "    allocation/         - Main app\n"
        "      models.py         - 9 models\n"
        "      views.py          - 25+ API views\n"
        "      serializers.py    - 14 serializers\n"
        "      validators.py     - CSV parsers\n"
        "      engine.py         - 3-phase allocation algorithm\n"
        "      exporters.py      - PDF + CSV generators\n"
        "      permissions.py    - IsAdmin, IsAdminOrFaculty\n"
        "      urls.py           - 25+ URL routes\n"
        "  frontend/\n"
        "    src/\n"
        "      api/              - Axios client + endpoints\n"
        "      components/       - SeatingGrid, StatsCard, etc.\n"
        "        ui/             - Radix-based primitives\n"
        "      context/          - AuthContext\n"
        "      hooks/            - useAuth\n"
        "      layouts/          - DashboardLayout + Sidebar\n"
        "      pages/            - 8 page components\n"
        "      lib/              - cn() utility"
    )
    el.append(Paragraph(structure, S['CB']))
    el.append(PageBreak())


def section_database(el, S):
    el.append(Paragraph("3. Database Schema", S['H1']))
    el.append(divider())

    el.append(Paragraph("3.1 Entity-Relationship Summary", S['H2']))
    er = (
        "User (AbstractUser) -- CSVUpload (uploaded_by)\n"
        "                    -- AllocationSession (created_by)\n"
        "                    -- HallInvigilator (faculty)\n"
        "                    -- StudentRecord (user)\n\n"
        "CSVUpload -- StudentRecord (csv_upload, many)\n"
        "          -- HallEntry (csv_upload, many)\n\n"
        "AllocationSession -- Hall (session, many)\n"
        "                  -- SeatAllocation (session, many)\n"
        "                  -- ConstraintViolation (session, many)\n"
        "                  -- HallInvigilator (session, many)\n\n"
        "SeatAllocation -- StudentRecord (student)\n"
        "               -- Hall (hall)"
    )
    el.append(Paragraph(er, S['CB']))

    el.append(Paragraph("3.2 Model Details", S['H2']))

    models = [
        ("User", "Extended AbstractUser", [
            ['Field', 'Type', 'Description'],
            ['role', 'CharField(10)', "ADMIN | FACULTY | STUDENT"],
            ['phone', 'CharField(20)', 'Contact number'],
            ['department', 'CharField(100)', 'Department name'],
            ['bio', 'TextField', 'User biography'],
        ]),
        ("CSVUpload", "Tracks uploaded CSV files", [
            ['Field', 'Type', 'Description'],
            ['name', 'CharField(200)', 'Display name'],
            ['filename', 'CharField(300)', 'Original filename'],
            ['csv_type', 'CharField(10)', 'STUDENTS | HALLS | COMBINED'],
            ['uploaded_by', 'FK to User', 'Who uploaded'],
            ['created_at', 'DateTimeField', 'Upload timestamp'],
        ]),
        ("StudentRecord", "Individual student from CSV", [
            ['Field', 'Type', 'Description'],
            ['csv_upload', 'FK to CSVUpload', 'Source CSV'],
            ['student_id', 'CharField(50)', 'Unique roll number (indexed)'],
            ['name', 'CharField(200)', 'Student full name'],
            ['subject_code', 'CharField(50)', 'Subject code (indexed)'],
            ['student_class', 'CharField(50)', 'Class/year (indexed)'],
            ['user', 'FK to User (nullable)', 'Linked login account'],
        ]),
        ("HallEntry", "Hall data from CSV", [
            ['Field', 'Type', 'Description'],
            ['csv_upload', 'FK to CSVUpload', 'Source CSV'],
            ['hall_id', 'CharField(50)', 'Hall identifier'],
            ['capacity', 'PositiveIntegerField', 'Max seats (validated >= 1)'],
            ['rows', 'PositiveIntegerField', 'Grid rows (auto-calc if 0)'],
            ['columns', 'PositiveIntegerField', 'Grid cols (auto-calc if 0)'],
        ]),
        ("AllocationSession", "One exam allocation run", [
            ['Field', 'Type', 'Description'],
            ['name', 'CharField(200)', 'Session display name'],
            ['student_csv', 'FK to CSVUpload', 'Source student data'],
            ['hall_csv', 'FK to CSVUpload (null)', 'Source hall data'],
            ['status', 'CharField(20)', 'ALLOCATED | COMPLETED'],
            ['exam_date', 'DateField', 'Examination date'],
            ['exam_time_from/to', 'TimeField', 'Exam time window'],
            ['total_students', 'IntegerField', 'Input student count'],
            ['allocated_count', 'IntegerField', 'Successfully seated'],
            ['unallocated_count', 'IntegerField', 'Could not be seated'],
            ['allocation_time_ms', 'FloatField', 'Processing time (ms)'],
            ['warnings', 'JSONField', 'List of warnings'],
        ]),
        ("Hall", "Hall instance per session", [
            ['Field', 'Type', 'Description'],
            ['session', 'FK to AllocationSession', 'Parent session'],
            ['hall_id', 'CharField(50)', 'Hall identifier'],
            ['capacity/rows/columns', 'PositiveIntegerField', 'Grid dimensions'],
        ]),
        ("SeatAllocation", "One student-seat assignment", [
            ['Field', 'Type', 'Description'],
            ['session', 'FK to AllocationSession', 'Parent session'],
            ['student', 'FK to StudentRecord', 'Assigned student'],
            ['hall', 'FK to Hall', 'Assigned hall'],
            ['row', 'PositiveIntegerField', '0-indexed row'],
            ['column', 'PositiveIntegerField', '0-indexed column'],
        ]),
        ("ConstraintViolation", "Logged issues", [
            ['Field', 'Type', 'Description'],
            ['session', 'FK to AllocationSession', 'Parent session'],
            ['violation_type', 'CharField(30)', 'ADJACENT_SAME_SUBJECT | UNALLOCATED'],
            ['description', 'TextField', 'Human-readable message'],
            ['student_id_ref', 'CharField(50)', 'Affected student'],
            ['hall_id_ref', 'CharField(50)', 'Affected hall'],
        ]),
        ("HallInvigilator", "Faculty-hall assignment", [
            ['Field', 'Type', 'Description'],
            ['session', 'FK to AllocationSession', 'Parent session'],
            ['hall', 'FK to Hall', 'Assigned hall'],
            ['faculty', 'FK to User', 'Assigned faculty'],
        ]),
    ]

    for name, desc, fields in models:
        el.append(Paragraph(f"<b>{name}</b> - {desc}", S['H3']))
        el.append(make_table(fields[0], fields[1:], [120, 120, 240]))
        el.append(Spacer(1, 8))
    el.append(PageBreak())


def section_algorithm(el, S):
    el.append(Paragraph("4. Allocation Algorithm - Detailed", S['H1']))
    el.append(divider())

    el.append(Paragraph("4.1 Problem Statement", S['H2']))
    el.append(Paragraph(
        "Given N students (each with a subject code) and M halls (each with capacity, rows, columns), "
        "assign every student to a hall and a specific seat (row, column) such that:", S['Body']))
    el.append(bullets([
        "No hall exceeds its capacity",
        "No two adjacent seats (left, right, top, bottom) have the same subject",
        "Same-class students are spread apart within each hall",
        "Allocation completes in under 10 seconds for 1000 students",
    ], S['BulletBody']))

    el.append(Paragraph("4.2 Three-Phase Greedy Algorithm", S['H2']))
    algo = (
        "PHASE 1: Hall Allocation (Round-Robin Subject Distribution)\n"
        "  Input:  N students grouped by subject\n"
        "  Output: Each student assigned to a specific hall\n"
        "  Method: For each student, pick hall with LEAST of that subject\n"
        "  Time:   O(S x H) where S=students, H=halls\n\n"
        "PHASE 2: Subject Interleaving (per Hall)\n"
        "  Input:  Students assigned to this hall\n"
        "  Output: Ordered queue for grid placement\n"
        "  Method: Round-robin across subjects, spread same-class\n"
        "  Result: [CSE, ECE, EEE, MECH, CSE, ECE, ...]\n\n"
        "PHASE 3: Constraint-Based Seating (Snake + Swap)\n"
        "  Input:  Interleaved queue + 2D grid\n"
        "  Output: Each student placed at (row, col)\n"
        "  Method: Snake traversal. Score each placement.\n"
        "          If conflict, search ahead 100 positions for better fit.\n"
        "  Time:   O(S x K) where K=swap window (100)"
    )
    el.append(Paragraph(algo, S['CB']))

    el.append(Paragraph("4.3 Phase 1 - Hall Allocation Detail", S['H2']))
    el.append(Paragraph(
        "The goal is to maximize subject mixing per hall. If a hall has students from 5 different "
        "subjects, the seating phase can easily ensure no adjacent same-subject. If a hall has only "
        "1 subject, it is impossible.", S['Body']))
    el.append(bullets([
        "Group all students by subject_code",
        "Sort subject groups by size (largest first)",
        "Within each subject, interleave by class (spread same-class apart)",
        "Build a global queue: round-robin 1 student from each subject",
        "For each student, find hall with: (a) remaining capacity > 0, (b) minimum count of that subject, (c) tie-break: more remaining space",
        "Assign student to that hall",
    ], S['BulletBody']))
    el.append(Paragraph(
        "<b>Complexity:</b> O(N x M) where N = total students, M = number of halls. "
        "For 1000 students and 20 halls: ~20,000 comparisons = less than 5ms.", S['Body']))

    el.append(Paragraph("4.4 Phase 2 - Subject Interleaving", S['H2']))
    phase2 = (
        "Input (Hall H001, 50 students):\n"
        "  CSE: [s1, s2, ..., s20]     (20 students)\n"
        "  ECE: [s21, s22, ..., s35]    (15 students)\n"
        "  EEE: [s36, s37, ..., s50]    (15 students)\n\n"
        "After interleaving:\n"
        "  [s1, s21, s36, s2, s22, s37, s3, s23, s38, ...]\n\n"
        "Consecutive students in the queue have different subjects."
    )
    el.append(Paragraph(phase2, S['CB']))

    el.append(Paragraph("4.5 Phase 3 - Snake Traversal + Constraint Swap", S['H2']))
    snake = (
        "Snake (boustrophedon) traversal:\n\n"
        "  Row 0: -->  -->  -->  -->    (left to right)\n"
        "  Row 1: <--  <--  <--  <--    (right to left)\n"
        "  Row 2: -->  -->  -->  -->    (left to right)\n\n"
        "Last seat of row N is adjacent to first seat of row N+1.\n"
        "Snake maintains interleaving pattern across row boundaries."
    )
    el.append(Paragraph(snake, S['CB']))

    el.append(Paragraph("Adjacency scoring function:", S['Body']))
    scoring = (
        "def _score(grid, row, col, student, rows, cols):\n"
        "    score = 0\n"
        "    for each neighbor in (left, right, top, bottom):\n"
        "        if neighbor.subject == student.subject:\n"
        "            score += 10\n"
        "            if neighbor.class == student.class:\n"
        "                score += 5\n"
        "    return score\n\n"
        "Score 0  = perfect (no adjacent same-subject)\n"
        "Score 10 = one adjacent same-subject\n"
        "Score 15 = same-subject AND same-class"
    )
    el.append(Paragraph(scoring, S['CB']))

    el.append(Paragraph("4.6 Correctness Guarantee", S['H2']))
    el.append(Paragraph(
        "<b>Theorem:</b> If a hall has students from 2 or more subjects and total students &lt;= capacity, "
        "the interleave + snake + swap algorithm produces zero same-subject adjacency violations.", S['Body']))
    el.append(Paragraph(
        "<b>Proof sketch:</b> With 2+ subjects, interleaving ensures consecutive queue positions "
        "have different subjects. Snake traversal ensures each cell's left/right neighbor is the "
        "previous/next in the queue (different subject). The top neighbor is in the same column of "
        "the previous row; subjects shift by N_subjects per row, so top neighbor is also different. "
        "Swap window handles edge cases at row boundaries.", S['Body']))
    el.append(Paragraph(
        "<b>When violations CAN occur:</b> Only when a single subject has more than 50% of a hall's "
        "students. Phase 1 specifically prevents this by distributing subjects evenly across halls.", S['Body']))

    el.append(Paragraph("4.7 Algorithm Comparison", S['H2']))
    comp = [
        ['Approach', 'Time', 'Optimal?', 'Why Rejected/Chosen'],
        ['Random', 'O(N)', 'No', 'No adjacency guarantee'],
        ['Graph Coloring', 'NP-hard', 'Yes', 'Impractical for grid layout'],
        ['Backtracking/CSP', 'O(N!) worst', 'Yes', 'Exponential, no time guarantee'],
        ['ILP Solver', 'Polynomial*', 'Yes', 'External dependency, complex'],
        ['Greedy+Interleave+Swap', 'O(NxK)', 'Near', 'Fast, explainable, correct for 2+ subjects'],
    ]
    el.append(make_table(comp[0], comp[1:], [110, 70, 50, 250]))
    el.append(PageBreak())


def section_api(el, S):
    el.append(Paragraph("5. REST API Reference", S['H1']))
    el.append(divider())

    el.append(Paragraph("5.1 Authentication Endpoints", S['H2']))
    eps = [
        ['Method', 'Endpoint', 'Auth', 'Description'],
        ['POST', '/api/auth/login/', 'None', 'Session login'],
        ['POST', '/api/auth/logout/', 'Any', 'Destroy session'],
        ['GET', '/api/auth/me/', 'Any', 'Current user profile'],
        ['PATCH', '/api/profile/update/', 'Any', 'Update profile'],
        ['POST', '/api/profile/change-password/', 'Any', 'Change password'],
    ]
    el.append(make_table(eps[0], eps[1:], [45, 170, 40, 225]))

    el.append(Paragraph("5.2 User Management", S['H2']))
    eps = [
        ['Method', 'Endpoint', 'Auth', 'Description'],
        ['GET', '/api/users/?role=FACULTY', 'Admin', 'List users by role'],
        ['POST', '/api/users/create/', 'Admin', 'Create account'],
        ['DELETE', '/api/users/{id}/delete/', 'Admin', 'Delete account'],
        ['GET', '/api/faculty/', 'Admin', 'Faculty list for dropdown'],
    ]
    el.append(make_table(eps[0], eps[1:], [50, 170, 40, 220]))

    el.append(Paragraph("5.3 CSV Upload Endpoints", S['H2']))
    eps = [
        ['Method', 'Endpoint', 'Auth', 'Description'],
        ['POST', '/api/csv/upload/students/', 'Admin', 'Upload students CSV'],
        ['POST', '/api/csv/upload/halls/', 'Admin', 'Upload halls CSV'],
        ['POST', '/api/csv/upload/combined/', 'Admin', 'Upload combined CSV'],
        ['GET', '/api/csv/?type=STUDENTS', 'Admin/Fac', 'List uploaded CSVs'],
        ['GET', '/api/csv/{id}/students/', 'Admin/Fac', 'Parsed students'],
        ['GET', '/api/csv/{id}/halls/', 'Admin/Fac', 'Parsed halls'],
        ['DELETE', '/api/csv/{id}/delete/', 'Admin', 'Delete CSV + records'],
    ]
    el.append(make_table(eps[0], eps[1:], [50, 175, 50, 205]))

    el.append(Paragraph("5.4 Allocation Endpoints", S['H2']))
    eps = [
        ['Method', 'Endpoint', 'Auth', 'Description'],
        ['POST', '/api/sessions/create/', 'Admin', 'Create + run allocation'],
        ['GET', '/api/sessions/', 'Admin/Fac', 'List sessions'],
        ['GET', '/api/sessions/{id}/', 'Admin/Fac', 'Session detail'],
        ['DELETE', '/api/sessions/{id}/delete/', 'Admin', 'Delete session'],
        ['POST', '/api/sessions/{id}/complete/', 'Admin', 'Mark completed'],
        ['GET', '/api/sessions/{id}/hall-layout/{pk}/', 'Admin/Fac', '2D grid data'],
        ['GET', '/api/export/csv/{id}/', 'Admin/Fac', 'CSV report'],
        ['GET', '/api/export/pdf/{id}/', 'Admin/Fac', 'PDF seating chart'],
    ]
    el.append(make_table(eps[0], eps[1:], [50, 200, 50, 180]))

    el.append(Paragraph("5.5 Student Endpoints", S['H2']))
    eps = [
        ['Method', 'Endpoint', 'Auth', 'Description'],
        ['GET', '/api/my-allocations/', 'Student', 'My seat assignments'],
        ['GET', '/api/my-allocations/{sid}/hall/{hpk}/', 'Student', 'Hall grid with my seat'],
        ['GET', '/api/students/', 'Admin/Fac', 'Paginated student list'],
        ['GET', '/api/students/search/?q=...', 'Admin/Fac', 'Search by roll number'],
    ]
    el.append(make_table(eps[0], eps[1:], [45, 210, 50, 175]))

    el.append(Paragraph("5.6 Create Allocation - Request", S['H2']))
    req = (
        'POST /api/sessions/create/\n\n'
        '{\n'
        '  "mode": "separate",\n'
        '  "student_csv_id": 1,\n'
        '  "hall_csv_id": 2,\n'
        '  "name": "Mid Semester Exam",\n'
        '  "exam_date": "2026-03-15",\n'
        '  "exam_time_from": "09:00",\n'
        '  "exam_time_to": "12:00",\n'
        '  "selected_classes": ["1st Year CSE"],\n'
        '  "excluded_student_ids": ["25001D5101"],\n'
        '  "hall_invigilators": {"H001": [5, 8]}\n'
        '}'
    )
    el.append(Paragraph(req, S['CB']))

    el.append(Paragraph("5.7 Create Allocation - Response", S['H2']))
    resp = (
        '{\n'
        '  "session_id": 1,\n'
        '  "status": "ALLOCATED",\n'
        '  "allocated": 980,\n'
        '  "unallocated": 20,\n'
        '  "warnings": ["Students (1000) exceed capacity (980)..."],\n'
        '  "time_ms": 342.5,\n'
        '  "hall_assignments": {"H001": 50, "H002": 50}\n'
        '}'
    )
    el.append(Paragraph(resp, S['CB']))
    el.append(PageBreak())


def section_frontend(el, S):
    el.append(Paragraph("6. Frontend Architecture", S['H1']))
    el.append(divider())

    el.append(Paragraph("6.1 Component Tree", S['H2']))
    tree = (
        "App\n"
        "  AuthProvider (context)\n"
        "    TooltipProvider (Radix)\n"
        "      AppRoutes\n"
        "        LoginPage\n"
        "        DashboardLayout\n"
        "          Sidebar (persistent navigation)\n"
        "          Outlet (page content)\n"
        "            DashboardPage      - StatsCard x 6\n"
        "            NewAllocationPage  - 4-step wizard\n"
        "              UploadBox        - Dropzone + validation\n"
        "              CsvCard          - Selectable card\n"
        "            AllocationsPage    - Sortable/filterable table\n"
        "            SessionDetailPage  - Tabs: Layout, List, Dist\n"
        "              SeatingGrid      - 2D grid with tooltips\n"
        "            StudentsPage       - Expandable rows + search\n"
        "            UsersPage          - Tab: Faculty/Student/Admin\n"
        "            ProfilePage        - Edit + change password\n"
        "            StudentPortal      - My allocations + hall view"
    )
    el.append(Paragraph(tree, S['CB']))

    el.append(Paragraph("6.2 Key Components", S['H2']))
    comps = [
        ['Component', 'File', 'Purpose'],
        ['SeatingGrid', 'SeatingGrid.jsx', '2D grid: colored subjects, tooltips, search highlight, found-seat pulse'],
        ['StatsCard', 'StatsCard.jsx', 'Dashboard metric with colored icon ring, hover lift'],
        ['PageHeader', 'PageHeader.jsx', 'Page title + subtitle + action buttons'],
        ['Sidebar', 'Sidebar.jsx', 'Role-based nav: dark gradient, active indicators'],
        ['UploadBox', 'NewAllocationPage', 'Drag-drop CSV upload with error display'],
    ]
    el.append(make_table(comps[0], comps[1:], [80, 120, 280]))

    el.append(Paragraph("6.3 UI Primitives (Radix-based)", S['H2']))
    prims = [
        ['Component', 'Library', 'Usage'],
        ['Dialog / Modal', 'Radix Dialog', 'Student search, create user, hall view'],
        ['Tabs', 'Radix Tabs', 'Session detail, user management'],
        ['Tooltip', 'Radix Tooltip', 'Seat hover in SeatingGrid'],
        ['Checkbox', 'Radix Checkbox', 'Student include/exclude'],
        ['Badge', 'Custom (CVA)', 'Status, role, subject indicators'],
        ['Button', 'Custom (CVA)', '9 variants, 6 sizes'],
    ]
    el.append(make_table(prims[0], prims[1:], [100, 90, 290]))

    el.append(Paragraph("6.4 SeatingGrid Technical Details", S['H2']))
    el.append(Paragraph(
        "The SeatingGrid is the most complex frontend component. It renders a full-width CSS Grid "
        "with sticky row/column headers and multiple interactive modes:", S['Body']))
    el.append(bullets([
        "<b>Normal mode:</b> All cells colored by subject with Radix tooltips",
        "<b>Search mode:</b> Matching cell gets glow animation, others dim to 8% opacity",
        "<b>Found-seat mode:</b> Cross-hall search: yellow highlight + pulse + auto-scroll",
        "<b>Filter mode:</b> Non-matching subjects/classes dim out",
        "<b>Student portal:</b> Student's own seat highlighted",
    ], S['BulletBody']))
    el.append(Paragraph(
        "Grid: CSS gridTemplateColumns = '48px repeat(N, minmax(0, 1fr))'. "
        "Each cell: min-height 72px. Colors: 15-color palette. "
        "Gradient overlay for depth. Found seat: #eab308 + outline + box-shadow animation.", S['Body']))
    el.append(PageBreak())


def section_csv(el, S):
    el.append(Paragraph("7. CSV Specifications", S['H1']))
    el.append(divider())

    el.append(Paragraph("7.1 Students CSV Format", S['H2']))
    el.append(make_table(
        ['Column', 'Required', 'Aliases', 'Description'],
        [
            ['student_id', 'Yes', 'roll_no, roll_number, rollno', 'Unique identifier'],
            ['name', 'Yes', 'student_name', 'Full name'],
            ['subject_code', 'Yes', 'subject', 'Subject code'],
            ['class', 'No', 'student_class', 'Class/section'],
        ], [80, 50, 150, 200]))

    el.append(Paragraph("7.2 Halls CSV Format", S['H2']))
    el.append(make_table(
        ['Column', 'Required', 'Aliases', 'Description'],
        [
            ['hall_id', 'Yes', 'hall, hall_name, name', 'Hall identifier'],
            ['capacity', 'Yes', 'cap, hall_capacity', 'Max seats (int > 0)'],
            ['rows', 'No', 'hall_rows', 'Grid rows (auto if missing)'],
            ['columns', 'No', 'hall_columns, cols', 'Grid cols (auto if missing)'],
        ], [80, 50, 150, 200]))

    el.append(Paragraph("7.3 Auto Row/Column Calculation", S['H2']))
    calc = (
        "columns = ceil(sqrt(capacity))\n"
        "rows = ceil(capacity / columns)\n\n"
        "Examples:\n"
        "  capacity=50  -> 8x7 = 56 seats (6 empty)\n"
        "  capacity=100 -> 10x10 = 100 seats\n"
        "  capacity=30  -> 6x5 = 30 seats"
    )
    el.append(Paragraph(calc, S['CB']))

    el.append(Paragraph("7.4 Validation Rules", S['H2']))
    el.append(make_table(
        ['Rule', 'Type', 'Message'],
        [
            ['Missing required column', 'Error', 'Missing columns: student_id...'],
            ['Empty student_id', 'Error', 'Row N: Missing student_id'],
            ['Duplicate student_id', 'Error', 'Row N: Duplicate X (first at M)'],
            ['Duplicate hall_id', 'Error', 'Row N: Duplicate X (first at M)'],
            ['Capacity <= 0', 'Error', 'Row N: Invalid capacity for H001'],
            ['Non-integer capacity', 'Error', 'Row N: Invalid capacity abc'],
            ['No data rows', 'Error', 'No data rows found'],
            ['rows x cols < capacity', 'Warning', 'Hall H001: auto-adjusting'],
        ], [130, 50, 300]))
    el.append(PageBreak())


def section_seating(el, S):
    el.append(Paragraph("8. Seating Constraint Logic", S['H1']))
    el.append(divider())

    el.append(Paragraph("8.1 Adjacency Definition", S['H2']))
    el.append(Paragraph(
        "Two seats are adjacent if directly left, right, above, or below (4-directional). "
        "Diagonal neighbors are NOT adjacent.", S['Body']))
    adj = (
        "           [ TOP  ]\n"
        "  [LEFT]   [SEAT]   [RIGHT]\n"
        "           [BOTTOM]\n\n"
        "  Diagonal = no constraint"
    )
    el.append(Paragraph(adj, S['CB']))

    el.append(Paragraph("8.2 Constraint Priority", S['H2']))
    el.append(bullets([
        "<b>Hard:</b> No hall exceeds capacity (overflow goes to unallocated)",
        "<b>Hard:</b> Each student assigned exactly once (unique_together)",
        "<b>Soft:</b> No same-subject adjacency (maximized, violations logged)",
        "<b>Soft:</b> Same-class separation (best effort within subject)",
    ], S['BulletBody']))

    el.append(Paragraph("8.3 When Separation is Impossible", S['H2']))
    el.append(Paragraph(
        "If a single subject has more than 50% of a hall's students, zero-adjacency is mathematically "
        "impossible. The system maximizes separation, logs violations, and displays them. "
        "Phase 1 hall allocation specifically prevents this.", S['Body']))
    el.append(PageBreak())


def section_performance(el, S):
    el.append(Paragraph("9. Performance and Scalability", S['H1']))
    el.append(divider())

    el.append(Paragraph("9.1 Benchmarks", S['H2']))
    el.append(make_table(
        ['Students', 'Halls', 'Algorithm', 'DB Save', 'Total', 'Violations'],
        [
            ['100', '2', '~3ms', '~20ms', '~50ms', '0'],
            ['200', '4', '~6ms', '~40ms', '~80ms', '0'],
            ['500', '10', '~15ms', '~100ms', '~180ms', '0'],
            ['1000', '20', '~35ms', '~200ms', '~350ms', '0'],
            ['2000', '40', '~80ms', '~400ms', '~700ms', '0'],
            ['5000', '100', '~200ms', '~1s', '~1.5s', '0'],
        ], [60, 45, 70, 65, 70, 60]))
    el.append(Paragraph("<i>Measured on standard laptop (i5, 8GB, SSD)</i>", S['Caption']))

    el.append(Paragraph("9.2 Optimizations", S['H2']))
    el.append(bullets([
        "<b>Bulk DB:</b> bulk_create() for allocations and violations",
        "<b>Background threads:</b> Student account creation non-blocking",
        "<b>MD5 hashing:</b> For auto-generated student passwords (1500x faster than bcrypt)",
        "<b>Bounded swap:</b> Window of 100 keeps Phase 3 linear",
        "<b>Eager loading:</b> select_related() on all FK queries",
        "<b>Client-side sort/filter:</b> No re-fetch for column sorting",
    ], S['BulletBody']))

    el.append(Paragraph("9.3 Complexity", S['H2']))
    el.append(make_table(
        ['Phase', 'Time', 'Space', 'Bottleneck'],
        [
            ['Hall Allocation', 'O(N x M)', 'O(N + M)', 'Hall selection'],
            ['Interleaving', 'O(N)', 'O(N)', 'Queue build'],
            ['Seating', 'O(N x K)', 'O(R x C)', 'Swap search (K=100)'],
            ['DB Save', 'O(N)', 'O(N)', 'bulk_create'],
            ['Total', 'O(N x max(M,K))', 'O(N + RxC)', '-'],
        ], [100, 80, 80, 220]))
    el.append(PageBreak())


def section_exports(el, S):
    el.append(Paragraph("10. Export System", S['H1']))
    el.append(divider())

    el.append(Paragraph("10.1 CSV Export", S['H2']))
    csv_fmt = (
        "Student ID, Name, Subject, Class, Hall, Row, Column\n"
        "25001D5101, Aarav Sharma, CS101, 1st Year CSE, H001, 1, 1\n"
        "...\n\n"
        "--- UNALLOCATED STUDENTS ---\n"
        "Student ID, Reason\n"
        "25001D5199, no capacity."
    )
    el.append(Paragraph(csv_fmt, S['CB']))

    el.append(Paragraph("10.2 PDF Export Contents", S['H2']))
    el.append(bullets([
        "Session metadata: name, date, time, source CSVs",
        "Summary table: students, allocated, unallocated, halls, capacity, time",
        "Subject color legend",
        "Hall-wise seating grids with color-coded cells",
        "Invigilator names per hall",
        "Occupancy count per hall",
        "Unallocated students table",
        "Page breaks between halls",
    ], S['BulletBody']))
    el.append(PageBreak())


def section_auth(el, S):
    el.append(Paragraph("11. Authentication and Authorization", S['H1']))
    el.append(divider())

    el.append(Paragraph("11.1 Session-Based Auth", S['H2']))
    el.append(Paragraph(
        "Django session authentication with CSRF protection. Axios interceptor sends CSRF token "
        "from cookies on every request.", S['Body']))

    el.append(Paragraph("11.2 Role-Based Access Control", S['H2']))
    el.append(make_table(
        ['Resource', 'Admin', 'Faculty', 'Student'],
        [
            ['Dashboard', 'Full stats', 'Own duties', 'Redirect'],
            ['New Allocation', 'Full access', 'No', 'No'],
            ['View Allocations', 'All sessions', 'Assigned only', 'No'],
            ['Hall Layout', 'All halls', 'Assigned halls', 'Own hall'],
            ['Students List', 'All students', 'Read-only', 'No'],
            ['User Management', 'CRUD', 'No', 'No'],
            ['CSV Upload/Delete', 'Yes', 'No', 'No'],
            ['Export PDF/CSV', 'Yes', 'Yes', 'No'],
            ['My Allocations', 'No', 'No', 'Yes'],
            ['Profile', 'Yes', 'Yes', 'Yes'],
        ], [110, 100, 100, 170]))

    el.append(Paragraph("11.3 Student Account Auto-Creation", S['H2']))
    stu_auth = (
        "Username: student_id (lowercase) e.g. '25001d5101'\n"
        "Password: {student_id}@{first4_of_name} e.g. '25001d5101@aara'\n\n"
        "Hashing: MD5 for speed (auto-generated, changeable)\n"
        "Thread: daemon, non-blocking"
    )
    el.append(Paragraph(stu_auth, S['CB']))
    el.append(PageBreak())


def section_edge_cases(el, S):
    el.append(Paragraph("12. Edge Cases and Error Handling", S['H1']))
    el.append(divider())
    el.append(make_table(
        ['Scenario', 'Handling'],
        [
            ['Students > total capacity', 'Warning, max allocated, rest unallocated'],
            ['Duplicate student IDs', 'Rejected with row numbers'],
            ['Duplicate hall IDs', 'Rejected with row numbers'],
            ['Invalid capacity (0, neg, text)', 'Rejected per row'],
            ['Missing required columns', 'Rejected with column list'],
            ['Empty CSV', 'Rejected: No data rows found'],
            ['Hall double-booked same time', 'HTTP 409 with hall names'],
            ['Student in two exams same time', 'HTTP 409 with student IDs'],
            ['Single subject in hall', 'Allocated, adjacency violations logged'],
            ['rows x cols < capacity', 'Auto-adjusted with warning'],
            ['Whitespace in CSV', 'Auto-trimmed'],
            ['Column name aliases', 'Recognized: roll_no, cap, etc.'],
            ['No halls provided', 'Error + all students unallocated'],
            ['Faculty not found', 'Silently skipped'],
            ['Delete CSV with sessions', 'Cascade deletes all related'],
        ], [170, 310]))
    el.append(PageBreak())


def section_deployment(el, S):
    el.append(Paragraph("13. Deployment Guide", S['H1']))
    el.append(divider())

    el.append(Paragraph("13.1 Prerequisites", S['H2']))
    el.append(bullets(["Python 3.10+ with pip", "Node.js 18+ with npm", "Git"], S['BulletBody']))

    el.append(Paragraph("13.2 Backend Setup", S['H2']))
    be = (
        "cd backend\n"
        "python3 -m venv env\n"
        "source env/bin/activate\n\n"
        "pip install django djangorestframework reportlab django-cors-headers\n\n"
        "python manage.py makemigrations allocation\n"
        "python manage.py migrate\n\n"
        "# Create admin\n"
        "python manage.py shell -c \"\n"
        "from allocation.models import User\n"
        "from django.contrib.auth.hashers import make_password\n"
        "User.objects.create(\n"
        "    username='admin', password=make_password('admin123'),\n"
        "    role='ADMIN', is_superuser=True, is_staff=True\n"
        ")\"\n\n"
        "python manage.py runserver  # Port 8000"
    )
    el.append(Paragraph(be, S['CB']))

    el.append(Paragraph("13.3 Frontend Setup", S['H2']))
    fe = (
        "cd frontend\n"
        "npm install\n"
        "npm run dev  # Port 3000\n\n"
        "# vite.config.js proxy:\n"
        "server: {\n"
        "  port: 3000,\n"
        "  proxy: { '/api': 'http://127.0.0.1:8000' }\n"
        "}"
    )
    el.append(Paragraph(fe, S['CB']))

    el.append(Paragraph("13.4 Generate Test Data", S['H2']))
    gen = (
        "cd backend\n"
        "python generate_csvs.py\n\n"
        "# Generates in sample_data/:\n"
        "#   students_1000.csv   - 1000 students, 5 branches\n"
        "#   halls_20x50.csv     - 20 halls x 50 capacity\n"
        "#   halls_mixed.csv     - Mixed sizes\n"
        "#   + error CSVs for validation testing"
    )
    el.append(Paragraph(gen, S['CB']))
    el.append(PageBreak())


def section_testing(el, S):
    el.append(Paragraph("14. Testing Strategy", S['H1']))
    el.append(divider())

    el.append(Paragraph("14.1 Test CSV Matrix", S['H2']))
    el.append(make_table(
        ['CSV File', 'Purpose', 'Expected'],
        [
            ['students_1000 + halls_20x50', 'Normal large', '1000 allocated, 0 unallocated'],
            ['students_100_same + halls_2x50', 'Same subject', '100 allocated, adjacency logged'],
            ['students_1000 + halls_small', 'Overflow', '150 allocated, 850 unallocated'],
            ['students_1000 + halls_mixed', 'Mixed sizes', 'Distributed across halls'],
            ['error_students_duplicates', 'Duplicate IDs', 'Rejected with errors'],
            ['error_halls_bad_capacity', 'Bad capacity', 'Rejected per row'],
            ['error_halls_missing_columns', 'Missing cols', 'Rejected with list'],
        ], [150, 100, 230]))

    el.append(Paragraph("14.2 Functional Checklist", S['H2']))
    el.append(bullets([
        "Upload students CSV - verify count, subjects, classes",
        "Upload halls CSV - verify hall list, capacities",
        "Run allocation - verify time < 10s, count correct",
        "Check grid - no same-subject adjacent (visual)",
        "Search across halls - auto-switch + highlight",
        "Export PDF - color grid, all halls, unallocated",
        "Export CSV - all columns, unallocated section",
        "Collision test - same hall same time = 409",
        "Student login - only own allocations visible",
        "Faculty login - only assigned sessions",
        "Sort all columns on allocations page",
        "Filter by subject/class on students page",
        "Expand student rows to see all exams",
    ], S['BulletBody']))

    el.append(Paragraph("14.3 Performance Tests", S['H2']))
    el.append(bullets([
        "1000 students + 20 halls: allocation < 10 seconds",
        "5000 students + 100 halls: allocation < 5 seconds",
        "PDF generation for 20 halls: < 3 seconds",
        "Page load with 1000 students: < 2 seconds",
    ], S['BulletBody']))


# ═══════════════════════════════════════════���═══
# MAIN
# ═══════════════════════════════════════════════
def build_document():
    doc = SimpleDocTemplate(
        OUTPUT_FILE, pagesize=A4,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        title="ExamAlloc Technical Documentation",
        author="ExamAlloc Team",
    )
    S = get_styles()
    el = []

    cover_page(el, S)
    section_toc(el, S)
    section_overview(el, S)
    section_architecture(el, S)
    section_database(el, S)
    section_algorithm(el, S)
    section_api(el, S)
    section_frontend(el, S)
    section_csv(el, S)
    section_seating(el, S)
    section_performance(el, S)
    section_exports(el, S)
    section_auth(el, S)
    section_edge_cases(el, S)
    section_deployment(el, S)
    section_testing(el, S)

    doc.build(el)
    print(f"  Generated: {OUTPUT_FILE}")


if __name__ == '__main__':
    build_document()