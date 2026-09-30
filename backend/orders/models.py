from django.db import models


class Order(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    order_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='orders')
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=50)
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='orders')
    created_by_employee = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_created')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'order_number'], name='unique_order_number_per_organization')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        ordering = ['order_item_id']

    def __str__(self):
        return f'{self.order.order_number} - {self.product.name}'
