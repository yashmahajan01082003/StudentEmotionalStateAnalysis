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


from django.shortcuts import render, get_object_or_404
from .models import Student, Lecture

def student_lectures(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    lectures = Lecture.objects.filter(
        class_name=student.class_name,
        division=student.division
    ).order_by("date", "start_time")
    return render(request, "teachers/student_lectures.html", {
        "student": student,
        "lectures": lectures
    })


from django.shortcuts import render, get_object_or_404
from .forms import LectureForm
from .models import Lecture, Teacher


def schedule_lecture(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = LectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.teacher = teacher
            lecture.save()  # duration auto-calculated
            return render(request, "teachers/lecture_success.html", {"lecture": lecture})
    else:
        form = LectureForm()
    return render(request, "teachers/schedule_lecture.html", {"form": form, "teacher": teacher})

from django.shortcuts import render, get_object_or_404
from .models import Teacher, Lecture


def teacher_lectures(request, teacher_id):
    # Get the teacher or return 404 if not found
    teacher = get_object_or_404(Teacher, id=teacher_id)

    # Fetch all lectures scheduled by this teacher
    lectures = Lecture.objects.filter(teacher=teacher).order_by("date", "start_time")

    # Render template
    return render(request, "teachers/teacher_lectures.html", {
        "teacher": teacher,
        "lectures": lectures
    })
