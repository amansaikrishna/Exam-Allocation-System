from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user: raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user; return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','role','phone','department','bio','date_joined']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','first_name','last_name','phone','department','bio']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=4)
    def validate_old_password(self, v):
        if not self.context['request'].user.check_password(v): raise serializers.ValidationError("Wrong.")
        return v

class StudentRecordSerializer(serializers.ModelSerializer):
    csv_name = serializers.CharField(source='csv_upload.name', default='')
    csv_id = serializers.IntegerField(source='csv_upload.id', default=None)
    allocations = serializers.SerializerMethodField()

    class Meta:
        model = StudentRecord
        fields = ['id','student_id','name','subject_code','student_class','csv_name','csv_id','created_at','allocations']

    def get_allocations(self, obj):
        # Return ALL allocations, not just 5
        allocs = SeatAllocation.objects.filter(student=obj).select_related('hall','session').order_by('-session__exam_date')
        return [{
            'session_id': a.session.id,
            'session_name': a.session.name,
            'hall_id': a.hall.hall_id,
            'row': a.row + 1,
            'column': a.column + 1,
            'exam_date': a.session.exam_date_str,
            'exam_time': a.session.exam_time_str,
            'status': a.session.status,
        } for a in allocs]

class HallEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = HallEntry
        fields = ['id','hall_id','capacity','rows','columns']

class CSVUploadSerializer(serializers.ModelSerializer):
    student_count = serializers.ReadOnlyField()
    hall_count = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', default='')
    classes = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    def get_classes(self, obj):
        if obj.csv_type == 'HALLS': return []
        return sorted(set(obj.students.values_list('student_class',flat=True).distinct()) - {''})
    def get_subjects(self, obj):
        if obj.csv_type == 'HALLS': return []
        return sorted(set(obj.students.values_list('subject_code',flat=True).distinct()))
    class Meta:
        model = CSVUpload
        fields = ['id','name','filename','csv_type','uploaded_by_name','student_count','hall_count','classes','subjects','created_at']

class HallSerializer(serializers.ModelSerializer):
    invigilators = serializers.SerializerMethodField()
    class Meta:
        model = Hall
        fields = ['id','hall_id','capacity','rows','columns','invigilators']
    def get_invigilators(self, obj):
        return [{'id':i.faculty.id,'name':i.faculty.get_full_name() or i.faculty.username}
                for i in obj.invigilators.select_related('faculty')]

class AllocationItemSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='student.student_id')
    student_name = serializers.CharField(source='student.name')
    subject_code = serializers.CharField(source='student.subject_code')
    student_class = serializers.CharField(source='student.student_class')
    hall_id = serializers.CharField(source='hall.hall_id')
    class Meta:
        model = SeatAllocation
        fields = ['student_id','student_name','subject_code','student_class','hall_id','row','column']

class ViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintViolation
        fields = ['violation_type','description','student_id_ref','hall_id_ref','row','column']

class SessionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', default='')
    exam_date_str = serializers.ReadOnlyField()
    exam_time_str = serializers.ReadOnlyField()
    student_csv_name = serializers.SerializerMethodField()
    hall_csv_name = serializers.SerializerMethodField()
    def get_student_csv_name(self, obj):
        return obj.student_csv.name if obj.student_csv else '—'
    def get_hall_csv_name(self, obj):
        return obj.hall_csv.name if obj.hall_csv else '—'
    class Meta:
        model = AllocationSession
        fields = ['id','name','status','exam_date','exam_date_str','exam_time_from','exam_time_to','exam_time_str',
                  'total_students','total_halls','total_capacity','allocated_count','unallocated_count',
                  'allocation_time_ms','warnings','student_csv_name','hall_csv_name','created_by_name','created_at','updated_at']

class SessionDetailSerializer(SessionListSerializer):
    halls = HallSerializer(many=True, read_only=True)
    allocations = AllocationItemSerializer(many=True, read_only=True)
    violations = ViolationSerializer(many=True, read_only=True)
    class Meta(SessionListSerializer.Meta):
        fields = SessionListSerializer.Meta.fields + ['halls','allocations','violations']