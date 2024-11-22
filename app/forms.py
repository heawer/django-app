from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Subject, User

subject_widget = {
    'title': forms.TextInput({
        'class': 'form-control',
        'placeholder': 'Enter subject title'
    }),
    'date': forms.DateInput({
        'class': 'form-control',
        'type': 'date',
        'placeholder': 'Select date'
    }),
    'time': forms.TimeInput({
        'class': 'form-control',
        'type': 'time',
        'placeholder': 'Select time'
    }),
    'teacher': forms.Select({
        'class': 'form-control'
    })
}

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']


class CreateSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['title', 'date', 'time']
        widgets = subject_widget
