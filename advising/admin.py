from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Appointment, CaseLog

# 1. Custom User Admin display
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Attributes', {'fields': ('role', 'department')}),
    )
    list_display = ['username', 'email', 'role', 'department', 'is_staff']

# 2. Register all models to the dashboard
admin.site.register(User, CustomUserAdmin)
admin.site.register(Appointment)
admin.site.register(CaseLog)