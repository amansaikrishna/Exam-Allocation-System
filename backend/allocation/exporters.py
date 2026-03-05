import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak


def generate_csv_report(session):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name', 'Subject', 'Class', 'Hall', 'Row', 'Column'])
    for a in session.allocations.select_related('student', 'hall').order_by('hall__hall_id', 'row', 'column'):
        writer.writerow([
            a.student.student_id, a.student.name, a.student.subject_code,
            a.student.student_class, a.hall.hall_id, a.row + 1, a.column + 1,
        ])
    unalloc = session.violations.filter(violation_type='UNALLOCATED')
    if unalloc.exists():
        writer.writerow([])
        writer.writerow(['--- UNALLOCATED STUDENTS ---'])
        writer.writerow(['Student ID', 'Reason'])
        for v in unalloc:
            writer.writerow([v.student_id_ref, v.description])
    return output.getvalue()


# Vivid, saturated colors for PDF grid
VIVID_PALETTE = [
    colors.HexColor('#4f46e5'),  # Indigo
    colors.HexColor('#059669'),  # Emerald
    colors.HexColor('#d97706'),  # Amber
    colors.HexColor('#dc2626'),  # Red
    colors.HexColor('#7c3aed'),  # Violet
    colors.HexColor('#0891b2'),  # Cyan
    colors.HexColor('#c026d3'),  # Fuchsia
    colors.HexColor('#0d9488'),  # Teal
    colors.HexColor('#e11d48'),  # Rose
    colors.HexColor('#2563eb'),  # Blue
    colors.HexColor('#ca8a04'),  # Yellow-dark
    colors.HexColor('#16a34a'),  # Green
    colors.HexColor('#9333ea'),  # Purple
    colors.HexColor('#ea580c'),  # Orange
    colors.HexColor('#0284c7'),  # Sky
]

# Lighter tints for cell backgrounds (vivid but readable with dark text)
VIVID_CELL_PALETTE = [
    colors.HexColor('#a5b4fc'),  # Indigo light
    colors.HexColor('#6ee7b7'),  # Emerald light
    colors.HexColor('#fcd34d'),  # Amber light
    colors.HexColor('#fca5a5'),  # Red light
    colors.HexColor('#c4b5fd'),  # Violet light
    colors.HexColor('#67e8f9'),  # Cyan light
    colors.HexColor('#f0abfc'),  # Fuchsia light
    colors.HexColor('#5eead4'),  # Teal light
    colors.HexColor('#fda4af'),  # Rose light
    colors.HexColor('#93c5fd'),  # Blue light
    colors.HexColor('#fde047'),  # Yellow light
    colors.HexColor('#86efac'),  # Green light
    colors.HexColor('#d8b4fe'),  # Purple light
    colors.HexColor('#fdba74'),  # Orange light
    colors.HexColor('#7dd3fc'),  # Sky light
]

# Dark text colors per subject for readability on vivid backgrounds
VIVID_TEXT_PALETTE = [
    colors.HexColor('#312e81'),  # Indigo dark
    colors.HexColor('#064e3b'),  # Emerald dark
    colors.HexColor('#78350f'),  # Amber dark
    colors.HexColor('#7f1d1d'),  # Red dark
    colors.HexColor('#4c1d95'),  # Violet dark
    colors.HexColor('#164e63'),  # Cyan dark
    colors.HexColor('#701a75'),  # Fuchsia dark
    colors.HexColor('#134e4a'),  # Teal dark
    colors.HexColor('#881337'),  # Rose dark
    colors.HexColor('#1e3a5f'),  # Blue dark
    colors.HexColor('#713f12'),  # Yellow dark
    colors.HexColor('#14532d'),  # Green dark
    colors.HexColor('#581c87'),  # Purple dark
    colors.HexColor('#7c2d12'),  # Orange dark
    colors.HexColor('#0c4a6e'),  # Sky dark
]


