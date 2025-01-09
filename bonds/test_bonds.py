from django.http import HttpResponse
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from bonds.models import Bond


class BondServiceTestCase(TestCase):
    def setUp(self):
        # Create a user and a token for authentication
        self.user: User = User.objects.create_user(
            username="testuser", password="password"
        )
        self.token: Token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Data for testing
        self.valid_bond_data: dict[str, str | float] = {
            "name": "Corporate Bond A",
            "isin": "CZ0003551251",
            "value": 1000.0,
            "interest_rate": 5.0,
            "purchase_date": "2024-01-01",
            "maturity_date": "2025-01-01",
            "interest_payment_frequency": "annual",
        }

    def test_authentication_required(self):
        # Test accessing an endpoint without authentication
        self.client.credentials()  # Remove the token
        response: HttpResponse = self.client.get("/api/bonds/")
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_add_bond(self):
        # Test adding a new bond
        response: HttpResponse = self.client.post(
            "/api/bonds/", self.valid_bond_data, format="json"
        )
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(Bond.objects.count(), 1)
        bond = Bond.objects.first()
        self.assertEqual(bond.name, "Corporate Bond A")

    def test_add_bond_invalid_isin(self):
        # Test adding a bond with an invalid ISIN
        invalid_data: dict[str, str | float] = self.valid_bond_data.copy()
        invalid_data["isin"] = "INVALIDISIN"
        response: HttpResponse = self.client.post(
            "/api/bonds/", invalid_data, format="json"
        )
        self.assertEqual(response.status_code, 400)  # Bad Request

    def test_update_bond(self):
        # Test updating an existing bond
        bond = Bond.objects.create(owner=self.user, **self.valid_bond_data)
        update_data: dict[str, str] = {"name": "Updated Bond Name"}
        response: HttpResponse = self.client.patch(
            f"/api/bonds/{bond.id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, 200)  # OK
        bond.refresh_from_db()
        self.assertEqual(bond.name, "Updated Bond Name")

    def test_delete_bond(self):
        # Test deleting a bond
        bond = Bond.objects.create(owner=self.user, **self.valid_bond_data)
        response: HttpResponse = self.client.delete(f"/api/bonds/{bond.id}/")
        self.assertEqual(response.status_code, 204)  # No Content
        self.assertEqual(Bond.objects.count(), 0)

    def test_list_bonds(self):
        # Test listing all bonds
        Bond.objects.create(owner=self.user, **self.valid_bond_data)
        response: HttpResponse = self.client.get("/api/bonds/")
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.json()), 1)

    def test_portfolio_analysis(self):
        # Test portfolio analysis endpoint
        Bond.objects.create(owner=self.user, **self.valid_bond_data)
        analysis_response: HttpResponse = self.client.get("/api/bonds/analysis/")
        self.assertEqual(analysis_response.status_code, 200)  # OK
        data = analysis_response.json()
        self.assertIn("average_interest_rate", data)
        self.assertIn("nearest_maturity_bond", data)
        self.assertIn("total_value", data)
        self.assertIn("future_value", data)

    def test_invalid_portfolio_analysis_empty(self):
        # Test portfolio analysis for an empty portfolio
        response: HttpResponse = self.client.get("/api/bonds/analysis/")
        self.assertEqual(response.status_code, 200)  # OK
        data = response.json()
        self.assertEqual(data["total_value"], 0)
        self.assertIsNone(data["nearest_maturity_bond"])

    def test_invalid_api_token(self):
        # Test using an invalid token
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response: HttpResponse = self.client.get("/api/bonds/")
        self.assertEqual(response.status_code, 401)  # Unauthorized
