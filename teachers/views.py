import os
from urllib import response
from django.shortcuts import render
from .forms import TeacherForm, TeacherLoginForm, StudentForm, StudentLoginForm, LectureForm
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
from django.utils import timezone
from .models import Lecture, Student

def student_lectures(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # All lectures for this student, ordered by date and start_time
    lectures = Lecture.objects.filter(
        class_name=student.class_name,
        division=student.division
    ).order_by("date", "start_time")
    
    # Determine current lecture(s)
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()
    
    current_lectures = lectures.filter(date=today).filter(
        start_time__lte=current_time,
        end_time__gte=current_time
    )
    
    return render(request, "teachers/student_lectures.html", {
        "student": student,
        "lectures": current_lectures,
        "current_lectures": current_lectures,  # This contains lecture(s) happening now
    })


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

from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, time

from django.utils import timezone
from .models import Lecture, Student, LectureAttendance
import time
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import time

from django.utils import timezone
from .models import Student, Lecture, LectureAttendance

import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import time
import os

from django.utils import timezone
from django.http import HttpResponse
from .models import Student, Lecture, LectureAttendance
from django.db.models import F


def run_emotion_function(request, student_id):
    print("Student ID:", student_id)

    # Fetch student
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return HttpResponse(f"No student found with ID: {student_id}")

    # Find current lecture
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    lectures_today = Lecture.objects.filter(
        class_name=student.class_name,
        division=student.division,
        date=today
    )

    current_lecture = None
    for lecture in lectures_today:
        if lecture.start_time <= current_time <= lecture.end_time:
            current_lecture = lecture
            print(f"Tracking emotions for lecture: {lecture.title}")
            break

    if not current_lecture:
        return HttpResponse("No ongoing lecture for this student right now.")

    # Load model and labels from the same directory as views.py
    app_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(app_dir, "model.h5")
    labels_path = os.path.join(app_dir, "labels.npy")

    model = load_model(model_path)
    label = np.load(labels_path)

    # Mediapipe setup
    holistic = mp.solutions.holistic
    hands = mp.solutions.hands
    holis = holistic.Holistic()
    drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    # Timing variables
    emotion_times = {}  # {"Happy": 5.2, "Absent": 3.0}
    current_state = None
    start_time = None

    while True:
        lst = []
        ret, frm = cap.read()
        if not ret:
            break
        frm = cv2.flip(frm, 1)
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

        if res.face_landmarks:
            # Person present, extract landmarks
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)

            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                lst.extend([0.0] * 42)

            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                lst.extend([0.0] * 42)

            lst = np.array(lst).reshape(1, -1)
            pred = label[np.argmax(model.predict(lst))]
            cv2.putText(frm, pred, (50, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
            state = pred
        else:
            # Person absent
            cv2.putText(frm, "Absent", (50, 50), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
            state = "Absent"

        # Timing logic
        current_time_epoch = time.time()
        if current_state is None:
            current_state = state
            start_time = current_time_epoch
        elif current_state != state:
            duration = current_time_epoch - start_time

            # Save or update in DB
            attendance, created = LectureAttendance.objects.get_or_create(
                student=student,
                lecture=current_lecture,
                state=current_state,
                defaults={'duration_seconds': duration}
            )
            if not created:
                attendance.duration_seconds = F('duration_seconds') + duration
                attendance.save()

            emotion_times[current_state] = emotion_times.get(current_state, 0) + duration
            current_state = state
            start_time = current_time_epoch

        # Draw landmarks
        if res.face_landmarks:
            drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_CONTOURS)
        if res.left_hand_landmarks:
            drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
        if res.right_hand_landmarks:
            drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

        cv2.imshow("Emotion Tracking", frm)

        if cv2.waitKey(1) == ord('q'):
            # Save last state
            if current_state is not None and start_time is not None:
                duration = time.time() - start_time

                attendance, created = LectureAttendance.objects.get_or_create(
                    student=student,
                    lecture=current_lecture,
                    state=current_state,
                    defaults={'duration_seconds': duration}
                )
                if not created:
                    attendance.duration_seconds = F('duration_seconds') + duration
                    attendance.save()

                emotion_times[current_state] = emotion_times.get(current_state, 0) + duration
            break

    cap.release()
    cv2.destroyAllWindows()

    # Print summary
    print("\n--- Emotion & Absence Durations ---")
    for state, t in emotion_times.items():
        print(f"{state}: {t:.2f} s")

    return HttpResponse(f"Emotion tracking completed for student {student.name} ({student_id})")

from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import Lecture, Student, LectureAttendance

def check_lecture(request, teacher_id):
    # 1️⃣ Get lecture details from URL query params
    title = request.GET.get('title')
    class_name = request.GET.get('class_name')
    division = request.GET.get('division')
    date_str = request.GET.get('date')
    start_time_str = request.GET.get('start_time')
    end_time_str = request.GET.get('end_time')

    # 2️⃣ Parse date and time strings
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
    except (ValueError, TypeError):
        return render(request, "teachers/check_lecture.html", {
            "error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM:SS for time."
        })

    print(f"Received parameters: title={title}, class_name={class_name}, division={division}, date={date}, start_time={start_time}, end_time={end_time}")

    # 3️⃣ Find the specific lecture for this teacher
    lecture = get_object_or_404(
        Lecture,
        teacher_id=teacher_id,
        title=title,
        class_name=class_name,
        division=division,
        date=date,
        start_time=start_time,
        end_time=end_time
    )

    # 4️⃣ Fetch all students in this class/division
    students = Student.objects.filter(class_name=class_name, division=division)

    # 5️⃣ Build attendance info
    attendance_data = []
    for student in students:
        attendance_entry = LectureAttendance.objects.filter(student=student, lecture=lecture).first()
        if attendance_entry:
            status = attendance_entry.state
            duration = attendance_entry.duration_seconds
        else:
            status = "Absent"
            duration = 0.0
        
        attendance_data.append({
            "student_name": student.name,
            "roll_no": student.roll_no,
            "email": student.email,
            "status": status,
            "duration": duration
        })

    # 6️⃣ Pass data to template
    context = {
        "lecture": lecture,
        "attendance_data": attendance_data,
    }
    return render(request, "teachers/check_lecture.html", context)

from django.shortcuts import render, get_object_or_404
from datetime import datetime
from .models import Student, Lecture, LectureAttendance
from google import genai


def show_student(request, student_id):
    # 1️⃣ Get lecture details from query params
    title = request.GET.get("title")
    class_name = request.GET.get("class_name")
    division = request.GET.get("division")
    date_str = request.GET.get("date")
    start_time_str = request.GET.get("start_time")
    end_time_str = request.GET.get("end_time")
    student_name = request.GET.get("student_name")

    print(f"Received parameters: student name = {student_name} ,title={title}, class_name={class_name}, division={division}, date={date_str}, start_time={start_time_str}, end_time={end_time_str}")

    # 2️⃣ Get the student object
    student = get_object_or_404(Student, name=student_name)
    print("Student:", student)

    # 3️⃣ Convert query params to proper date/time objects
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
    except Exception as e:
        print("Date/Time conversion error:", e)
        date = start_time = end_time = None

    # 4️⃣ Get the correct lecture (matching all params)
    lecture = get_object_or_404(
        Lecture,
        title=title,
        class_name=class_name,
        division=division,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    print("Lecture:", lecture)

    # 5️⃣ Fetch the attendance records for that lecture & student
    attendance_entry = LectureAttendance.objects.filter(
        student_id=student.id,
        lecture_id=lecture.id
    )
    print("Attendance Entry:", attendance_entry)


    GEMINI_API_KEY = "AIzaSyBvyYR9VuZiLlMW-GD188i-Cz2WPwElB58"
    # Initialize the client
    client = genai.Client(api_key=GEMINI_API_KEY)

    # can you create a query which would have the data of the student attendance in a lecture which would have name and the emotion based details in duration and generate the summary about student in this lecture
    # loop attendance entry and create a query donot include everything, just use nam eof stident and attenadcane entry
    query = f"Create a summary for student {student.name} in the lecture titled '{lecture.title}' held on {lecture.date} from {lecture.start_time} to {lecture.end_time}. The student had the following attendance and emotion details: "
    for entry in attendance_entry:
        query += f"State: {entry.state}, Duration: {entry.duration_seconds} seconds. "
    
    # # Generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
    )
    response_text = response.text
    print("Generated Summary:", response_text)
    # response_text = "This is a placeholder summary. Replace this with actual API response."
    # 6️⃣ Render the data
    context = {
        "student": student,
        "lecture": lecture,
        "attendance_entry": attendance_entry,
        "response_text": response_text,
    }
    return render(request, "teachers/show_student.html", context)


def generate_summary(request, teacher_id):
    # 1️⃣ Get lecture details from query params
    title = request.GET.get("title")
    class_name = request.GET.get("class_name")
    division = request.GET.get("division")
    date_str = request.GET.get("date")
    start_time_str = request.GET.get("start_time")
    end_time_str = request.GET.get("end_time")
    # get the lecture dteaals from the query params
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
    except Exception as e:
        print("Date/Time conversion error:", e)
        date = start_time = end_time = None

    # 4️⃣ Get the correct lecture (matching all params)
    lecture = get_object_or_404(
        Lecture,
        title=title,
        class_name=class_name,
        division=division,
        date=date,
        start_time=start_time,
        end_time=end_time
    )

    # 5️⃣ Get all attendance entries (sorted by student)
    attendance_entries = LectureAttendance.objects.filter(lecture=lecture).select_related('student').order_by('student__name')

    # ✅ Group by student
    from collections import defaultdict
    student_data = defaultdict(list)

    for entry in attendance_entries:
        student_data[entry.student].append({
            "state": entry.state,
            "duration": entry.duration_seconds
        })

    # ✅ Build HTML (one row per student)
    report_html = "<h2>Lecture Summary Report</h2>"
    report_html += f"<h3>Lecture: {lecture.title}</h3>"
    report_html += f"<h4>Date: {lecture.date}, Time: {lecture.start_time} - {lecture.end_time}</h4>"
    report_html += "<table border='1' cellpadding='5' cellspacing='0'>"
    report_html += "<tr><th>Student Name</th><th>Roll No</th><th>Email</th><th>Details (State - Duration)</th></tr>"

    for student, records in student_data.items():
        # Combine multiple states into a string
        details = ", ".join([f"{r['state']} ({r['duration']:.2f}s)" for r in records])
        report_html += f"<tr><td>{student.name}</td><td>{student.roll_no}</td><td>{student.email}</td><td>{details}</td></tr>"

    report_html += "</table>"

    # Render
    context = {
        "lecture": lecture,
        "attendance_entries": attendance_entries,
        "report_html": report_html,
    }
    return render(request, "teachers/generate_summary.html", context)
