from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Appointment, CaseLog
from .forms import AppointmentForm, CaseLogForm

# 1. Login View
class CustomLoginView(LoginView):
    template_name = 'advising/login.html'

# 2. Logout View
def user_logout(request):
    logout(request)
    return redirect('login')

# 3. Dynamic Dashboard View
@login_required
def dashboard(request):
    user = request.user
    case_log_form = None
    
    # Handle Student Booking
    if request.method == 'POST' and 'submit_appointment' in request.POST and user.role == 'student':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = user
            appointment.save()
            return redirect('dashboard')
    else:
        form = AppointmentForm()

    # Handle Advisor Case Log Submission
    if request.method == 'POST' and 'submit_caselog' in request.POST and user.role == 'advisor':
        case_log_form = CaseLogForm(request.POST, advisor=user)
        if case_log_form.is_valid():
            case_log = case_log_form.save(commit=False)
            case_log.advisor = user
            case_log.student = case_log.appointment.student
            case_log.save()
            return redirect('dashboard')
    elif user.role == 'advisor':
        case_log_form = CaseLogForm(advisor=user)

    # Fetch data based on role
    if user.role == 'student':
        appointments = Appointment.objects.filter(student=user).order_by('-date')
        case_logs = CaseLog.objects.filter(student=user).order_by('-created_at')
    else:  # Advisor / Admin
        appointments = Appointment.objects.filter(advisor=user).order_by('-date')
        case_logs = CaseLog.objects.filter(advisor=user).order_by('-created_at')

    context = {
        'form': form,
        'case_log_form': case_log_form,
        'appointments': appointments,
        'case_logs': case_logs,
    }
    return render(request, 'advising/dashboard.html', context)