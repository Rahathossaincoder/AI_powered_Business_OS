from django.db import models


class Inventory(models.Model):
    inventory_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='inventory_records')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='inventory_items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='inventory_entries')
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        constraints = [
            models.UniqueConstraint(fields=['branch', 'product'], name='unique_inventory_per_branch_product')
        ]

    def __str__(self):
        return f'{self.branch.name} - {self.product.name}: {self.quantity}'


class InventoryTransaction(models.Model):
    TRANSACTION_INITIAL_STOCK = 'INITIAL_STOCK'
    TRANSACTION_PURCHASE = 'PURCHASE'
    TRANSACTION_SALE = 'SALE'
    TRANSACTION_RETURN = 'RETURN'
    TRANSACTION_ADJUSTMENT = 'ADJUSTMENT'
    TRANSACTION_DAMAGE = 'DAMAGE'
    TRANSACTION_CORRECTION = 'CORRECTION'
    TRANSACTION_TRANSFER_IN = 'TRANSFER_IN'
    TRANSACTION_TRANSFER_OUT = 'TRANSFER_OUT'

    TRANSACTION_TYPES = [
        (TRANSACTION_INITIAL_STOCK, 'Initial Stock'),
        (TRANSACTION_PURCHASE, 'Purchase'),
        (TRANSACTION_SALE, 'Sale'),
        (TRANSACTION_RETURN, 'Return'),
        (TRANSACTION_ADJUSTMENT, 'Adjustment'),
        (TRANSACTION_DAMAGE, 'Damage'),
        (TRANSACTION_CORRECTION, 'Correction'),
        (TRANSACTION_TRANSFER_IN, 'Transfer In'),
        (TRANSACTION_TRANSFER_OUT, 'Transfer Out'),
    ]

    inventory_transaction_id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='inventory_transactions')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='inventory_transactions')
    inventory = models.ForeignKey('inventory.Inventory', on_delete=models.CASCADE, related_name='transactions')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='inventory_transactions')
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    quantity_change = models.IntegerField()
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_type} - {self.product.name}'
