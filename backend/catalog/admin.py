from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'organization', 'parent', 'name', 'slug', 'is_active')
    search_fields = ('name', 'slug', 'organization__name')
    list_filter = ('organization', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'organization', 'category', 'sku', 'name', 'selling_price', 'is_active')
    search_fields = ('sku', 'name', 'organization__name')
    list_filter = ('organization', 'category', 'is_active')
