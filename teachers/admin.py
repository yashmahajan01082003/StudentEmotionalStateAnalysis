from django.contrib import admin
from .models import Teacher, Student, Lecture, LectureAttendance
# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Lecture)
admin.site.register(LectureAttendance)