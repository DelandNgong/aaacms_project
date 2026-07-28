from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Appointment, CaseLog, AvailabilitySlot, User
from .forms import AppointmentForm, CaseLogForm, AvailabilityForm

class CustomLoginView(LoginView):
    template_name = 'advising/login.html'

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    case_log_form = None
    availability_form = None
    form = None
    
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
                
                # Link slot details & check for double-booking race condition
                slot = appointment.slot
                if slot:
                    if slot.is_booked:
                        messages.error(request, "Sorry! That availability slot was just booked by another student. Please select a different slot.")
                        return redirect('dashboard')

                    appointment.date = slot.date
                    appointment.time_slot = slot.time_slot
                    appointment.advisor = slot.advisor
                    slot.is_booked = True
                    slot.save()

                appointment.save()
                advisor_name = appointment.advisor.get_full_name() or appointment.advisor.username
                messages.success(request, f"Appointment successfully scheduled with {advisor_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Please correct the errors below to complete your booking.")
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
                messages.success(request, f"Availability slot for {slot.date} ({slot.time_slot}) published successfully!")
                return redirect('dashboard')
            else:
                messages.error(request, "Failed to publish availability slot. Please check your input.")
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
                student_name = case_log.student.get_full_name() or case_log.student.username
                messages.success(request, f"Case log for {student_name} recorded successfully!")
                return redirect('dashboard')
            else:
                messages.error(request, "Failed to save case log. Please check your input.")
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