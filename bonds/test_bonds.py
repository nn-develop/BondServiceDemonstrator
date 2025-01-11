from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from bonds.models import Bond
from decimal import Decimal
from datetime import date, datetime


class BondServiceTestCase(TestCase):
    def setUp(self):
        # Create a user and a token for authentication
        self.user: User = User.objects.create_user(
            username="testuser", password="password"
        )
        self.token: Token = Token.objects.create(user=self.user)
        self.api_client: APIClient = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Data for testing
        self.valid_bond_data: dict[str, str | Decimal | date] = {
            "cval": "CZ0003551251",
            "ison": "Rentico Invest/11.23 DEB 20260531",
            "tval": Decimal(100.00),
            "pdcp": "list",
            "regdt": "2023-05-24",
            "eico": "0019319703",
            "ename": "Rentico Invest s.r.o.",
            "elei": "315700PZ559GOUR26559",
            "interest_rate": Decimal(5.00),
            "purchase_date": datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
            "maturity_date": datetime.strptime("2025-05-31", "%Y-%m-%d").date(),
            "interest_frequency": "Semiannual",
        }

    def test_authentication_required(self) -> None:
        self.api_client.credentials()
        response: Response = self.api_client.get("/api/bonds/manage/")
        self.assertEqual(response.status_code, 401)

    def test_add_bond(self):
        response: Response = self.api_client.post(
            "/api/bonds/manage/", self.valid_bond_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bond.objects.count(), 1)
        bond: Bond = Bond.objects.first()
        self.assertEqual(bond.cval, "CZ0003551251")
        self.assertEqual(bond.ison, "Rentico Invest/11.23 DEB 20260531")

    def test_add_bond_invalid_isin(self):
        invalid_data: dict[str, str | Decimal | date] = self.valid_bond_data.copy()
        invalid_data["cval"] = "INVALIDISIN"
        response: Response = self.api_client.post(
            "/api/bonds/manage/", invalid_data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_update_bond(self):
        bond: Bond = Bond.objects.create(owner=self.user, **self.valid_bond_data)
        update_data: dict[str, str] = {"interest_frequency": "Updated Frequency"}
        response: Response = self.api_client.patch(
            f"/api/bonds/manage/{bond.pk}/", update_data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        bond.refresh_from_db()
        self.assertEqual(bond.interest_frequency, "Updated Frequency")

    def test_delete_bond(self):
        bond: Bond = Bond.objects.create(owner=self.user, **self.valid_bond_data)
        response: Response = self.api_client.delete(f"/api/bonds/manage/{bond.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Bond.objects.count(), 0)

    def test_list_bonds(self):
        Bond.objects.create(owner=self.user, **self.valid_bond_data)
        response: Response = self.api_client.get("/api/bonds/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_portfolio_analysis(self):
        Bond.objects.create(owner=self.user, **self.valid_bond_data)
        analysis_response: Response = self.api_client.get("/api/bonds/analysis/")
        self.assertEqual(analysis_response.status_code, 200)
        data: dict[str, float | None] = analysis_response.json()
        self.assertIn("average_interest_rate", data)
        self.assertIn("nearest_maturity_bond", data)
        self.assertIn("total_value", data)
        self.assertIn("future_value", data)

    def test_invalid_portfolio_analysis_empty(self):
        response: Response = self.api_client.get("/api/bonds/analysis/")
        self.assertEqual(response.status_code, 200)
        data: dict[str, float | None] = response.json()
        self.assertEqual(data["total_value"], 0)
        self.assertIsNone(data["nearest_maturity_bond"])
