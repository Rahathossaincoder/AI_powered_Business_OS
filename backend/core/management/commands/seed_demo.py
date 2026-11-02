from django.core.management.base import BaseCommand

from catalog.models import Category, Product
from core.models import Organization
from inventory.models import Inventory
from users.models import Employee, User


class Command(BaseCommand):
    help = "Org, login (shakib / shakib123), categories, products, stock."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug="wavespace", defaults={"name": "Wavespace"}
        )
        user, created = User.objects.get_or_create(
            username="shakib",
            defaults={
                "email": "shakib@wavespace.io",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("shakib123")
            user.save()
        Employee.objects.get_or_create(organization=org, user=user)

        cats = {}
        for name in ["Hardware", "Software", "IoT Sensors"]:
            cats[name], _ = Category.objects.get_or_create(
                organization=org,
                slug=name.lower().replace(" ", "-"),
                defaults={"name": name},
            )

        rows = [
            ("SKU-8841-A", "Quantum Edge AI Server v4", "Hardware", 2800, 3499, 5, 3),
            ("SKU-9920-C", "Wavespace Analytics Pro Seat", "Software", 40, 99, 10, 250),
            ("SKU-7721-B", "IoT Gateway Sensor Array", "IoT Sensors", 120, 249.5, 20, 142),
            ("SKU-5020-X", "High-Density Router X5", "Hardware", 150, 299, 8, 0),
            ("SKU-1100-D", "Edge Compute Module", "Hardware", 300, 520, 10, 60),
        ]
        for sku, name, cat, cost, price, reorder, qty in rows:
            product, _ = Product.objects.get_or_create(
                organization=org,
                sku=sku,
                defaults={
                    "name": name,
                    "category": cats[cat],
                    "cost_price": cost,
                    "selling_price": price,
                    "reorder_level": reorder,
                },
            )
            Inventory.objects.get_or_create(
                organization=org, product=product, defaults={"quantity": qty}
            )
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: shakib / shakib123"))