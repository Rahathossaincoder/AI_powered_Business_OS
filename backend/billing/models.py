from django.db import models


class Payment(models.Model):
    PAYMENT_METHOD_CASH = 'CASH'
    PAYMENT_METHOD_CARD = 'CARD'
    PAYMENT_METHOD_MOBILE = 'MOBILE_PAYMENT'
    PAYMENT_METHOD_BANK = 'BANK_TRANSFER'
    PAYMENT_METHOD_OTHER = 'OTHER'

    PAYMENT_METHODS = [
        (PAYMENT_METHOD_CASH, 'Cash'),
        (PAYMENT_METHOD_CARD, 'Card'),
        (PAYMENT_METHOD_MOBILE, 'Mobile Payment'),
        (PAYMENT_METHOD_BANK, 'Bank Transfer'),
        (PAYMENT_METHOD_OTHER, 'Other'),
    ]

    payment_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHODS, default=PAYMENT_METHOD_CASH)
    status = models.CharField(max_length=32, default='paid')
    transaction_reference = models.CharField(max_length=255, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.order.order_number} - {self.amount}'


class Invoice(models.Model):
    INVOICE_PENDING = 'PENDING'
    INVOICE_PAID = 'PAID'
    INVOICE_CANCELLED = 'CANCELLED'

    INVOICE_STATUS = [
        (INVOICE_PENDING, 'Pending'),
        (INVOICE_PAID, 'Paid'),
        (INVOICE_CANCELLED, 'Cancelled'),
    ]

    invoice_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='invoices')
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50)
    status = models.CharField(max_length=32, choices=INVOICE_STATUS, default=INVOICE_PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'invoice_number'], name='unique_invoice_number_per_organization')
        ]

    def __str__(self):
        return self.invoice_number


class Receipt(models.Model):
    receipt_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='receipts')
    invoice = models.OneToOneField('billing.Invoice', on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50)
    receipt_type = models.CharField(max_length=50, default='sales')
    file_path = models.CharField(max_length=255, blank=True)
    print_status = models.CharField(max_length=32, default='pending')
    generated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'receipts'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'receipt_number'], name='unique_receipt_number_per_organization')
        ]

    def __str__(self):
        return self.receipt_number
