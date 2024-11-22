from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),  
    path('subjects/<int:subject_id>/', views.subject_details, name='subject_details'),
    path('subjects/enroll/<int:subject_id>/', views.enroll, name='enroll'),
    path('subjects/unenroll/<int:subject_id>/', views.unenroll, name='unenroll'),
    path('my_subjects/', views.my_subjects, name='my_subjects'),
    path('subjects/attendance/<int:subject_id>/<str:token>/', views.mark_attendance, name='mark_attendance'),
    path('subjects/start_lesson/<int:subject_id>/', views.start_lesson, name='start_lesson'),
    path('subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('subjects/scan_qr_code/', views.scan_qr_code, name='scan_qr_code'),
]
