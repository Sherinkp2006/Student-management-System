from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['rollno', 'student_name','year','dept','email','mobile_no']


class AdminUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=(
            ('user', 'User'),
            ('staff', 'Staff administrator'),
            ('superuser', 'Superuser'),
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email')