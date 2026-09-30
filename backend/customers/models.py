from django.db import models


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='customers')
    customer_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'customer_code'], name='unique_customer_code_per_organization')
        ]
        ordering = ['name']

    def __str__(self):
        return self.name
