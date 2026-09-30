from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    profile_picture = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.email


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'name'], name='unique_role_name_per_organization')
        ]

    def __str__(self):
        return self.name


class Permission(models.Model):
    permission_id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'name']

    def __str__(self):
        return f'{self.module}:{self.code}'


class RolePermission(models.Model):
    role_permission_id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey('users.Role', on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey('users.Permission', on_delete=models.CASCADE, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_permissions'
        constraints = [
            models.UniqueConstraint(fields=['role', 'permission'], name='unique_role_permission')
        ]

    def __str__(self):
        return f'{self.role.name} -> {self.permission.code}'


class Employee(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='employees')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    role = models.ForeignKey('users.Role', on_delete=models.PROTECT, related_name='employees')
    employee_code = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, default='active')
    hire_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'employee_code'], name='unique_employee_code_per_organization')
        ]
        ordering = ['organization', 'employee_code']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
