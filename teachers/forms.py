from django import forms
from .models import Teacher, Student

class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Teacher
        fields = ['name', 'division', 'class_name', 'subject', 'email', 'password']


class TeacherLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'email', 'class_name', 'division', 'password']


class StudentLoginForm(forms.Form):
    roll_no = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

from django import forms
from .models import Lecture


class LectureForm(forms.ModelForm):
    # Class dropdown (example values — you can customize)
    CLASS_CHOICES = [
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
    ]

    # Division dropdown
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    class_name = forms.ChoiceField(choices=CLASS_CHOICES)
    division = forms.ChoiceField(choices=DIVISION_CHOICES)

    # Date picker
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date'
        })
    )

    # Start time picker
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={'type': 'time'}, format='%H:%M'
        )
    )

    # End time picker
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={'type': 'time'}, format='%H:%M'
        )
    )

    class Meta:
        model = Lecture
        fields = ['title', 'class_name', 'division', 'date', 'start_time', 'end_time']
