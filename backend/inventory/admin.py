from django.contrib import admin

from .models import Inventory, InventoryTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "branch", "quantity", "reorder_level", "organization", "updated_at"]
    list_filter = ["organization", "branch"]
    search_fields = ["product__name", "product__sku"]


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ["created_at", "product", "branch", "transaction_type", "quantity_change", "quantity_after"]
    list_filter = ["transaction_type", "branch"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False