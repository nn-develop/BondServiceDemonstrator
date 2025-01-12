from decimal import Decimal
from datetime import date
from django.db.models import QuerySet
from ..models import Bond


class PortfolioAnalysisService:

    @staticmethod
    def future_value(
        value: Decimal, interest_rate: Decimal, maturity_date: date
    ) -> Decimal:
        """Calculates the future value of a bond based on interest rate and maturity."""
        time_to_maturity: Decimal = Decimal(
            (maturity_date - date.today()).days
        ) / Decimal(365.0)
        return value * (Decimal(1) + (interest_rate / Decimal(100)) * time_to_maturity)

    @staticmethod
    def average_interest_rate(bonds) -> Decimal:
        """Calculates the average interest rate for the portfolio."""
        total_interest_rate: Decimal = sum(
            (Decimal(bond.interest_rate) for bond in bonds), start=Decimal(0)
        )
        return total_interest_rate / Decimal(len(bonds)) if bonds else Decimal(0)

    @staticmethod
    def nearest_bond(bonds: QuerySet) -> Bond:
        """Finds the bond with the nearest maturity."""
        return min(bonds, key=lambda bond: bond.maturity_date)

    @staticmethod
    def total_value(bonds: QuerySet) -> Decimal:
        """Calculates the total value of the bonds."""
        return sum((Decimal(bond.tval) for bond in bonds), start=Decimal(0))

    @staticmethod
    def future_value_sum(bonds: QuerySet) -> Decimal:
        """Calculates the sum of the future values of the bonds."""
        return sum(
            (
                PortfolioAnalysisService.future_value(
                    bond.tval, bond.interest_rate, bond.maturity_date
                )
                for bond in bonds
            ),
            start=Decimal(0),
        )
