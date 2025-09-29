from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    division = models.CharField(max_length=10)
    class_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)   # NEW FIELD

    def __str__(self):
        return f"{self.name} - {self.class_name} ({self.division})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    class_name = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    password = models.CharField(max_length=128)   # NEW FIELD

    def __str__(self):
        return f"{self.name} ({self.roll_no})"

from django.db import models
from datetime import timedelta


class Lecture(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=200)
    class_name = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False)  # auto-calculated

    def save(self, *args, **kwargs):
        # Calculate duration as timedelta
        start_dt = timedelta(
            hours=self.start_time.hour, minutes=self.start_time.minute, seconds=self.start_time.second
        )
        end_dt = timedelta(
            hours=self.end_time.hour, minutes=self.end_time.minute, seconds=self.end_time.second
        )
        self.duration = end_dt - start_dt
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.class_name} ({self.division}) {self.date} [{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}]"
