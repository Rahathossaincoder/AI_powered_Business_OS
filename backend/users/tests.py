from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Organization
from users.models import Employee

User = get_user_model()


class JwtAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="api-user",
            email="api@example.com",
            password="test-password",
        )
        organization = Organization.objects.create(name="Wavespace", slug="wavespace")
        Employee.objects.create(organization=organization, user=self.user)

    def test_access_token_authenticates_api_requests(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "api-user", "password": "test-password"},
            format="json",
        )

        self.assertEqual(token_response.status_code, 200, token_response.data)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200, response.data)

        refresh_response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": token_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 200, refresh_response.data)
        self.assertIn("access", refresh_response.data)
