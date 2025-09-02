from django.shortcuts import render
from .forms import TeacherForm, TeacherLoginForm, StudentForm, StudentLoginForm
from .models import Teacher, Student

# Teacher registration
def register_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            return render(request, "teachers/success.html", {"teacher": teacher})
    else:
        form = TeacherForm()
    return render(request, "teachers/register.html", {"form": form})


# Teacher login
def login_teacher(request):
    if request.method == "POST":
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                teacher = Teacher.objects.get(email=email, password=password)
                return render(request, "teachers/login_success.html", {"teacher": teacher})
            except Teacher.DoesNotExist:
                form.add_error(None, "Invalid teacher credentials")
    else:
        form = TeacherLoginForm()
    return render(request, "teachers/login.html", {"form": form})


# Student registration
def register_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            return render(request, "teachers/student_success.html", {"student": student})
    else:
        form = StudentForm()
    return render(request, "teachers/student_register.html", {"form": form})


# Student login
def login_student(request):
    if request.method == "POST":
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            roll_no = form.cleaned_data['roll_no']
            password = form.cleaned_data['password']
            try:
                student = Student.objects.get(roll_no=roll_no, password=password)
                return render(request, "teachers/student_success.html", {"student": student})
            except Student.DoesNotExist:
                form.add_error(None, "Invalid student credentials")
    else:
        form = StudentLoginForm()
    return render(request, "teachers/student_login.html", {"form": form})
