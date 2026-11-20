from django.core.management.base import BaseCommand

from catalog.models import Category, Product
from core.models import Branch, Organization
from inventory.models import Inventory
from inventory.services import apply_stock_change, create_inventory_record
from users.models import Employee, User


class Command(BaseCommand):
    help = "Demo organization, login (shakib / shakib123), branches, categories, products, stock and ledger."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(slug="wavespace", defaults={"name": "Wavespace"})
        user, created = User.objects.get_or_create(
            username="shakib", defaults={"email": "shakib@wavespace.io", "is_staff": True, "is_superuser": True}
        )
        if created:
            user.set_password("shakib123")
            user.save()
        Employee.objects.get_or_create(organization=org, user=user)

        branches = {}
        for code, name, main in [("BR-001", "Main HQ Central Depot", True),
                                 ("BR-002", "West Coast Fulfilment", False),
                                 ("BR-003", "Downtown Outlet", False)]:
            branches[code], _ = Branch.objects.get_or_create(
                organization=org, code=code, defaults={"name": name, "is_main_branch": main}
            )

        cats = {}
        for name in ["Hardware", "Software", "IoT Sensors"]:
            cats[name], _ = Category.objects.get_or_create(
                organization=org, slug=name.lower().replace(" ", "-"), defaults={"name": name}
            )

        products = {}
        for sku, name, cat, cost, price, reorder in [
            ("SKU-8841-A", "Quantum Edge AI Server v4", "Hardware", 2800, 3499, 5),
            ("SKU-9920-C", "Wavespace Analytics Pro Seat", "Software", 40, 99, 10),
            ("SKU-7721-B", "IoT Gateway Sensor Array", "IoT Sensors", 120, 249.5, 20),
            ("SKU-5020-X", "High-Density Router X5", "Hardware", 150, 299, 8),
            ("SKU-1100-D", "Edge Compute Module", "Hardware", 300, 520, 10),
            ("SKU-1049-F", "High-Speed Optic Transceiver 100G", "Hardware", 90, 180, 10),
        ]:
            products[sku], _ = Product.objects.get_or_create(
                organization=org, sku=sku,
                defaults={"name": name, "category": cats[cat], "cost_price": cost,
                          "selling_price": price, "reorder_level": reorder},
            )

        if Inventory.objects.filter(organization=org).exists():
            self.stdout.write(self.style.SUCCESS("Demo data ready (inventory already seeded). Login: shakib / shakib123"))
            return

        def stock(sku, branch, opening, reorder):
            return create_inventory_record(organization=org, branch=branches[branch], product=products[sku],
                                           quantity=opening, reorder_level=reorder, user=user)

        def move(record, kind, change, reason, **extra):
            apply_stock_change(inventory=record, quantity_change=change, transaction_type=kind,
                               reason=reason, user=user, **extra)

        quantum = stock("SKU-8841-A", "BR-001", 6, 15)
        move(quantum, "SALE", -3, "Order #ORD-9982", reference_type="ORDER", reference_id="9982")
        iot = stock("SKU-7721-B", "BR-002", 122, 30)
        move(iot, "PURCHASE", 20, "Shipment received from central supplier", reference_type="PURCHASE_ORDER", reference_id="PO-2041")
        stock("SKU-9920-C", "BR-001", 250, 10)
        edge = stock("SKU-1100-D", "BR-001", 42, 10)
        move(edge, "DAMAGE", -2, "Damaged in transit")
        stock("SKU-1100-D", "BR-002", 20, 10)
        stock("SKU-5020-X", "BR-003", 0, 8)
        stock("SKU-1049-F", "BR-003", 0, 10)
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: shakib / shakib123"))