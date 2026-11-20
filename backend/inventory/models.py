from django.conf import settings
from django.db import models


class Inventory(models.Model):
    """Current stock of one product at one branch. Quantity only changes through services.apply_stock_change."""

    inventory_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="inventory_records"
    )
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name="inventory_records")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="inventory_records")
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory"
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "product"], name="unique_inventory_per_branch_product"
            )
        ]

    def __str__(self):
        return f"{self.product_id} @ {self.branch_id}: {self.quantity}"


class TransactionType(models.TextChoices):
    INITIAL_STOCK = "INITIAL_STOCK", "Initial stock"
    PURCHASE = "PURCHASE", "Purchase"
    SALE = "SALE", "Sale"
    RETURN = "RETURN", "Return"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"
    DAMAGE = "DAMAGE", "Damage"
    CORRECTION = "CORRECTION", "Correction"


class InventoryTransaction(models.Model):
    """The inventory ledger. One row per stock change; rows are never edited or deleted."""

    inventory_transaction_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        "core.Organization", on_delete=models.CASCADE, related_name="inventory_transactions"
    )
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT, related_name="transactions")
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name="inventory_transactions")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="inventory_transactions")
    transaction_type = models.CharField(max_length=32, choices=TransactionType.choices)
    quantity_change = models.IntegerField()
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    reference_type = models.CharField(max_length=50, blank=True, default="")
    reference_id = models.CharField(max_length=100, blank=True, default="")
    reason = models.CharField(max_length=100, blank=True, default="")
    note = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_transactions"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Inventory ledger rows are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Inventory ledger rows cannot be deleted.")

    def __str__(self):
        return f"{self.transaction_type} {self.quantity_change:+d}"