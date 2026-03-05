from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/me/', views.me_view),
    path('profile/update/', views.update_profile_view),
    path('profile/change-password/', views.change_password_view),

    path('users/', views.list_users_view),
    path('users/create/', views.create_user_view),
    path('users/<int:user_id>/delete/', views.delete_user_view),
    path('faculty/', views.faculty_list_view),

    path('students/', views.list_students_view),
    path('students/search/', views.search_student_view),

    # Three upload endpoints
    path('csv/upload/students/', views.upload_students_csv_view),
    path('csv/upload/halls/', views.upload_halls_csv_view),
    path('csv/upload/combined/', views.upload_combined_csv_view),
    path('csv/', views.list_csv_view),
    path('csv/<int:csv_id>/students/', views.csv_students_view),
    path('csv/<int:csv_id>/halls/', views.csv_halls_view),
    path('csv/<int:csv_id>/delete/', views.delete_csv_view),

    path('sessions/create/', views.create_and_allocate_view),
    path('sessions/', views.session_list_view),
    path('sessions/<int:session_id>/', views.session_detail_view),
    path('sessions/<int:session_id>/delete/', views.delete_session_view),
    path('sessions/<int:session_id>/complete/', views.complete_session_view),
    path('sessions/<int:session_id>/hall-layout/<int:hall_pk>/', views.hall_layout_view),

    path('export/csv/<int:session_id>/', views.export_csv_view),
    path('export/pdf/<int:session_id>/', views.export_pdf_view),

    path('dashboard/', views.dashboard_view),
    path('my-allocations/', views.my_allocations_view),
    path('my-allocations/<int:session_id>/hall/<int:hall_pk>/', views.student_hall_layout_view),
]