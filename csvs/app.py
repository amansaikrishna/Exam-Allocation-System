#!/usr/bin/env python3
"""Generate test CSVs — separate students + halls files."""
import csv, os, random

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_data')
os.makedirs(OUTPUT, exist_ok=True)

FIRSTS = ["Aarav","Aditi","Aditya","Akash","Ananya","Arjun","Bhavya","Chaitanya","Deepika","Dhruv","Divya","Esha","Farhan","Gayatri","Harsha","Ishaan","Jaya","Karthik","Lakshmi","Manish","Navya","Nikhil","Priya","Pranav","Pooja","Rahul","Riya","Rohit","Sakshi","Sanjay","Shreya","Siddharth","Sneha","Suresh","Swati","Tanvi","Tushar","Uma","Varun","Vidya","Ajay","Anita","Arun","Bindu","Chandra","Devi","Ganesh","Hari","Indira","Jagdish","Kavitha","Kishore","Lalitha","Mohan","Nandini","Om","Padma","Rajesh","Rekha","Sathish","Amit","Brinda","Chirag","Disha","Ekansh","Falguni","Gaurav","Harini","Ishan","Juhi","Kunal","Lavanya","Mukesh","Neha","Omkar","Pallavi","Qadir","Roshni","Sagar","Tanya"]
LASTS = ["Sharma","Verma","Patel","Reddy","Gupta","Nair","Singh","Rao","Joshi","Kumar","Menon","Pandey","Ahmed","Iyer","Desai","Mehta","Kulkarni","Bhat","Pillai","Tiwari","Saxena","Chopra","Agarwal","Mishra","Shetty","Kapoor","Dutta","Bansal","Trivedi","Hegde","Chauhan","Jain","Prasad","Naik","Bose","Malhotra","Ghosh","Shankar","Sinha","Raman"]
BRANCHES = [
    {'code':'CS101','series':5100,'class':'1st Year CSE'},
    {'code':'EC101','series':4100,'class':'1st Year ECE'},
    {'code':'EE101','series':3100,'class':'1st Year EEE'},
    {'code':'ME101','series':2100,'class':'1st Year MECH'},
    {'code':'CV101','series':1100,'class':'1st Year CIVIL'},
]
def rn(): return f"{random.choice(FIRSTS)} {random.choice(LASTS)}"
def roll(ser, seq): return f"25001D{ser+seq}"
def wcsv(fn, hdr, rows):
    p = os.path.join(OUTPUT, fn)
    with open(p,'w',newline='') as f: w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
    print(f"  ✅ {fn}: {len(rows)} rows")

print("="*50)
print("🎓 ExamAlloc CSV Generator")
print("="*50)

# ─── 1: Students 1000 ───
print("\n📄 students_1000.csv")
rows = []
for b in BRANCHES:
    for i in range(1,201): rows.append([roll(b['series'],i), rn(), b['code'], b['class']])
random.shuffle(rows)
wcsv('students_1000.csv', ['student_id','name','subject_code','class'], rows)

# ─── 2: Halls 20×50 ───
print("\n📄 halls_20x50.csv")
rows = [[f"H{i:03d}",50,5,10] for i in range(1,21)]
wcsv('halls_20x50.csv', ['hall_id','capacity','rows','columns'], rows)

# ─── 3: Halls mixed sizes ───
print("\n📄 halls_mixed.csv")
rows = [['AUDI-1',100,10,10],['AUDI-2',100,10,10],['LAB-1',50,5,10],['LAB-2',50,5,10],['LAB-3',50,5,10],
    ['CR-101',40,5,8],['CR-102',40,5,8],['CR-103',40,5,8],['CR-104',40,5,8],['CR-105',40,5,8],
    ['EXAM-1',60,6,10],['EXAM-2',60,6,10],['EXAM-3',60,6,10]]
wcsv('halls_mixed.csv', ['hall_id','capacity','rows','columns'], rows)

# ─── 4: Halls small (overflow test) ───
print("\n📄 halls_small_overflow.csv")
rows = [[f"SMALL-{i}",30,5,6] for i in range(1,6)]
wcsv('halls_small_overflow.csv', ['hall_id','capacity','rows','columns'], rows)

# ─── 5: Students 100 same class ───
print("\n📄 students_100_same.csv")
rows = [[roll(5100,i), rn(), 'CS101', '1st Year CSE'] for i in range(1,101)]
wcsv('students_100_same.csv', ['student_id','name','subject_code','class'], rows)

# ─── 6: Halls 2×50 ───
print("\n📄 halls_2x50.csv")
wcsv('halls_2x50.csv', ['hall_id','capacity','rows','columns'], [['HALL-A',50,5,10],['HALL-B',50,5,10]])

# ─── ERROR CSVs ───
print("\n📄 error_students_duplicates.csv")
rows = [[roll(5100,i),rn(),'CS101','1st Year CSE'] for i in range(1,21)]
rows.append([roll(5100,1),'Dup One','CS101','1st Year CSE'])
rows.append([roll(5100,5),'Dup Five','CS101','1st Year CSE'])
wcsv('error_students_duplicates.csv', ['student_id','name','subject_code','class'], rows)

print("\n📄 error_students_missing.csv")
rows = [['','No ID','CS101','X'],['25001D5102','','CS101','X'],['25001D5103','No Sub','','X'],[roll(5100,4),rn(),'CS101','OK']]
wcsv('error_students_missing.csv', ['student_id','name','subject_code','class'], rows)

print("\n📄 error_halls_duplicates.csv")
wcsv('error_halls_duplicates.csv', ['hall_id','capacity','rows','columns'], [['H001',50,5,10],['H002',40,5,8],['H001',60,6,10]])

print("\n📄 error_halls_bad_capacity.csv")
wcsv('error_halls_bad_capacity.csv', ['hall_id','capacity'], [['H001',50],['H002',0],['H003',-10],['H004','abc']])

print("\n📄 error_halls_missing_columns.csv")
wcsv('error_halls_missing_columns.csv', ['hall_id','description'], [['H001','A hall']])

# ─── Combined CSVs (backward compat) ───
print("\n📄 combined_200.csv")
rows = []
for b in BRANCHES:
    for i in range(1,21): rows.append([roll(b['series'],i),rn(),b['code'],'H001' if i<=10 else 'H002',50,'1st Year '+b['code'][:2]+'E'])
random.shuffle(rows)
wcsv('combined_200.csv', ['student_id','name','subject_code','hall_id','hall_capacity','class'], rows)

print("\n" + "="*50)
print(f"📁 All in: {OUTPUT}")
print("="*50)
print("""
USAGE:
─────────────────────────────────────
SEPARATE MODE (recommended):
  Students: students_1000.csv
  Halls:    halls_20x50.csv  or  halls_mixed.csv

OVERFLOW TEST:
  Students: students_1000.csv
  Halls:    halls_small_overflow.csv  (150 seats for 1000 → 850 unallocated!)

SAME CLASS TEST:
  Students: students_100_same.csv
  Halls:    halls_2x50.csv

COMBINED MODE:
  combined_200.csv

ERROR FILES (should all fail):
  error_students_duplicates.csv
  error_students_missing.csv
  error_halls_duplicates.csv
  error_halls_bad_capacity.csv
  error_halls_missing_columns.csv
""")
