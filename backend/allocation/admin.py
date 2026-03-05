from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CUA(UserAdmin):
    list_display = ['username','role','department','is_active']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (('Extra',{'fields':('role','phone','department','bio')}),)

@admin.register(CSVUpload)
class CSVA(admin.ModelAdmin):
    list_display = ['name','filename','csv_type','student_count','hall_count','created_at']
    list_filter = ['csv_type']

@admin.register(StudentRecord)
class SRA(admin.ModelAdmin):
    list_display = ['student_id','name','subject_code','student_class','csv_upload']
    search_fields = ['student_id','name']

@admin.register(HallEntry)
class HEA(admin.ModelAdmin):
    list_display = ['hall_id','capacity','rows','columns','csv_upload']

@admin.register(AllocationSession)
class ASA(admin.ModelAdmin):
    list_display = ['name','status','exam_date','total_students','allocated_count']

@admin.register(SeatAllocation)
class SAA(admin.ModelAdmin):
    list_display = ['session','student','hall','row','column']

@admin.register(HallInvigilator)
class HIA(admin.ModelAdmin):
    list_display = ['session','hall','faculty']