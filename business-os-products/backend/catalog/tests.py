from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from catalog.models import Category, Product
from core.models import Organization
from inventory.models import Inventory
from users.models import Employee

User = get_user_model()


class ProductApiTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Wavespace", slug="wavespace")
        self.other_org = Organization.objects.create(name="Other", slug="other")
        self.user = User.objects.create_user(
            username="a", email="a@x.io", password="pw"
        )
        Employee.objects.create(organization=self.org, user=self.user)
        self.cat = Category.objects.create(
            organization=self.org, name="Hardware", slug="hardware"
        )
        self.other_cat = Category.objects.create(
            organization=self.other_org, name="Secret", slug="secret"
        )
        self.client.force_authenticate(self.user)

    def make(self, sku, qty, reorder=5, **kw):
        p = Product.objects.create(
            organization=self.org,
            category=self.cat,
            sku=sku,
            name=f"P {sku}",
            cost_price=10,
            selling_price=20,
            reorder_level=reorder,
            **kw,
        )
        Inventory.objects.create(organization=self.org, product=p, quantity=qty)
        return p

    def payload(self, **kw):
        d = {
            "sku": "sku-1",
            "name": "Widget",
            "category": self.cat.pk,
            "cost_price": "10.00",
            "selling_price": "25.00",
            "reorder_level": 3,
            "unit": "pcs",
        }
        d.update(kw)
        return d

    def test_create_sets_org_and_uppercases_sku(self):
        r = self.client.post("/api/products/", self.payload(), format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["sku"], "SKU-1")
        self.assertEqual(r.data["stock"], 0)
        self.assertEqual(r.data["stock_status"], "out_of_stock")
        self.assertEqual(Product.objects.get(pk=r.data["id"]).organization, self.org)

    def test_frontend_cannot_choose_organization(self):
        r = self.client.post(
            "/api/products/",
            self.payload(organization=self.other_org.pk),
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Product.objects.get(pk=r.data["id"]).organization, self.org)

    def test_duplicate_sku_rejected(self):
        self.make("SKU-1", 5)
        r = self.client.post("/api/products/", self.payload(sku="sku-1"), format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("sku", r.data)

    def test_other_orgs_category_rejected(self):
        r = self.client.post(
            "/api/products/", self.payload(category=self.other_cat.pk), format="json"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("category", r.data)

    def test_negative_price_rejected(self):
        r = self.client.post(
            "/api/products/", self.payload(cost_price="-1"), format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_stock_status_and_summary(self):
        self.make("A", 100)
        self.make("B", 3)
        self.make("C", 0)
        s = self.client.get("/api/products/summary/").data
        self.assertEqual(
            s, {"total": 3, "in_stock": 1, "low_stock": 1, "out_of_stock": 1}
        )
        r = self.client.get("/api/products/?stock_status=low_stock")
        self.assertEqual([x["sku"] for x in r.data["results"]], ["B"])

    def test_search_filter_and_price(self):
        self.make("ALPHA", 9)
        self.make("BETA", 9)
        r = self.client.get("/api/products/?search=alp")
        self.assertEqual(r.data["count"], 1)
        r = self.client.get("/api/products/?min_price=21")
        self.assertEqual(r.data["count"], 0)

    def test_tenant_isolation(self):
        other = Product.objects.create(
            organization=self.other_org,
            category=self.other_cat,
            sku="X",
            name="X",
            cost_price=1,
            selling_price=2,
        )
        self.assertEqual(self.client.get("/api/products/").data["count"], 0)
        self.assertEqual(self.client.get(f"/api/products/{other.pk}/").status_code, 404)

    def test_update_and_soft_delete(self):
        p = self.make("A", 10)
        r = self.client.patch(
            f"/api/products/{p.pk}/", {"selling_price": "99.00"}, format="json"
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["selling_price"], "99.00")
        self.assertEqual(r.data["stock"], 10)
        self.assertEqual(self.client.delete(f"/api/products/{p.pk}/").status_code, 204)
        p.refresh_from_db()
        self.assertFalse(p.is_active)

    def test_requires_login_and_org(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/products/").status_code, 403)
        loner = User.objects.create_user(username="l", email="l@x.io", password="pw")
        self.client.force_authenticate(loner)
        self.assertEqual(self.client.get("/api/products/").status_code, 403)

    def test_categories(self):
        r = self.client.post("/api/categories/", {"name": "Software"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["slug"], "software")
        r2 = self.client.post("/api/categories/", {"name": "Software"}, format="json")
        self.assertEqual(r2.status_code, 400)
        self.assertEqual(self.client.get("/api/categories/").data["count"], 2)
