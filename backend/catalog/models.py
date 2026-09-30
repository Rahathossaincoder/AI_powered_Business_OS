from django.db import models


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'slug'], name='unique_category_slug_per_organization')
        ]
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('catalog.Category', on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, default='pcs')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.IntegerField(default=0)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'sku'], name='unique_product_sku_per_organization')
        ]
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'
