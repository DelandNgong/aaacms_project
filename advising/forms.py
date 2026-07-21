from django import forms
from .models import Appointment, User

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['advisor', 'date', 'time_slot', 'issue_category', 'appointment_mode', 'meeting_link']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.TextInput(attrs={'placeholder': 'e.g., 10:00 AM - 10:30 AM', 'class': 'form-control'}),
            'issue_category': forms.TextInput(attrs={'placeholder': 'e.g., Academic Guidance, Registration', 'class': 'form-control'}),
            'appointment_mode': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'placeholder': 'Optional Google Meet or Teams link', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter advisor dropdown so only users with role='advisor' appear!
        self.fields['advisor'].queryset = User.objects.filter(role='advisor')
        self.fields['advisor'].widget.attrs.update({'class': 'form-select'})