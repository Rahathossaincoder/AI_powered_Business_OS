from django.contrib import admin

from .models import Employee, Permission, Role, RolePermission, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'first_name', 'last_name', 'is_active', 'email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'email_verified')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'organization', 'name', 'is_system_role')
    search_fields = ('name', 'organization__name')
    list_filter = ('organization', 'is_system_role')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('permission_id', 'code', 'name', 'module')
    search_fields = ('code', 'name', 'module')
    list_filter = ('module',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role_permission_id', 'role', 'permission')
    list_filter = ('role__organization',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'organization', 'branch', 'employee_code', 'first_name', 'last_name', 'role')
    search_fields = ('employee_code', 'first_name', 'last_name', 'email')
    list_filter = ('organization', 'branch', 'status')
