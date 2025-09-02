from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_teacher, name="login_teacher"),
    path("register/", views.register_teacher, name="register_teacher"),
    path("student/register/", views.register_student, name="register_student"),
    path("student/login/", views.login_student, name="login_student"),
]
