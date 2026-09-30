from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'organization', 'customer_code', 'name', 'phone', 'email', 'is_active')
    search_fields = ('customer_code', 'name', 'phone', 'email')
    list_filter = ('organization', 'is_active')
