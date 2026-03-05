import math
from datetime import datetime
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import time as time_module
import threading

from .models import *
from .serializers import *
from .permissions import IsAdmin, IsAdminOrFaculty
from .validators import validate_students_csv, validate_halls_csv, validate_combined_csv
from .engine import run_allocation
from .exporters import generate_csv_report, generate_pdf_seating_chart


# ═══ AUTH ═══
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    ser = LoginSerializer(data=request.data); ser.is_valid(raise_exception=True)
    login(request, ser.validated_data['user'])
    return Response({'message':'OK','user':UserSerializer(ser.validated_data['user']).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request); return Response({'message':'OK'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    data = UserSerializer(request.user).data
    if request.user.role == 'STUDENT':
        sr = StudentRecord.objects.filter(user=request.user).first()
        if sr: data['student_profile'] = {'student_id':sr.student_id,'name':sr.name,'subject_code':sr.subject_code,'student_class':sr.student_class}
    return Response(data)

@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    ser = ProfileUpdateSerializer(request.user, data=request.data, partial=True); ser.is_valid(raise_exception=True); ser.save()
    return Response(UserSerializer(request.user).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    ser = ChangePasswordSerializer(data=request.data, context={'request':request}); ser.is_valid(raise_exception=True)
    request.user.set_password(ser.validated_data['new_password']); request.user.save()
    update_session_auth_hash(request, request.user); return Response({'message':'Password changed.'})


# ═══ USERS ═══
@api_view(['GET'])
@permission_classes([IsAdmin])
def list_users_view(request):
    qs = User.objects.all(); role = request.query_params.get('role')
    if role: qs = qs.filter(role=role.upper())
    return Response(UserSerializer(qs, many=True).data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_user_view(request):
    d = request.data; uname = d.get('username',''); pwd = d.get('password','')
    if not uname or not pwd: return Response({'error':'username + password required'},status=400)
    if User.objects.filter(username=uname).exists(): return Response({'error':f"'{uname}' exists"},status=400)
    u = User.objects.create(username=uname, password=make_password(pwd), role=d.get('role','FACULTY'),
        first_name=d.get('first_name',''), last_name=d.get('last_name',''), email=d.get('email',''), department=d.get('department',''))
    return Response(UserSerializer(u).data, status=201)

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_user_view(request, user_id):
    try: t = User.objects.get(pk=user_id)
    except: return Response({'error':'Not found'},status=404)
    if t.id == request.user.id: return Response({'error':'Cannot delete self'},status=400)
    t.delete(); return Response({'message':'Deleted'})

@api_view(['GET'])
@permission_classes([IsAdmin])
def faculty_list_view(request):
    return Response([{'id':f.id,'username':f.username,'name':f.get_full_name() or f.username,'department':f.department}
        for f in User.objects.filter(role='FACULTY')])


# ═══ STUDENTS (read-only) ═══
@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def list_students_view(request):
    qs = StudentRecord.objects.select_related('csv_upload').all()
    s = request.query_params.get('search')
    if s: qs = qs.filter(Q(student_id__icontains=s)|Q(name__icontains=s))
    csv_id = request.query_params.get('csv_id')
    if csv_id: qs = qs.filter(csv_upload_id=csv_id)
    page = int(request.query_params.get('page',1)); pp = int(request.query_params.get('per_page',50))
    total = qs.count(); records = qs[(page-1)*pp:page*pp]
    return Response({'results':StudentRecordSerializer(records,many=True).data,'total':total,'page':page})

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def search_student_view(request):
    q = request.query_params.get('q','').strip()
    if not q: return Response({'error':'Provide ?q='},status=400)
    exact = StudentRecord.objects.filter(student_id__iexact=q).first()
    if not exact:
        matches = StudentRecord.objects.filter(student_id__icontains=q)[:10]
        if not matches: return Response({'error':f"No match for '{q}'"},status=404)
        return Response({'exact_match':False,'suggestions':StudentRecordSerializer(matches,many=True).data})
    allocs = SeatAllocation.objects.filter(student=exact).select_related('hall','session')
    return Response({'exact_match':True,'student':StudentRecordSerializer(exact).data,
        'allocations':[{'session_id':a.session.id,'session_name':a.session.name,'status':a.session.status,
            'hall_id':a.hall.hall_id,'row':a.row+1,'column':a.column+1,
            'exam_date':a.session.exam_date_str,'exam_time':a.session.exam_time_str} for a in allocs]})


# ═══ CSV UPLOADS ═══
@api_view(['POST'])
@permission_classes([IsAdmin])
@parser_classes([MultiPartParser, FormParser])
def upload_students_csv_view(request):
    f = request.FILES.get('file')
    if not f: return Response({'error':'No file.'},status=400)
    csv_name = request.data.get('name','') or f.name.replace('.csv','')
    try: content = f.read().decode('utf-8')
    except: return Response({'error':'Must be UTF-8 CSV.'},status=400)
    parsed = validate_students_csv(content)
    if parsed['errors']:
        return Response({'error':'Validation failed.','parse_errors':parsed['errors'],'parse_warnings':parsed.get('warnings',[])},status=400)
    if not parsed['students']:
        return Response({'error':'No valid students.'},status=400)
    cu = CSVUpload.objects.create(name=csv_name, filename=f.name, csv_type='STUDENTS', uploaded_by=request.user)
    StudentRecord.objects.bulk_create([
        StudentRecord(csv_upload=cu, student_id=s['student_id'], name=s['name'],
            subject_code=s['subject_code'], student_class=s.get('class',''))
        for s in parsed['students']
    ])
    return Response({
        'csv_id':cu.id, 'name':cu.name, 'csv_type':'STUDENTS',
        'total_students':len(parsed['students']), 'parse_warnings':parsed.get('warnings',[]),
        'classes':sorted(set(s.get('class','') for s in parsed['students'])-{''}),
        'subjects':sorted(set(s['subject_code'] for s in parsed['students'])),
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAdmin])
@parser_classes([MultiPartParser, FormParser])
def upload_halls_csv_view(request):
    f = request.FILES.get('file')
    if not f: return Response({'error':'No file.'},status=400)
    csv_name = request.data.get('name','') or f.name.replace('.csv','')
    try: content = f.read().decode('utf-8')
    except: return Response({'error':'Must be UTF-8 CSV.'},status=400)
    parsed = validate_halls_csv(content)
    if parsed['errors']:
        return Response({'error':'Validation failed.','parse_errors':parsed['errors'],'parse_warnings':parsed.get('warnings',[])},status=400)
    if not parsed['halls']:
        return Response({'error':'No valid halls.'},status=400)
    cu = CSVUpload.objects.create(name=csv_name, filename=f.name, csv_type='HALLS', uploaded_by=request.user)
    for h in parsed['halls']:
        HallEntry.objects.create(csv_upload=cu, hall_id=h['hall_id'], capacity=h['capacity'], rows=h['rows'], columns=h['columns'])
    return Response({
        'csv_id':cu.id, 'name':cu.name, 'csv_type':'HALLS',
        'total_halls':len(parsed['halls']), 'parse_warnings':parsed.get('warnings',[]),
        'halls':[{'hall_id':h['hall_id'],'capacity':h['capacity'],'rows':h['rows'],'columns':h['columns']} for h in parsed['halls']],
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAdmin])
@parser_classes([MultiPartParser, FormParser])
def upload_combined_csv_view(request):
    f = request.FILES.get('file')
    if not f: return Response({'error':'No file.'},status=400)
    csv_name = request.data.get('name','') or f.name.replace('.csv','')
    try: content = f.read().decode('utf-8')
    except: return Response({'error':'Must be UTF-8 CSV.'},status=400)
    parsed = validate_combined_csv(content)
    if parsed['errors']:
        return Response({'error':'Validation failed.','parse_errors':parsed['errors'],'parse_warnings':parsed.get('warnings',[])},status=400)
    if not parsed['students']:
        return Response({'error':'No valid data.'},status=400)
    cu = CSVUpload.objects.create(name=csv_name, filename=f.name, csv_type='COMBINED', uploaded_by=request.user)
    StudentRecord.objects.bulk_create([
        StudentRecord(csv_upload=cu, student_id=s['student_id'], name=s['name'],
            subject_code=s['subject_code'], student_class=s.get('class',''))
        for s in parsed['students']
    ])
    for hid, hd in parsed['halls'].items():
        HallEntry.objects.create(csv_upload=cu, hall_id=hid, capacity=hd['capacity'], rows=hd['rows'], columns=hd['columns'])
    return Response({
        'csv_id':cu.id, 'name':cu.name, 'csv_type':'COMBINED',
        'total_students':len(parsed['students']), 'total_halls':len(parsed['halls']),
        'parse_warnings':parsed.get('warnings',[]),
        'classes':sorted(set(s.get('class','') for s in parsed['students'])-{''}),
        'subjects':sorted(set(s['subject_code'] for s in parsed['students'])),
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def list_csv_view(request):
    csv_type = request.query_params.get('type')
    qs = CSVUpload.objects.all()
    if csv_type: qs = qs.filter(csv_type=csv_type.upper())
    return Response(CSVUploadSerializer(qs, many=True).data)

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def csv_students_view(request, csv_id):
    try: cu = CSVUpload.objects.get(pk=csv_id)
    except: return Response({'error':'Not found'},status=404)
    qs = cu.students.all()
    cls = request.query_params.get('student_class')
    if cls: qs = qs.filter(student_class=cls)
    subj = request.query_params.get('subject')
    if subj: qs = qs.filter(subject_code=subj)
    classes = sorted(set(cu.students.values_list('student_class',flat=True).distinct())-{''})
    subjects = sorted(set(cu.students.values_list('subject_code',flat=True).distinct()))
    return Response({'students':StudentRecordSerializer(qs,many=True).data,'classes':classes,'subjects':subjects,'total':qs.count()})

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def csv_halls_view(request, csv_id):
    try: cu = CSVUpload.objects.get(pk=csv_id)
    except: return Response({'error':'Not found'},status=404)
    return Response({'halls':HallEntrySerializer(cu.hall_entries.all(),many=True).data,'total':cu.hall_entries.count()})

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_csv_view(request, csv_id):
    try: cu = CSVUpload.objects.get(pk=csv_id)
    except: return Response({'error':'Not found'},status=404)
    sc = cu.students.count()
    user_ids = list(cu.students.exclude(user__isnull=True).values_list('user_id',flat=True))
    cu.delete()
    da = 0
    if user_ids: da = User.objects.filter(id__in=user_ids, role='STUDENT').delete()[0]
    return Response({'message':f'Deleted. {sc} students, {da} accounts removed.'})


# ═══ COLLISION ═══
def _times_overlap(s1, e1, s2, e2):
    return s1 < e2 and s2 < e1

def _check_hall_collision(hall_ids, ed, tf, tt, exc=None):
    confs = []
    qs = AllocationSession.objects.filter(exam_date=ed)
    if exc: qs = qs.exclude(pk=exc)
    for s in qs:
        if _times_overlap(tf, tt, s.exam_time_from, s.exam_time_to):
            bk = set(s.halls.values_list('hall_id', flat=True))
            ov = set(hall_ids) & bk
            if ov:
                confs.append(f"Hall(s) {', '.join(sorted(ov))} booked for '{s.name}' on {ed} "
                             f"({s.exam_time_from.strftime('%I:%M %p')}–{s.exam_time_to.strftime('%I:%M %p')})")
    return confs

def _check_student_collision(sids, ed, tf, tt, exc=None):
    confs = []
    qs = AllocationSession.objects.filter(exam_date=ed)
    if exc: qs = qs.exclude(pk=exc)
    for s in qs:
        if _times_overlap(tf, tt, s.exam_time_from, s.exam_time_to):
            al = set(s.allocations.values_list('student__student_id', flat=True))
            ov = set(sids) & al
            if ov:
                sample = sorted(ov)[:5]
                more = f" +{len(ov)-5}" if len(ov) > 5 else ""
                confs.append(f"{len(ov)} student(s) already in '{s.name}': {', '.join(sample)}{more}")
    return confs


# ═══ BACKGROUND STUDENT ACCOUNT CREATION ═══
def _create_student_accounts_background(student_records):
    """Create student login accounts in background thread.
    Uses fast MD5 hashing for bulk creation, not bcrypt."""
    import django
    django.setup()

    for sr in student_records:
        if sr.user_id:
            continue
        uname = sr.student_id.lower()
        if User.objects.filter(username=uname).exists():
            # Link existing
            try:
                u = User.objects.get(username=uname)
                sr.user = u
                sr.save(update_fields=['user'])
            except:
                pass
            continue
        pwd = User.generate_student_password(sr.student_id, sr.name)
        # Use MD5 for speed (student passwords are auto-generated, not user-chosen)
        from django.contrib.auth.hashers import MD5PasswordHasher
        hasher = MD5PasswordHasher()
        hashed = hasher.encode(pwd, hasher.salt())
        try:
            u = User.objects.create(
                username=uname, password=hashed, role='STUDENT',
                first_name=sr.name.split()[0] if sr.name else '',
                last_name=' '.join(sr.name.split()[1:]) if len(sr.name.split()) > 1 else '',
            )
            sr.user = u
            sr.save(update_fields=['user'])
        except:
            pass


# ═══ CREATE + ALLOCATE ═══
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_and_allocate_view(request):
    total_start = time_module.time()
    d = request.data

    # Date/time validation
    exam_date = d.get('exam_date'); tf = d.get('exam_time_from'); tt = d.get('exam_time_to')
    if not exam_date or not tf or not tt:
        return Response({'error': 'exam_date, exam_time_from, exam_time_to required.'}, status=400)
    try:
        ed = datetime.strptime(exam_date, '%Y-%m-%d').date()
        tf_t = datetime.strptime(tf, '%H:%M').time()
        tt_t = datetime.strptime(tt, '%H:%M').time()
    except:
        return Response({'error': 'Invalid date/time.'}, status=400)
    if tf_t >= tt_t:
        return Response({'error': 'From must be before To.'}, status=400)

    mode = d.get('mode', 'separate')

    # ── Load students and halls based on mode ──
    if mode == 'combined':
        csv_id = d.get('csv_id')
        if not csv_id:
            return Response({'error': 'csv_id required.'}, status=400)
        try:
            cu = CSVUpload.objects.get(pk=csv_id, csv_type='COMBINED')
        except:
            return Response({'error': 'Combined CSV not found.'}, status=404)

        qs = cu.students.all()
        hall_entries = cu.hall_entries.all()
        student_csv = cu
        hall_csv = cu
    else:
        student_csv_id = d.get('student_csv_id')
        hall_csv_id = d.get('hall_csv_id')
        if not student_csv_id:
            return Response({'error': 'student_csv_id required.'}, status=400)
        if not hall_csv_id:
            return Response({'error': 'hall_csv_id required.'}, status=400)
        try:
            s_csv = CSVUpload.objects.get(pk=student_csv_id, csv_type='STUDENTS')
        except:
            return Response({'error': 'Student CSV not found.'}, status=404)
        try:
            h_csv = CSVUpload.objects.get(pk=hall_csv_id, csv_type='HALLS')
        except:
            return Response({'error': 'Hall CSV not found.'}, status=404)

        qs = s_csv.students.all()
        hall_entries = h_csv.hall_entries.all()
        student_csv = s_csv
        hall_csv = h_csv

    # Apply filters
    sel_classes = d.get('selected_classes')
    if sel_classes:
        qs = qs.filter(student_class__in=sel_classes)
    sel_subjects = d.get('selected_subjects')
    if sel_subjects:
        qs = qs.filter(subject_code__in=sel_subjects)
    excluded = set(d.get('excluded_student_ids') or [])
    students = [s for s in qs if s.student_id not in excluded]
    if not students:
        return Response({'error': 'No students after filtering.'}, status=400)

    # Build halls
    halls_map = {}
    for he in hall_entries:
        halls_map[he.hall_id] = {'capacity': he.capacity, 'rows': he.rows, 'columns': he.columns}
    if not halls_map:
        return Response({'error': 'No halls.'}, status=400)

    # Collision checks
    hc = _check_hall_collision(list(halls_map.keys()), ed, tf_t, tt_t)
    if hc:
        return Response({'error': 'Hall conflict.', 'conflicts': hc}, status=409)
    sc = _check_student_collision([s.student_id for s in students], ed, tf_t, tt_t)
    if sc:
        return Response({'error': 'Student conflict.', 'conflicts': sc}, status=409)

    # ── Create session ──
    session_name = d.get('name', '') or student_csv.name
    session = AllocationSession.objects.create(
        name=session_name, student_csv=student_csv,
        hall_csv=hall_csv if hall_csv.id != student_csv.id else None,
        created_by=request.user, exam_date=ed, exam_time_from=tf_t, exam_time_to=tt_t,
        total_students=len(students), total_halls=len(halls_map),
        total_capacity=sum(h['capacity'] for h in halls_map.values()),
    )

    # Create hall DB objects
    hall_objs = {}
    for hid, hd in halls_map.items():
        h = Hall.objects.create(session=session, hall_id=hid,
                                capacity=hd['capacity'], rows=hd['rows'], columns=hd['columns'])
        hall_objs[hid] = h

    # Invigilators
    inv_map = d.get('hall_invigilators') or {}
    for hid, fids in inv_map.items():
        if hid in hall_objs:
            for fid in (fids if isinstance(fids, list) else [fids]):
                try:
                    fac = User.objects.get(pk=int(fid), role='FACULTY')
                    HallInvigilator.objects.create(session=session, hall=hall_objs[hid], faculty=fac)
                except:
                    pass

    # ── RUN ALLOCATION ENGINE ──
    halls_data = [
        {'hall_id': hid, 'capacity': hd['capacity'], 'rows': hd['rows'], 'columns': hd['columns']}
        for hid, hd in halls_map.items()
    ]
    students_data = [
        {'student_id': s.student_id, 'name': s.name, 'subject_code': s.subject_code, 'student_class': s.student_class}
        for s in students
    ]

    result = run_allocation(students_data, halls_data, pre_assigned=False)

    # ── Save allocations (bulk) ──
    stu_map = {s.student_id: s for s in students}
    alloc_objs = []
    for a in result.allocations:
        if a['student_id'] in stu_map and a['hall_id'] in hall_objs:
            alloc_objs.append(SeatAllocation(
                session=session, student=stu_map[a['student_id']],
                hall=hall_objs[a['hall_id']], row=a['row'], column=a['col'],
            ))
    SeatAllocation.objects.bulk_create(alloc_objs)

    # Save violations (bulk)
    viol_objs = []
    for v in result.violations:
        viol_objs.append(ConstraintViolation(
            session=session, violation_type=v['type'], description=v['description'],
            student_id_ref=v.get('student_id', ''), hall_id_ref=v.get('hall_id', ''),
            row=v.get('row'), column=v.get('col'),
        ))
    if viol_objs:
        ConstraintViolation.objects.bulk_create(viol_objs)

    # ── Total time (before account creation) ──
    total_ms = round((time_module.time() - total_start) * 1000, 2)

    # Update session
    session.allocated_count = len(result.allocations)
    session.unallocated_count = len(result.unallocated)
    session.allocation_time_ms = total_ms
    session.warnings = result.warnings
    session.save()

    # ── Create student accounts in BACKGROUND (don't block response) ──
    student_ids_allocated = [a['student_id'] for a in result.allocations]
    records_needing_accounts = list(
        StudentRecord.objects.filter(student_id__in=student_ids_allocated, user__isnull=True)
    )
    if records_needing_accounts:
        thread = threading.Thread(
            target=_create_student_accounts_background,
            args=(records_needing_accounts,),
            daemon=True,
        )
        thread.start()

    return Response({
        'session_id': session.id,
        'status': 'ALLOCATED',
        'allocated': len(result.allocations),
        'unallocated': len(result.unallocated),
        'warnings': result.warnings,
        'time_ms': total_ms,
        'hall_assignments': {hid: len(sids) for hid, sids in result.hall_assignments.items()},
    }, status=201)


# ═══ SESSION OPS ═══
@api_view(['POST'])
@permission_classes([IsAdmin])
def complete_session_view(request, session_id):
    try: s = AllocationSession.objects.get(pk=session_id)
    except: return Response({'error': 'Not found.'}, status=404)
    if s.status == 'COMPLETED':
        return Response({'error': 'Already completed.'}, status=400)
    s.status = 'COMPLETED'; s.save()
    return Response({'message': 'Completed.'})

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def session_list_view(request):
    qs = AllocationSession.objects.all()
    if request.user.role == 'FACULTY':
        qs = qs.filter(id__in=HallInvigilator.objects.filter(faculty=request.user).values_list('session_id', flat=True))
    return Response(SessionListSerializer(qs, many=True).data)

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def session_detail_view(request, session_id):
    try: s = AllocationSession.objects.get(pk=session_id)
    except: return Response({'error': 'Not found.'}, status=404)
    if request.user.role == 'FACULTY' and not HallInvigilator.objects.filter(session=s, faculty=request.user).exists():
        return Response({'error': 'Not assigned.'}, status=403)
    return Response(SessionDetailSerializer(s).data)

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_session_view(request, session_id):
    try: s = AllocationSession.objects.get(pk=session_id)
    except: return Response({'error': 'Not found.'}, status=404)
    s.delete()
    return Response({'message': 'Deleted.'})

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def hall_layout_view(request, session_id, hall_pk):
    try:
        session = AllocationSession.objects.get(pk=session_id)
        hall = session.halls.get(pk=hall_pk)
    except:
        return Response({'error': 'Not found.'}, status=404)
    allocs = session.allocations.filter(hall=hall).select_related('student')
    grid = [[None] * hall.columns for _ in range(hall.rows)]
    for a in allocs:
        grid[a.row][a.column] = {
            'student_id': a.student.student_id, 'name': a.student.name,
            'subject_code': a.student.subject_code, 'student_class': a.student.student_class,
        }
    invs = [{'id': i.faculty.id, 'name': i.faculty.get_full_name() or i.faculty.username}
            for i in hall.invigilators.select_related('faculty')]
    return Response({
        'hall_id': hall.hall_id, 'rows': hall.rows, 'columns': hall.columns,
        'capacity': hall.capacity, 'occupied': allocs.count(),
        'grid': grid, 'invigilators': invs,
    })


# ═══ EXPORTS ═══
@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def export_csv_view(request, session_id):
    try: s = AllocationSession.objects.get(pk=session_id)
    except: return Response({'error': 'Not found.'}, status=404)
    resp = HttpResponse(generate_csv_report(s), content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="allocation_{session_id}.csv"'
    return resp

@api_view(['GET'])
@permission_classes([IsAdminOrFaculty])
def export_pdf_view(request, session_id):
    try: s = AllocationSession.objects.get(pk=session_id)
    except: return Response({'error': 'Not found.'}, status=404)
    buf = generate_pdf_seating_chart(s)
    resp = HttpResponse(buf.read(), content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="seating_{session_id}.pdf"'
    return resp


# ═══ DASHBOARD ═══
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    if request.user.role == 'ADMIN':
        ss = AllocationSession.objects.all()
        return Response({
            'total_sessions': ss.count(),
            'allocated': ss.filter(status='ALLOCATED').count(),
            'completed': ss.filter(status='COMPLETED').count(),
            'total_students': StudentRecord.objects.count(),
            'total_csvs': CSVUpload.objects.count(),
            'faculty_count': User.objects.filter(role='FACULTY').count(),
            'subjects': list(StudentRecord.objects.values_list('subject_code', flat=True).distinct()),
        })
    elif request.user.role == 'FACULTY':
        assigned = HallInvigilator.objects.filter(faculty=request.user).select_related('session', 'hall')
        sids = set(); duties = []
        for inv in assigned:
            sids.add(inv.session.id)
            duties.append({
                'session_id': inv.session.id, 'session_name': inv.session.name,
                'session_status': inv.session.status,
                'exam_date': inv.session.exam_date_str, 'exam_time': inv.session.exam_time_str,
                'hall_id': inv.hall.hall_id, 'hall_pk': inv.hall.pk,
                'hall_capacity': inv.hall.capacity,
            })
        return Response({
            'total_assigned': len(sids),
            'allocated': AllocationSession.objects.filter(id__in=sids, status='ALLOCATED').count(),
            'completed': AllocationSession.objects.filter(id__in=sids, status='COMPLETED').count(),
            'duties': duties,
        })
    return Response({})


# ═══ STUDENT SELF ═══
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_allocations_view(request):
    if request.user.role != 'STUDENT':
        return Response({'error': 'Students only.'}, status=403)
    sr = StudentRecord.objects.filter(user=request.user).first()
    if not sr:
        return Response({'student_id': request.user.username, 'name': '', 'allocations': []})
    allocs = SeatAllocation.objects.filter(student=sr).select_related('hall', 'session')
    return Response({
        'student_id': sr.student_id, 'name': sr.name,
        'subject_code': sr.subject_code, 'student_class': sr.student_class,
        'allocations': [{
            'session_id': a.session.id, 'session_name': a.session.name,
            'session_status': a.session.status, 'hall_id': a.hall.hall_id,
            'hall_pk': a.hall.pk, 'row': a.row + 1, 'column': a.column + 1,
            'subject_code': sr.subject_code,
            'exam_date': a.session.exam_date_str, 'exam_time': a.session.exam_time_str,
        } for a in allocs],
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_hall_layout_view(request, session_id, hall_pk):
    if request.user.role != 'STUDENT':
        return Response({'error': 'Students only.'}, status=403)
    sr = StudentRecord.objects.filter(user=request.user).first()
    if not sr:
        return Response({'error': 'No profile.'}, status=404)
    if not SeatAllocation.objects.filter(student=sr, session_id=session_id).exists():
        return Response({'error': 'Not allocated.'}, status=403)
    try:
        hall = Hall.objects.get(pk=hall_pk, session_id=session_id)
    except:
        return Response({'error': 'Not found.'}, status=404)
    allocs = SeatAllocation.objects.filter(session_id=session_id, hall=hall).select_related('student')
    grid = [[None] * hall.columns for _ in range(hall.rows)]
    for a in allocs:
        grid[a.row][a.column] = {
            'student_id': a.student.student_id, 'name': a.student.name,
            'subject_code': a.student.subject_code, 'student_class': a.student.student_class,
        }
    return Response({
        'hall_id': hall.hall_id, 'rows': hall.rows, 'columns': hall.columns,
        'capacity': hall.capacity, 'occupied': allocs.count(),
        'grid': grid, 'my_student_id': sr.student_id,
    })