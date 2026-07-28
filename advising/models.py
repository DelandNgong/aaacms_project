from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom Extended User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('advisor', 'Advisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


# 2. Advisor Availability Slots Model
class AvailabilitySlot(models.Model):
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'advisor'}, related_name='availability_slots')
    date = models.DateField()
    time_slot = models.CharField(max_length=50) # e.g., "10:00 AM - 11:00 AM"
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'time_slot']

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.advisor.username} - {self.date} ({self.time_slot}) [{status}]"


# 3. Appointment Model
class Appointment(models.Model):
    # Category Choices Definition
    CATEGORY_CHOICES = [
        ('Academic Advising', 'Academic Advising'),
        ('Course Registration', 'Course Registration'),
        ('Graduation Audit', 'Graduation Audit'),
        ('Career Guidance', 'Career Guidance'),
        ('General Inquiry', 'General Inquiry'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_appointments')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advisor_appointments')
    slot = models.ForeignKey(AvailabilitySlot, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time_slot = models.CharField(max_length=50)
    
    # Ensure choices=CATEGORY_CHOICES is set
    issue_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Academic Advising')
    
    appointment_mode = models.CharField(max_length=50, choices=[('In-Person', 'In-Person'), ('Virtual', 'Virtual')], default='In-Person')
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 4. Case Log Model (With Unique related_names Fixed)
class CaseLog(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='case_logs')
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'advisor'}, related_name='advisor_caselogs')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='student_caselogs')
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.student.username} by {self.advisor.username}"