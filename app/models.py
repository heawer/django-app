from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import CASCADE

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Subject(models.Model):
    title = models.CharField(max_length=200)  
    date = models.DateField()  
    time = models.TimeField()  
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='subjects')

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.title}"


class Attendance(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='attendances')
    subject = models.ForeignKey(
        Subject, on_delete=CASCADE, related_name='attendances')
    attended = models.BooleanField(default=False)
    attendance_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.title} - {'Attended' if self.attended else 'Not Attended'}"
