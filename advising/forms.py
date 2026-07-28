from django import forms
from .models import Appointment, User, CaseLog, AvailabilitySlot

# 1. Availability Form for Advisors
class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'time_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.TextInput(attrs={'placeholder': 'e.g., 10:00 AM - 11:00 AM', 'class': 'form-control'}),
        }


# 2. Appointment Form for Students
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['advisor', 'slot', 'issue_category', 'appointment_mode', 'meeting_link']
        widgets = {
            'advisor': forms.Select(attrs={'class': 'form-select'}),
            'slot': forms.Select(attrs={'class': 'form-select'}),
            'issue_category': forms.Select(attrs={'class': 'form-select'}),
            'appointment_mode': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/... (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter available unbooked slots
        self.fields['slot'].queryset = AvailabilitySlot.objects.filter(is_booked=False)
        
        # Filter advisors dropdown to only show Advisor users
        self.fields['advisor'].queryset = User.objects.filter(role='advisor')


# 3. Case Log Form for Advisors
class CaseLogForm(forms.ModelForm):
    class Meta:
        model = CaseLog
        fields = ['appointment', 'notes']
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter session notes, academic recommendations...', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        advisor = kwargs.pop('advisor', None)
        super().__init__(*args, **kwargs)
        if advisor:
            self.fields['appointment'].queryset = Appointment.objects.filter(advisor=advisor)