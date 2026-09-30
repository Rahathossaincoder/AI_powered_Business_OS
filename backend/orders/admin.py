from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'organization', 'branch', 'order_number', 'customer', 'status', 'total_amount', 'created_at')
    search_fields = ('order_number', 'customer__name', 'organization__name')
    list_filter = ('organization', 'branch', 'status')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'product', 'quantity', 'unit_price', 'line_total')
    search_fields = ('product__name', 'order__order_number')
    list_filter = ('order__organization',)
