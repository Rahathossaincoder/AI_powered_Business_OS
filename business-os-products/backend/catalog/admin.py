from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "parent", "is_active"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "organization", "category", "selling_price", "is_active"]
    list_filter = ["organization", "category", "is_active"]
    search_fields = ["sku", "name"]
