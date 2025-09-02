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
