from rest_framework import generics
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListCreateView(generics.ListCreateAPIView):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer