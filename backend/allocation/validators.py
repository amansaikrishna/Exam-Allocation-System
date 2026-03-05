import csv, io, math


def validate_students_csv(file_content):
    """Parse student CSV: student_id, name, subject_code, [class]"""
    students = []
    errors = []
    warnings = []
    seen = {}

    try:
        reader = csv.DictReader(io.StringIO(file_content))
    except Exception as e:
        return {'students': [], 'errors': [f"CSV error: {e}"], 'warnings': []}

    if not reader.fieldnames:
        return {'students': [], 'errors': ["Empty CSV."], 'warnings': []}

    hmap = {f: f.strip().lower().replace(' ', '_') for f in reader.fieldnames}
    aliases = {'student_name':'name','roll_no':'student_id','roll_number':'student_id',
               'rollno':'student_id','subject':'subject_code','student_class':'class'}
    for k, v in list(hmap.items()):
        if v in aliases: hmap[k] = aliases[v]
    norm = set(hmap.values())

    required = {'student_id', 'name', 'subject_code'}
    miss = required - norm
    if miss:
        return {'students':[], 'errors':[f"Missing columns: {', '.join(sorted(miss))}. Found: {', '.join(sorted(norm))}"], 'warnings':[]}

    for i, raw in enumerate(reader, start=2):
        row = {hmap[k]: (v.strip() if v else '') for k, v in raw.items()}
        sid = row.get('student_id','')
        name = row.get('name','')
        subject = row.get('subject_code','')
        sclass = row.get('class','')

        if not sid: errors.append(f"Row {i}: Missing student_id."); continue
        if not name: errors.append(f"Row {i}: Missing name for '{sid}'."); continue
        if not subject: errors.append(f"Row {i}: Missing subject_code for '{sid}'."); continue
        if sid in seen:
            errors.append(f"Row {i}: Duplicate student '{sid}' (first at row {seen[sid]})."); continue
        seen[sid] = i
        students.append({'student_id':sid, 'name':name, 'subject_code':subject, 'class':sclass})

    if not students and not errors:
        errors.append("No data rows found.")

    return {'students': students, 'errors': errors, 'warnings': warnings}


def validate_halls_csv(file_content):
    """Parse halls CSV: hall_id, capacity, [rows, columns]"""
    halls = []
    errors = []
    warnings = []
    seen = {}

    try:
        reader = csv.DictReader(io.StringIO(file_content))
    except Exception as e:
        return {'halls': [], 'errors': [f"CSV error: {e}"], 'warnings': []}

    if not reader.fieldnames:
        return {'halls': [], 'errors': ["Empty CSV."], 'warnings': []}

    hmap = {f: f.strip().lower().replace(' ', '_') for f in reader.fieldnames}
    aliases = {'hall':'hall_id','hall_name':'hall_id','name':'hall_id',
               'cap':'capacity','hall_capacity':'capacity',
               'hall_rows':'rows','hall_columns':'columns','cols':'columns'}
    for k, v in list(hmap.items()):
        if v in aliases: hmap[k] = aliases[v]
    norm = set(hmap.values())

    required = {'hall_id', 'capacity'}
    miss = required - norm
    if miss:
        return {'halls':[], 'errors':[f"Missing columns: {', '.join(sorted(miss))}. Found: {', '.join(sorted(norm))}"], 'warnings':[]}

    for i, raw in enumerate(reader, start=2):
        row = {hmap[k]: (v.strip() if v else '') for k, v in raw.items()}
        hid = row.get('hall_id','')
        cap_str = row.get('capacity','')

        if not hid: errors.append(f"Row {i}: Missing hall_id."); continue
        if not cap_str: errors.append(f"Row {i}: Missing capacity for '{hid}'."); continue
        try:
            cap = int(cap_str)
            if cap <= 0: raise ValueError()
        except: errors.append(f"Row {i}: Invalid capacity '{cap_str}' for '{hid}'."); continue

        if hid in seen:
            errors.append(f"Row {i}: Duplicate hall '{hid}' (first at row {seen[hid]})."); continue
        seen[hid] = i

        r_str = row.get('rows','')
        c_str = row.get('columns','')
        try: r = int(r_str) if r_str else 0
        except: r = 0
        try: c = int(c_str) if c_str else 0
        except: c = 0

        if r <= 0 or c <= 0:
            c = math.ceil(math.sqrt(cap))
            r = math.ceil(cap / c)
        if r * c < cap:
            warnings.append(f"Hall '{hid}': {r}×{c}={r*c} < capacity {cap}. Auto-adjusting.")
            c = math.ceil(math.sqrt(cap))
            r = math.ceil(cap / c)

        halls.append({'hall_id':hid, 'capacity':cap, 'rows':r, 'columns':c})

    if not halls and not errors:
        errors.append("No data rows found.")

    return {'halls': halls, 'errors': errors, 'warnings': warnings}


