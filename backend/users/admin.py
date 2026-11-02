from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Employee, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "organization", "user"]
    list_filter = ["organization"]
    search_fields = ["user__username", "user__email"]
