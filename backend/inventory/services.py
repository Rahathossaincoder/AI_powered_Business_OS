from django.db import transaction

from .models import Inventory, InventoryTransaction, TransactionType

POSITIVE_ONLY = {TransactionType.INITIAL_STOCK, TransactionType.PURCHASE, TransactionType.RETURN}
NEGATIVE_ONLY = {TransactionType.SALE, TransactionType.DAMAGE}


class StockError(ValueError):
    """Raised when a stock change breaks a business rule."""


def check_change(transaction_type, quantity_change, quantity_before):
    """Validates the sign and the resulting stock. Returns quantity_after."""
    if quantity_change == 0:
        raise StockError("Quantity change cannot be zero.")
    if transaction_type in POSITIVE_ONLY and quantity_change < 0:
        raise StockError(f"{transaction_type} must add stock (use a positive quantity).")
    if transaction_type in NEGATIVE_ONLY and quantity_change > 0:
        raise StockError(f"{transaction_type} must remove stock (use a negative quantity).")
    quantity_after = quantity_before + quantity_change
    if quantity_after < 0:
        raise StockError(f"Not enough stock: only {quantity_before} available.")
    return quantity_after


@transaction.atomic
def apply_stock_change(*, inventory, quantity_change, transaction_type, reason, note="",
                       reference_type="", reference_id="", user=None):
    """The only place stock is changed. Locks the row, updates the quantity and writes the ledger entry together."""
    locked = Inventory.objects.select_for_update().get(pk=inventory.pk)
    before = locked.quantity
    after = check_change(transaction_type, quantity_change, before)
    locked.quantity = after
    locked.save(update_fields=["quantity", "updated_at"])
    entry = InventoryTransaction.objects.create(
        organization_id=locked.organization_id, inventory=locked, branch_id=locked.branch_id,
        product_id=locked.product_id, transaction_type=transaction_type,
        quantity_change=quantity_change, quantity_before=before, quantity_after=after,
        reference_type=reference_type, reference_id=reference_id, reason=reason, note=note,
        created_by=user if getattr(user, "is_authenticated", False) else None,
    )
    return locked, entry


@transaction.atomic
def create_inventory_record(*, organization, branch, product, quantity, reorder_level, user=None):
    """Creates the stock record; opening stock above zero is written to the ledger as INITIAL_STOCK."""
    record = Inventory.objects.create(
        organization=organization, branch=branch, product=product, quantity=0, reorder_level=reorder_level
    )
    if quantity > 0:
        record, _ = apply_stock_change(
            inventory=record, quantity_change=quantity, transaction_type=TransactionType.INITIAL_STOCK,
            reason="Opening stock", user=user,
        )
    return record