from django.contrib import admin
from django.urls import path
from accounts.views import AuditLogListCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/audit-logs/', AuditLogListCreateView.as_view(), name='audit-logs-api'),
]