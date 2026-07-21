from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

# 1. Custom Login View
class CustomLoginView(LoginView):
    template_name = 'advising/login.html'

# 2. Logout View
def user_logout(request):
    logout(request)
    return redirect('login')

# 3. Temporary Dashboard redirect placeholder
@login_required
def dashboard(request):
    return render(request, 'advising/dashboard.html')