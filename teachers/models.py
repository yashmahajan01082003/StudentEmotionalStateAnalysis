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


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    division = models.CharField(max_length=10)
    class_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name} - {self.class_name} ({self.division})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    class_name = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class StudentEmotionRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="emotions")
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_emotions")
    emotion = models.CharField(max_length=255)   # detected value like "happy", "confused", etc.
    
    start_time = models.DateTimeField()          # when emotion started
    end_time = models.DateTimeField(null=True, blank=True)  # when it ended (optional, if ongoing)
    detected_at = models.DateTimeField(auto_now_add=True)   # when record was created

    def duration(self):
        """Return duration in seconds if end_time is available."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.emotion} ({self.start_time})"
    

class StudentDrowsinessRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="drowsiness_records")
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_drowsiness")
    drowsiness_level = models.CharField(max_length=255)   # detected value like "mild", "moderate", "severe"
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        """Return duration in seconds if end_time is available."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        return f"{self.student.name} - {self.subject} - Drowsiness: {self.drowsiness_level} ({self.start_time})"
    

class StudentPresenceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="presence_records")
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_presence")
    
    is_present = models.BooleanField(default=True)  # True = present, False = absent
    
    start_time = models.DateTimeField()  # when detection started
    end_time = models.DateTimeField(null=True, blank=True)  # when detection ended
    detected_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.name} - {self.subject} - {status} ({self.start_time})"