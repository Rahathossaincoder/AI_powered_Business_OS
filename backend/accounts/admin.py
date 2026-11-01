from django.contrib import admin
from .models import Customer, Order, Invoice, AuditLog

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Invoice)
admin.site.register(AuditLog)