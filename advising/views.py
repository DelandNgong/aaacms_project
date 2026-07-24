from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Appointment, CaseLog, AvailabilitySlot, User
from .forms import AppointmentForm, CaseLogForm, AvailabilityForm

class CustomLoginView(LoginView):
    template_name = 'advising/login.html'

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    case_log_form = None
    availability_form = None
    
    # ------------------------------------
    # STUDENT WORKFLOW
    # ------------------------------------
    if user.role == 'student':
        # Search & Filtering
        query = request.GET.get('search', '').strip()
        
        available_slots = AvailabilitySlot.objects.filter(is_booked=False)
        if query:
            available_slots = available_slots.filter(
                Q(advisor__username__icontains=query) |
                Q(advisor__first_name__icontains=query) |
                Q(advisor__last_name__icontains=query) |
                Q(date__icontains=query)
            )

        # Handle Booking Submission
        if request.method == 'POST' and 'submit_appointment' in request.POST:
            form = AppointmentForm(request.POST)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.student = user
                
                # Link slot details
                slot = appointment.slot
                if slot:
                    appointment.date = slot.date
                    appointment.time_slot = slot.time_slot
                    appointment.advisor = slot.advisor
                    slot.is_booked = True
                    slot.save()

                appointment.save()
                return redirect('dashboard')
        else:
            form = AppointmentForm()

        appointments = Appointment.objects.filter(student=user).order_by('-date')
        case_logs = CaseLog.objects.filter(student=user).order_by('-created_at')

        context = {
            'form': form,
            'appointments': appointments,
            'case_logs': case_logs,
            'available_slots': available_slots,
            'query': query,
        }

    # ------------------------------------
    # ADVISOR WORKFLOW
    # ------------------------------------
    else:
        # Handle Availability Submission
        if request.method == 'POST' and 'submit_availability' in request.POST:
            availability_form = AvailabilityForm(request.POST)
            if availability_form.is_valid():
                slot = availability_form.save(commit=False)
                slot.advisor = user
                slot.save()
                return redirect('dashboard')
        else:
            availability_form = AvailabilityForm()

        # Handle Case Log Submission
        if request.method == 'POST' and 'submit_caselog' in request.POST:
            case_log_form = CaseLogForm(request.POST, advisor=user)
            if case_log_form.is_valid():
                case_log = case_log_form.save(commit=False)
                case_log.advisor = user
                case_log.student = case_log.appointment.student
                case_log.save()
                return redirect('dashboard')
        else:
            case_log_form = CaseLogForm(advisor=user)

        appointments = Appointment.objects.filter(advisor=user).order_by('-date')
        case_logs = CaseLog.objects.filter(advisor=user).order_by('-created_at')
        my_slots = AvailabilitySlot.objects.filter(advisor=user).order_by('date')

        context = {
            'availability_form': availability_form,
            'case_log_form': case_log_form,
            'appointments': appointments,
            'case_logs': case_logs,
            'my_slots': my_slots,
        }

    return render(request, 'advising/dashboard.html', context)