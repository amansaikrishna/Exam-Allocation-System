import time
from collections import defaultdict


class AllocationResult:
    def __init__(self):
        self.allocations = []      # [{student_id, hall_id, row, col}]
        self.unallocated = []      # [student_id]
        self.violations = []       # [{type, description, ...}]
        self.hall_assignments = {} # {hall_id: [student_ids]}
        self.time_ms = 0.0
        self.warnings = []


def run_allocation(students, halls, pre_assigned=False):
    """
    If pre_assigned=True: students already have hall_id assigned (combined CSV mode).
    If pre_assigned=False: system assigns students to halls, then seats them.
    """
    start = time.time()
    result = AllocationResult()

    if not students:
        result.warnings.append("No students to allocate.")
        return result
    if not halls:
        result.warnings.append("No halls available.")
        result.unallocated = [s['student_id'] for s in students]
        for s in students:
            result.violations.append({
                'type':'UNALLOCATED', 'description':f"{s['student_id']} — no halls.",
                'student_id':s['student_id'], 'hall_id':'', 'row':None, 'col':None,
            })
        return result

    total_cap = sum(h['capacity'] for h in halls)
    if len(students) > total_cap:
        result.warnings.append(f"Students ({len(students)}) exceed capacity ({total_cap}). {len(students)-total_cap} will be unallocated.")

    if pre_assigned:
        # Combined CSV mode: students already mapped to halls
        hall_map = {h['hall_id']: [] for h in halls}
        leftover = []
        for s in students:
            hid = s.get('hall_id', '')
            if hid in hall_map:
                hall_map[hid].append(s)
            else:
                leftover.append(s)
        if leftover:
            result.warnings.append(f"{len(leftover)} students have unknown hall_id.")
        # Seat each hall
        for hall in sorted(halls, key=lambda h: h['capacity'], reverse=True):
            hid = hall['hall_id']
            stu_list = hall_map.get(hid, [])
            if not stu_list:
                continue
            _seat_hall(hall, stu_list, result)
        for s in leftover:
            result.unallocated.append(s['student_id'])
            result.violations.append({
                'type':'UNALLOCATED', 'description':f"{s['student_id']} — hall not found.",
                'student_id':s['student_id'], 'hall_id':'', 'row':None, 'col':None,
            })
    else:
        # SMART HALL ALLOCATION: assign students to halls maximizing subject separation
        assignments = _assign_students_to_halls(students, halls)
        for hall in sorted(halls, key=lambda h: h['capacity'], reverse=True):
            hid = hall['hall_id']
            stu_list = assignments.get(hid, [])
            if not stu_list:
                continue
            _seat_hall(hall, stu_list, result)
        # Handle unassigned
        assigned_ids = set()
        for hid, slist in assignments.items():
            for s in slist:
                assigned_ids.add(s['student_id'])
        for s in students:
            if s['student_id'] not in assigned_ids:
                result.unallocated.append(s['student_id'])
                result.violations.append({
                    'type':'UNALLOCATED', 'description':f"{s['student_id']} ({s['subject_code']}) — no capacity.",
                    'student_id':s['student_id'], 'hall_id':'', 'row':None, 'col':None,
                })

    result.time_ms = round((time.time() - start) * 1000, 2)

    # Build hall_assignments summary
    for a in result.allocations:
        hid = a['hall_id']
        if hid not in result.hall_assignments:
            result.hall_assignments[hid] = []
        result.hall_assignments[hid].append(a['student_id'])

    return result