def generate_pdf_seating_chart(session):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"<b>{session.name}</b>", styles['Title']))
    date_str = session.exam_date_str if session.exam_date else '—'
    time_str = session.exam_time_str if session.exam_time_from else '—'
    elements.append(Paragraph(f"Date: {date_str} &nbsp;&nbsp; Time: {time_str}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary
    violation_count = session.violations.count()
    summary_data = [
        ['Total Students', str(session.total_students)],
        ['Allocated', str(session.allocated_count)],
        ['Unallocated', str(session.unallocated_count)],
        ['Halls', str(session.total_halls)],
        ['Total Capacity', str(session.total_capacity)],
        ['Time', f"{session.allocation_time_ms or 'N/A'} ms"],
    ]
    summary_table = Table(summary_data, colWidths=[150, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Source info
    source_parts = []
    if session.student_csv:
        source_parts.append(f"Students: {session.student_csv.name}")
    if session.hall_csv:
        source_parts.append(f"Halls: {session.hall_csv.name}")
    if source_parts:
        elements.append(Paragraph(f"Source: {' | '.join(source_parts)}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Subject color map
    allocs = session.allocations.select_related('student', 'hall').order_by('hall__hall_id', 'row', 'column')
    subjects = sorted(set(a.student.subject_code for a in allocs))
    subj_cell_colors = {s: VIVID_CELL_PALETTE[i % len(VIVID_CELL_PALETTE)] for i, s in enumerate(subjects)}
    subj_badge_colors = {s: VIVID_PALETTE[i % len(VIVID_PALETTE)] for i, s in enumerate(subjects)}
    subj_text_colors = {s: VIVID_TEXT_PALETTE[i % len(VIVID_TEXT_PALETTE)] for i, s in enumerate(subjects)}

    # Legend
    if subjects:
        legend_data = [['Subject', 'Color']]
        legend_style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]
        for i, s in enumerate(subjects):
            legend_data.append([s, ''])
            legend_style.append(('BACKGROUND', (1, i + 1), (1, i + 1), subj_cell_colors[s]))
            legend_style.append(('FONTNAME', (0, i + 1), (0, i + 1), 'Helvetica-Bold'))
            legend_style.append(('TEXTCOLOR', (0, i + 1), (0, i + 1), subj_badge_colors[s]))
        lt = Table(legend_data, colWidths=[100, 50])
        lt.setStyle(TableStyle(legend_style))
        elements.append(lt)
        elements.append(Spacer(1, 16))

    # Hall-wise seating charts
    halls = session.halls.all().order_by('hall_id')
    for hall in halls:
        elements.append(Paragraph(
            f"<b>Hall: {hall.hall_id}</b> ({hall.rows} x {hall.columns}, Capacity: {hall.capacity})",
            styles['Heading2']))

        # Invigilators
        invigs = hall.invigilators.select_related('faculty').all()
        if invigs:
            inv_names = ', '.join(i.faculty.get_full_name() or i.faculty.username for i in invigs)
            elements.append(Paragraph(f"Invigilators: {inv_names}", styles['Normal']))

        elements.append(Spacer(1, 8))

        # Build grid
        grid = [[None] * hall.columns for _ in range(hall.rows)]
        hall_allocs = allocs.filter(hall=hall)
        for a in hall_allocs:
            grid[a.row][a.column] = a

        # Header row
        header = [''] + [f"C{c + 1}" for c in range(hall.columns)]
        table_data = [header]
        style_cmds = [
            # Column headers
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            # Row headers
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 7),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
            # Cell defaults
            ('FONTSIZE', (1, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#475569')),
            ('PADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        for r in range(hall.rows):
            row_data = [f"R{r + 1}"]
            for c in range(hall.columns):
                a = grid[r][c]
                if a:
                    cell_text = f"{a.student.student_id}\n{a.student.subject_code}"
                    row_data.append(cell_text)
                    subj = a.student.subject_code
                    if subj in subj_cell_colors:
                        style_cmds.append(('BACKGROUND', (c + 1, r + 1), (c + 1, r + 1), subj_cell_colors[subj]))
                        style_cmds.append(('TEXTCOLOR', (c + 1, r + 1), (c + 1, r + 1), subj_text_colors[subj]))
                        style_cmds.append(('FONTNAME', (c + 1, r + 1), (c + 1, r + 1), 'Helvetica-Bold'))
                else:
                    row_data.append('')
                    style_cmds.append(('BACKGROUND', (c + 1, r + 1), (c + 1, r + 1), colors.HexColor('#f1f5f9')))
                    style_cmds.append(('TEXTCOLOR', (c + 1, r + 1), (c + 1, r + 1), colors.HexColor('#cbd5e1')))
            table_data.append(row_data)

        col_width = min(65, (landscape(A4)[0] - 100) / (hall.columns + 1))
        col_widths = [30] + [col_width] * hall.columns

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(style_cmds))
        elements.append(t)
        elements.append(Spacer(1, 8))

        # Hall stats
        occupied = hall_allocs.count()
        pct = round((occupied / hall.capacity) * 100) if hall.capacity else 0
        elements.append(Paragraph(
            f"<b>Occupied: {occupied}/{hall.capacity}</b> ({pct}%)", styles['Normal']))
        elements.append(PageBreak())

    # Unallocated section
    unalloc = session.violations.filter(violation_type='UNALLOCATED')
    if unalloc.exists():
        elements.append(Paragraph("<b>Unallocated Students</b>", styles['Heading2']))
        ua_data = [['Student ID', 'Reason']]
        for v in unalloc:
            ua_data.append([v.student_id_ref, v.description[:80]])
        ua_table = Table(ua_data, colWidths=[120, 400])
        ua_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fef2f2'), colors.white]),
        ]))
        elements.append(ua_table)

    doc.build(elements)
    buf.seek(0)
    return buf