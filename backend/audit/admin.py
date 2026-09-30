from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('audit_log_id', 'organization', 'user', 'employee', 'action', 'entity_type', 'created_at')
    search_fields = ('action', 'entity_type', 'entity_id', 'user__email', 'employee__email')
    list_filter = ('organization', 'action', 'entity_type')
