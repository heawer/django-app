import socket
import subprocess
import qrcode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string

from .forms import CreateSubjectForm, RegisterForm
from .models import Attendance, Enrollment, Subject

# authentication
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('subject_list')
    else:
        if request.user.is_authenticated:
            return redirect('subject_list')

        form = RegisterForm()

    return render(
        request,
        'registration/register.html',
        {
            'form': form
        }
    )


# subjects
@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if subject.teacher != request.user:
        return redirect('subject_list')

    if request.method == 'POST':
        form = CreateSubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject updated successfully!")
            return redirect('subject_list')
    else:
        form = CreateSubjectForm(instance=subject)

    return render(request, 'subjects/edit_subject.html', {'form': form, 'subject': subject})

@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if subject.teacher != request.user:
        return redirect('subject_list')

    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect('subject_list')

@login_required
def subject_list(request):
    if request.user.role == 'teacher':
        subjects = Subject.objects.filter(teacher=request.user)

        if request.method == 'POST':
            form = CreateSubjectForm(request.POST)
            if form.is_valid():
                subject = form.save(commit=False)
                subject.teacher = request.user
                subject.save()
                return redirect('subject_list')
        else:
            form = CreateSubjectForm()

        return render(request, 'subjects/subject_list.html', {
            'subjects': subjects,
            'form': form,
        })

    subjects = Subject.objects.all()
    enrollments = Enrollment.objects.filter(student=request.user)
    enrolled_subjects = [enrollment.subject for enrollment in enrollments]

    attendance_data = {}
    for subject in enrolled_subjects:
        attendance = Attendance.objects.filter(
            student=request.user, subject=subject).first()
        attendance_data[subject.id] = attendance


    return render(request, 'subjects/subject_list.html', {
        'subjects': subjects,
        'enrolled_subjects': enrolled_subjects,
        'attendance_data': attendance_data,
    })

@login_required
def subject_details(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.user.role == 'teacher' or subject.teacher == request.user:
        enrollments = subject.enrollments.all()
        students = []
        for enrollment in enrollments:
            attendance = Attendance.objects.filter(
                student=enrollment.student, subject=subject).first()
            students.append({
                'username': enrollment.student.username,
                'attended': attendance.attended if attendance else False,
                'attendance_time': attendance.attendance_time if attendance else None
            })

        return render(request, 'subjects/subject_details.html', {
            'subject': subject,
            'students': students,
        })
    else:
        enrolled_subjects = request.user.enrollments.all()
        enrollment = Enrollment.objects.filter(student=request.user, subject=subject).first()
        attendance = Attendance.objects.filter(student=request.user, subject=subject).first()
        return render(request, 'subjects/subject_details.html', {
            'subject': subject,
            'enrollment': enrollment,
            'attendance': attendance,
            'enrolled_subjects': enrolled_subjects,
        })

    return redirect('subject_list')


@login_required
def my_subjects(request):
    if request.user.role == 'teacher':
        subjects = Subject.objects.filter(teacher=request.user)
        return render(request, 'subjects/my_subjects.html', {'subjects': subjects})

    enrollments = Enrollment.objects.filter(student=request.user)
    enrolled_subjects = [enrollment.subject for enrollment in enrollments]
    return render(request, 'subjects/my_subjects.html', {'enrolled_subjects': enrolled_subjects})


# enrollment
@login_required
def enroll(request, subject_id):
    subject = Subject.objects.get(id=subject_id)

    if Enrollment.objects.filter(student=request.user, subject=subject).exists():
        messages.warning(request, "You are already enrolled in this subject!")
        return redirect('subject_list')

    Enrollment.objects.create(student=request.user, subject=subject)
    messages.success(request, "You have successfully enrolled in the subject!")
    return redirect('subject_list')

@login_required
def unenroll(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    enrollment = Enrollment.objects.filter(
        student=request.user, subject=subject).first()
    if not enrollment:
        messages.error(request, "You are not enrolled in this subject!")
        return redirect('subject_list')

    enrollment.delete()

    Attendance.objects.filter(student=request.user, subject=subject).delete()

    messages.success(
        request, "You have successfully unenrolled from the subject!")
    return redirect('subject_list')


# attendance
@login_required
def start_lesson(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    domain = settings.ALLOWED_HOSTS[0]
    protocol = "https" if request.is_secure() else "http"

    attendance_url = f'{protocol}://{domain}/subjects/attendance/{subject.id}/{get_random_string(length=32)}/'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(attendance_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

@login_required
def mark_attendance(request, subject_id, token):
    subject = get_object_or_404(Subject, id=subject_id)

    enrollment = Enrollment.objects.filter(
        student=request.user, subject=subject).first()

    if not enrollment:
        messages.error(request, "You are not enrolled in this subject.")
        return redirect('subject_list')

    attendance = Attendance.objects.filter(
        student=request.user, subject=subject).first()

    if not attendance:
        attendance = Attendance.objects.create(
            student=request.user,
            subject=subject,
            attended=False,
            attendance_time=None
        )

    if attendance.attended:
        messages.info(request, "You have already marked your attendance.")
        return redirect('subject_list')

    attendance.attended = True
    attendance.attendance_time = timezone.now()
    attendance.save()

    messages.success(request, "Attendance successfully marked!")
    return redirect('subject_details', subject_id=subject.id)


@login_required
def scan_qr_code(request):
    return render(request, 'subjects/scan_qr_code.html')
