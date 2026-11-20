from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from catalog.models import Category, Product
from core.models import Branch, Organization
from inventory.models import Inventory, InventoryTransaction
from users.models import Employee

User = get_user_model()


class InventoryApiTests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Wavespace", slug="wavespace"
        )
        self.other_organization = Organization.objects.create(
            name="Other", slug="other"
        )
        self.user = User.objects.create_user(
            username="inventory-user",
            email="inventory@example.com",
            password="test-password",
        )
        Employee.objects.create(organization=self.organization, user=self.user)
        self.category = Category.objects.create(
            organization=self.organization, name="Hardware", slug="hardware"
        )
        self.product = Product.objects.create(
            organization=self.organization,
            category=self.category,
            sku="SKU-1",
            name="Widget",
            cost_price=10,
            selling_price=20,
        )
        self.branch = Branch.objects.create(
            organization=self.organization, code="BR-001", name="Main"
        )
        self.client.force_authenticate(self.user)

    def test_create_inventory_writes_opening_stock_transaction(self):
        response = self.client.post(
            "/api/inventory/",
            {
                "branch": self.branch.pk,
                "product": self.product.pk,
                "quantity": 8,
                "reorder_level": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        record = Inventory.objects.get(pk=response.data["id"])
        transaction = InventoryTransaction.objects.get(inventory=record)
        self.assertEqual(record.quantity, 8)
        self.assertEqual(transaction.transaction_type, "INITIAL_STOCK")
        self.assertEqual(transaction.quantity_before, 0)
        self.assertEqual(transaction.quantity_after, 8)

    def test_adjustment_updates_stock_and_writes_ledger_entry(self):
        record = Inventory.objects.create(
            organization=self.organization,
            branch=self.branch,
            product=self.product,
            quantity=8,
        )

        response = self.client.post(
            "/api/inventory/adjust/",
            {
                "inventory": record.pk,
                "transaction_type": "SALE",
                "quantity_change": -3,
                "reason": "Order fulfilled",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        record.refresh_from_db()
        self.assertEqual(record.quantity, 5)
        self.assertEqual(response.data["transaction"]["quantity_before"], 8)
        self.assertEqual(response.data["transaction"]["quantity_after"], 5)

    def test_adjustment_rejects_negative_stock_without_ledger_entry(self):
        record = Inventory.objects.create(
            organization=self.organization,
            branch=self.branch,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            "/api/inventory/adjust/",
            {
                "inventory": record.pk,
                "transaction_type": "SALE",
                "quantity_change": -3,
                "reason": "Order fulfilled",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        record.refresh_from_db()
        self.assertEqual(record.quantity, 2)
        self.assertFalse(InventoryTransaction.objects.filter(inventory=record).exists())

    def test_inventory_quantity_can_only_change_through_adjustment(self):
        record = Inventory.objects.create(
            organization=self.organization,
            branch=self.branch,
            product=self.product,
            quantity=8,
        )

        response = self.client.patch(
            f"/api/inventory/{record.pk}/",
            {"quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        record.refresh_from_db()
        self.assertEqual(record.quantity, 8)
