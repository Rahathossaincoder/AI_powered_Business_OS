from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default='DRAFT')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    issued_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

class AuditLog(models.Model):
    audit_log_id = models.AutoField(primary_key=True)
    performed_by = models.CharField(max_length=255)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100, blank=True, default="")
    ip_address = models.CharField(max_length=50, default="127.0.0.1")
    changes = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.performed_by}"