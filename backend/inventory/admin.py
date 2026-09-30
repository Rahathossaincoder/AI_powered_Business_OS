from django.contrib import admin

from .models import Inventory, InventoryTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'organization', 'branch', 'product', 'quantity', 'reorder_level')
    search_fields = ('product__name', 'branch__name', 'organization__name')
    list_filter = ('organization', 'branch')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('inventory_transaction_id', 'organization', 'branch', 'product', 'transaction_type', 'quantity_change', 'created_at')
    search_fields = ('product__name', 'reference_type', 'reference_id')
    list_filter = ('organization', 'branch', 'transaction_type')
