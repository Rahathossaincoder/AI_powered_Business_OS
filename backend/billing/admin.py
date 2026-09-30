from django.contrib import admin

from .models import Invoice, Payment, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'organization', 'order', 'amount', 'payment_method', 'status', 'payment_date')
    search_fields = ('transaction_reference', 'order__order_number')
    list_filter = ('organization', 'payment_method', 'status')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'organization', 'invoice_number', 'order', 'status', 'total_amount', 'issued_at')
    search_fields = ('invoice_number', 'order__order_number')
    list_filter = ('organization', 'status')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_id', 'organization', 'receipt_number', 'invoice', 'receipt_type', 'print_status')
    search_fields = ('receipt_number', 'invoice__invoice_number')
    list_filter = ('organization', 'receipt_type', 'print_status')