def validate_combined_csv(file_content):
    """Parse old-style combined CSV: student_id, name, subject_code, hall_id, hall_capacity, [class, rows, columns]"""
    students = []
    halls = {}
    errors = []
    warnings = []
    seen_ids = {}
    hall_students = {}
    hall_caps = {}

    try:
        reader = csv.DictReader(io.StringIO(file_content))
    except Exception as e:
        return {'students':[], 'halls':{}, 'errors':[f"CSV error: {e}"], 'warnings':[]}

    if not reader.fieldnames:
        return {'students':[], 'halls':{}, 'errors':["Empty CSV."], 'warnings':[]}

    hmap = {f: f.strip().lower().replace(' ', '_') for f in reader.fieldnames}
    aliases = {'student_name':'name','roll_no':'student_id','roll_number':'student_id',
               'rollno':'student_id','subject':'subject_code','hall':'hall_id',
               'cap':'hall_capacity','capacity':'hall_capacity','student_class':'class',
               'hall_rows':'rows','hall_columns':'columns','cols':'columns'}
    for k, v in list(hmap.items()):
        if v in aliases: hmap[k] = aliases[v]
    norm = set(hmap.values())

    required = {'student_id','name','subject_code','hall_id','hall_capacity'}
    miss = required - norm
    if miss:
        return {'students':[], 'halls':{}, 'errors':[f"Missing columns: {', '.join(sorted(miss))}"], 'warnings':[]}

    valid_rows = []
    for i, raw in enumerate(reader, start=2):
        row = {hmap.get(k,k): (v.strip() if v else '') for k, v in raw.items()}
        sid = row.get('student_id',''); name = row.get('name','')
        subject = row.get('subject_code',''); hall_id = row.get('hall_id','')
        cap_str = row.get('hall_capacity',''); sclass = row.get('class','')

        if not sid: errors.append(f"Row {i}: Missing student_id."); continue
        if not name: errors.append(f"Row {i}: Missing name for '{sid}'."); continue
        if not subject: errors.append(f"Row {i}: Missing subject_code for '{sid}'."); continue
        if not hall_id: errors.append(f"Row {i}: Missing hall_id for '{sid}'."); continue
        if not cap_str: errors.append(f"Row {i}: Missing hall_capacity for '{sid}'."); continue
        try:
            cap = int(cap_str)
            if cap <= 0: raise ValueError()
        except: errors.append(f"Row {i}: Invalid hall_capacity '{cap_str}' for '{sid}'."); continue

        if sid in seen_ids:
            prev = seen_ids[sid]
            if prev['hall_id'] == hall_id:
                errors.append(f"Row {i}: Duplicate student '{sid}' (row {prev['row']}).")
            else:
                errors.append(f"Row {i}: Student '{sid}' in hall '{hall_id}' but already in '{prev['hall_id']}' (row {prev['row']}).")
            continue
        seen_ids[sid] = {'row':i, 'hall_id':hall_id}

        if hall_id not in hall_caps: hall_caps[hall_id] = set()
        hall_caps[hall_id].add(cap)
        hall_students[hall_id] = hall_students.get(hall_id, 0) + 1

        hr_str = row.get('rows',''); hc_str = row.get('columns','')
        try: hr = int(hr_str) if hr_str else 0
        except: hr = 0
        try: hc = int(hc_str) if hc_str else 0
        except: hc = 0

        valid_rows.append({'student_id':sid,'name':name,'subject_code':subject,'hall_id':hall_id,
                           'hall_capacity':cap,'class':sclass,'hall_rows':hr,'hall_columns':hc})

    for hid, caps in hall_caps.items():
        if len(caps) > 1:
            errors.append(f"Hall '{hid}': Conflicting capacities {sorted(caps)}.")
    if len(hall_students) > 1:
        for hid, cnt in hall_students.items():
            if cnt == 1: errors.append(f"Hall '{hid}': Only 1 student — likely a typo.")
            elif cnt == 2: warnings.append(f"Hall '{hid}': Only 2 students — verify.")

    if errors:
        return {'students':[], 'halls':{}, 'errors':errors, 'warnings':warnings}

    import math
    for r in valid_rows:
        hid = r['hall_id']
        if hid not in halls:
            cap = r['hall_capacity']; hr = r.get('hall_rows',0); hc = r.get('hall_columns',0)
            if hr <= 0 or hc <= 0:
                hc = math.ceil(math.sqrt(cap)); hr = math.ceil(cap/hc)
            halls[hid] = {'capacity':cap, 'rows':hr, 'columns':hc}

    students = [{'student_id':r['student_id'],'name':r['name'],'subject_code':r['subject_code'],
                 'hall_id':r['hall_id'],'hall_capacity':r['hall_capacity'],'class':r['class']}
                for r in valid_rows]

    return {'students':students, 'halls':halls, 'errors':errors, 'warnings':warnings}