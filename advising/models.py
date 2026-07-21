from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Users Table (Maps to D1 in your ERD)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('advisor', 'Advisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# 2. Appointments Table (Maps to D2 in your ERD)
class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_appointments')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advisor_appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=50)  # e.g., "10:00 AM - 10:30 AM"
    issue_category = models.CharField(max_length=100)  # e.g., "Registration Guidance"
    appointment_mode = models.CharField(max_length=20, choices=(('In-Person', 'In-Person'), ('Online', 'Online')))
    meeting_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Appt {self.appointment_id}: {self.student.username} with {self.advisor.username}"


# 3. CaseLogs Table (Maps to D3 in your ERD)
class CaseLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='case_logs')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_logs')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_logs')
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.log_id} for Student {self.student.username}"
