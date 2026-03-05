import re, math
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    ROLE_CHOICES = [('ADMIN','Admin'),('FACULTY','Faculty'),('STUDENT','Student')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=20, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['username']

    @staticmethod
    def generate_student_password(student_id, name):
        clean = re.sub(r'\s+', '', name).lower()
        return f"{student_id.lower()}@{clean[:4]}"


class CSVUpload(models.Model):
    TYPE_CHOICES = [('STUDENTS','Students'),('HALLS','Halls'),('COMBINED','Combined')]
    name = models.CharField(max_length=200)
    filename = models.CharField(max_length=300)
    csv_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='COMBINED')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.csv_type})"

    @property
    def student_count(self):
        return self.students.count()

    @property
    def hall_count(self):
        return self.hall_entries.count()


class StudentRecord(models.Model):
    csv_upload = models.ForeignKey(CSVUpload, on_delete=models.CASCADE, related_name='students')
    student_id = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=50, db_index=True)
    student_class = models.CharField(max_length=50, blank=True, default='', db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['student_id']
        unique_together = [('csv_upload', 'student_id')]

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class HallEntry(models.Model):
    """Hall data from CSV upload."""
    csv_upload = models.ForeignKey(CSVUpload, on_delete=models.CASCADE, related_name='hall_entries')
    hall_id = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    rows = models.PositiveIntegerField(default=0)
    columns = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('csv_upload', 'hall_id')]
        ordering = ['hall_id']

    def save(self, *args, **kwargs):
        if (not self.rows or not self.columns) and self.capacity > 0:
            self.columns = math.ceil(math.sqrt(self.capacity))
            self.rows = math.ceil(self.capacity / self.columns)
        super().save(*args, **kwargs)


class AllocationSession(models.Model):
    STATUS_CHOICES = [('ALLOCATED','Allocated'),('COMPLETED','Completed')]
    name = models.CharField(max_length=200)
    student_csv = models.ForeignKey(CSVUpload, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions_as_students')
    hall_csv = models.ForeignKey(CSVUpload, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions_as_halls')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ALLOCATED')
    exam_date = models.DateField()
    exam_time_from = models.TimeField()
    exam_time_to = models.TimeField()
    total_students = models.IntegerField(default=0)
    total_halls = models.IntegerField(default=0)
    total_capacity = models.IntegerField(default=0)
    allocated_count = models.IntegerField(default=0)
    unallocated_count = models.IntegerField(default=0)
    allocation_time_ms = models.FloatField(null=True, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def exam_date_str(self):
        return self.exam_date.strftime('%d-%m-%Y') if self.exam_date else ''

    @property
    def exam_time_str(self):
        parts = []
        if self.exam_time_from: parts.append(self.exam_time_from.strftime('%I:%M %p'))
        if self.exam_time_to: parts.append(self.exam_time_to.strftime('%I:%M %p'))
        return ' — '.join(parts)


class Hall(models.Model):
    session = models.ForeignKey(AllocationSession, on_delete=models.CASCADE, related_name='halls')
    hall_id = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    rows = models.PositiveIntegerField(default=0)
    columns = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('session', 'hall_id')]
        ordering = ['hall_id']

    def save(self, *args, **kwargs):
        if (not self.rows or not self.columns) and self.capacity > 0:
            self.columns = math.ceil(math.sqrt(self.capacity))
            self.rows = math.ceil(self.capacity / self.columns)
        super().save(*args, **kwargs)


class SeatAllocation(models.Model):
    session = models.ForeignKey(AllocationSession, on_delete=models.CASCADE, related_name='allocations')
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='seat_allocations')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='allocations')
    row = models.PositiveIntegerField()
    column = models.PositiveIntegerField()

    class Meta:
        unique_together = [('session', 'student'), ('session', 'hall', 'row', 'column')]
        ordering = ['hall', 'row', 'column']


class HallInvigilator(models.Model):
    session = models.ForeignKey(AllocationSession, on_delete=models.CASCADE, related_name='invigilators')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='invigilators')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invigilation_duties')

    class Meta:
        unique_together = [('session', 'hall', 'faculty')]


class ConstraintViolation(models.Model):
    TYPES = [('ADJACENT_SAME_SUBJECT','Adjacent Same Subject'),('UNALLOCATED','Unallocated')]
    session = models.ForeignKey(AllocationSession, on_delete=models.CASCADE, related_name='violations')
    violation_type = models.CharField(max_length=30, choices=TYPES)
    description = models.TextField()
    student_id_ref = models.CharField(max_length=50, blank=True, default='')
    hall_id_ref = models.CharField(max_length=50, blank=True, default='')
    row = models.PositiveIntegerField(null=True, blank=True)
    column = models.PositiveIntegerField(null=True, blank=True)