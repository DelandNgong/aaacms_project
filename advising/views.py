from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Appointment, CaseLog
from .forms import AppointmentForm

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
    
    # Handle Appointment Booking (Students)
    if request.method == 'POST' and user.role == 'student':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = user  # Assign logged-in student automatically
            appointment.save()
            return redirect('dashboard')
    else:
        form = AppointmentForm()

    # Fetch data based on role
    if user.role == 'student':
        appointments = Appointment.objects.filter(student=user).order_by('-date')
    else:  # Advisor or Admin
        appointments = Appointment.objects.filter(advisor=user).order_by('-date')

    context = {
        'form': form,
        'appointments': appointments,
    }
    return render(request, 'advising/dashboard.html', context)