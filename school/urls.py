from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('teachers.urls')),   # root redirects to teachers.urls
]
