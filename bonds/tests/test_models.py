from django.test import TestCase
from django.core.exceptions import ValidationError
from bonds.models import Bond
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, datetime


class BondModelTestCase(TestCase):
    def setUp(self):
        self.user: User = User.objects.create_user(
            username="testuser", password="password"
        )

        self.valid_bond_data: dict[str, str | Decimal | date | User] = {
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
            "owner": self.user,
        }

    def test_validate_cval_format(self):
        with self.assertRaises(ValidationError):
            Bond.validate_cval_format("INVALIDISIN")

    def test_create_valid_bond(self):
        bond: Bond = Bond.objects.create(**self.valid_bond_data)
        self.assertEqual(bond.cval, self.valid_bond_data["cval"])
        self.assertEqual(bond.ison, self.valid_bond_data["ison"])

    def test_create_bond_invalid_isin(self):
        invalid_data: dict = self.valid_bond_data.copy()
        invalid_data["cval"] = "INVALIDISIN"
        with self.assertRaises(ValidationError):
            Bond.objects.create(**invalid_data)

    def test_create_bond_missing_field(self):
        invalid_data: dict[str, str | Decimal | date | User] = (
            self.valid_bond_data.copy()
        )
        del invalid_data["ison"]
        with self.assertRaises(ValidationError):
            Bond.objects.create(**invalid_data)

    def test_create_bond_invalid_interest_rate(self):
        invalid_data: dict[str, str | Decimal | date | User] = (
            self.valid_bond_data.copy()
        )
        invalid_data["interest_rate"] = Decimal(-1.00)
        with self.assertRaises(ValidationError):
            Bond.objects.create(**invalid_data)

    def test_create_bond_invalid_date_format(self):
        invalid_data: dict[str, str | Decimal | date | User] = (
            self.valid_bond_data.copy()
        )
        invalid_data["purchase_date"] = "invalid-date"
        with self.assertRaises(ValidationError):
            Bond.objects.create(**invalid_data)
