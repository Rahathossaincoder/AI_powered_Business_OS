from accounts.models import AuditLog

AuditLog.objects.all().delete()

data = [
    ("Shahid Miah (EMP-001)", "ORDER_COMPLETED", "Order", "ORD-9982", "192.168.1.42",
     {"status": {"before": "PENDING", "after": "COMPLETED"}}),
    ("David Miller (EMP-004)", "INVENTORY_ADJUSTMENT", "Inventory", "INV-8841", "192.168.1.88",
     {"stock": {"before": 10, "after": 3}}),
    ("System Bot", "AI_TOOL_CALL", "AIConversation", "conv-88912", "127.0.0.1",
     {"tool": {"before": None, "after": "get_sales_summary"}}),
    ("Jessica Wong (EMP-003)", "CUSTOMER_CREATED", "Customer", "CUST-1003", "192.168.1.60",
     {"name": {"before": None, "after": "Elena Rostova"}}),
    ("Alexandre Blanc (EMP-002)", "PRODUCT_UPDATED", "Product", "SKU-8841-A", "192.168.1.75",
     {"price": {"before": 3299, "after": 3499}}),
]

for d in data:
    AuditLog.objects.create(
        performed_by=d[0], action=d[1], entity_type=d[2],
        entity_id=d[3], ip_address=d[4], changes=d[5],
    )

print("Done:", AuditLog.objects.count(), "records added")