def _assign_students_to_halls(students, halls):
    """
    Smart hall allocation:
    1. Group students by subject
    2. Distribute subjects across halls round-robin
    3. Within each subject, spread same-class students
    4. Maximize subject mixing per hall
    """
    # Group by subject
    by_subject = defaultdict(list)
    for s in students:
        by_subject[s['subject_code']].append(s)

    subject_keys = sorted(by_subject.keys(), key=lambda k: len(by_subject[k]), reverse=True)

    # Within each subject, spread classes apart
    for key in subject_keys:
        by_subject[key] = _spread_by_class(by_subject[key])

    # Sort halls by capacity descending
    sorted_halls = sorted(halls, key=lambda h: h['capacity'], reverse=True)
    hall_buckets = {h['hall_id']: {'cap': h['capacity'], 'students': [], 'subject_counts': defaultdict(int)} for h in sorted_halls}

    # Round-robin distribute: for each subject, place students one at a time
    # into the hall with the LEAST of that subject (for max mixing)
    all_students_queue = []
    queues = [list(by_subject[k]) for k in subject_keys if by_subject[k]]
    while queues:
        nxt = []
        for q in queues:
            if q:
                all_students_queue.append(q.pop(0))
            if q:
                nxt.append(q)
        queues = nxt

    for stu in all_students_queue:
        subj = stu['subject_code']
        # Find hall with: space remaining AND least count of this subject
        best_hall = None
        best_score = float('inf')
        for h in sorted_halls:
            hid = h['hall_id']
            bucket = hall_buckets[hid]
            remaining = bucket['cap'] - len(bucket['students'])
            if remaining <= 0:
                continue
            # Score: lower = better. Prefer halls with fewer of this subject.
            subj_count = bucket['subject_counts'][subj]
            total_in_hall = len(bucket['students'])
            # Tie-break: prefer halls with more remaining space
            score = (subj_count * 1000) - remaining
            if score < best_score:
                best_score = score
                best_hall = hid
        if best_hall:
            hall_buckets[best_hall]['students'].append(stu)
            hall_buckets[best_hall]['subject_counts'][subj] += 1

    return {hid: bucket['students'] for hid, bucket in hall_buckets.items()}


def _seat_hall(hall, students, result):
    """Seat students within a single hall with subject separation."""
    rows = hall['rows']
    cols = hall['columns']
    cap = hall['capacity']

    # Interleave by subject for this hall
    by_subj = defaultdict(list)
    for s in students:
        by_subj[s['subject_code']].append(s)
    subj_keys = sorted(by_subj.keys(), key=lambda k: len(by_subj[k]), reverse=True)
    for k in subj_keys:
        by_subj[k] = _spread_by_class(by_subj[k])
    interleaved = _round_robin(subj_keys, by_subj)

    grid = [[None] * cols for _ in range(rows)]
    idx = 0
    filled = 0

    for r, c in _snake_order(rows, cols):
        if filled >= cap or idx >= len(interleaved):
            break

        best_idx = idx
        best_score = _score(grid, r, c, interleaved[idx], rows, cols)

        if best_score > 0:
            for off in range(1, min(100, len(interleaved) - idx)):
                sc = _score(grid, r, c, interleaved[idx + off], rows, cols)
                if sc < best_score:
                    best_score = sc
                    best_idx = idx + off
                if sc == 0:
                    break
            if best_idx != idx:
                interleaved[idx], interleaved[best_idx] = interleaved[best_idx], interleaved[idx]

        stu = interleaved[idx]
        grid[r][c] = stu
        result.allocations.append({
            'student_id': stu['student_id'],
            'hall_id': hall['hall_id'],
            'row': r, 'col': c,
        })
        idx += 1
        filled += 1

    # Remaining = unallocated from this hall
    for s in interleaved[idx:]:
        result.unallocated.append(s['student_id'])
        result.violations.append({
            'type': 'UNALLOCATED',
            'description': f"{s['student_id']} ({s['subject_code']}) — hall {hall['hall_id']} full.",
            'student_id': s['student_id'], 'hall_id': hall['hall_id'],
            'row': None, 'col': None,
        })


def _spread_by_class(students):
    by_class = defaultdict(list)
    for s in students:
        by_class[s.get('student_class', '') or s.get('class', '')].append(s)
    keys = sorted(by_class.keys(), key=lambda k: len(by_class[k]), reverse=True)
    return _round_robin(keys, by_class)


def _round_robin(keys, groups):
    queues = [list(groups[k]) for k in keys if groups[k]]
    out = []
    while queues:
        nxt = []
        for q in queues:
            if q: out.append(q.pop(0))
            if q: nxt.append(q)
        queues = nxt
    return out


def _snake_order(rows, cols):
    for r in range(rows):
        rng = range(cols) if r % 2 == 0 else range(cols - 1, -1, -1)
        for c in rng:
            yield r, c


def _score(grid, r, c, student, rows, cols):
    subj = student['subject_code']
    cls = student.get('student_class', '') or student.get('class', '')
    key = f"{subj}|{cls}"
    score = 0
    for nr, nc in [(r, c-1), (r, c+1), (r-1, c), (r+1, c)]:
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
            n = grid[nr][nc]
            if n['subject_code'] == subj:
                score += 10
                n_cls = n.get('student_class', '') or n.get('class', '')
                if f"{n['subject_code']}|{n_cls}" == key:
                    score += 5
    return score