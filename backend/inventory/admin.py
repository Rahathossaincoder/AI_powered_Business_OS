from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["organization", "product", "quantity"]
    list_filter = ["organization"]
    search_fields = ["product__sku", "product__name"]
