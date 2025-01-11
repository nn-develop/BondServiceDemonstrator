from decimal import Decimal, getcontext
from datetime import datetime, timedelta, date
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Bond
from .serializers import BondSerializer
from bond_service_demonstrator.logger import logger


class BondViewSet(viewsets.ModelViewSet):
    # ViewSet for Bond operations (CRUD)
    queryset: QuerySet[Bond] = Bond.objects.all()
    serializer_class = BondSerializer
    permission_classes: list[type[IsAuthenticated]] = [IsAuthenticated]

    def perform_create(self, serializer: BondSerializer) -> None:
        """Assigns the logged-in user as the owner and saves the bond."""
        logger.debug(f"Creating a new bond for user {self.request.user}")
        created_bond: Bond = serializer.save(owner=self.request.user)
        logger.info(f"Bond created with name: {created_bond.ison}")

    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """Returns a list of bonds belonging to the current user."""
        logger.debug(f"Listing bonds for user {request.user}")
        queryset: QuerySet = self.get_queryset().filter(owner=request.user)
        serializer: BondSerializer = self.get_serializer(queryset, many=True)
        logger.debug(f"Found {len(queryset)} bonds for user {request.user.username}")
        return Response(serializer.data)

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """Fetches a specific bond owned by the user."""
        logger.debug(
            f"Retrieving bond with ID {kwargs['pk']} for user {request.user.username}"
        )
        try:
            bond: Bond = get_object_or_404(Bond, pk=kwargs["pk"], owner=request.user)
            serializer: BondSerializer = self.get_serializer(bond)
            logger.debug(f"Bond retrieved: {bond.ison}")
            return Response(serializer.data)
        except NotFound as e:
            logger.error(
                f"Bond not found with ID {kwargs['pk']} for user {request.user.username}"
            )
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving bond with ID {kwargs['pk']}: {e}")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """Updates a bond if owned by the current user."""
        logger.debug(
            f"Updating bond with ID {kwargs['pk']} for user {request.user.username}"
        )
        try:
            bond: Bond = get_object_or_404(Bond, pk=kwargs["pk"], owner=request.user)
            serializer: BondSerializer = self.get_serializer(
                bond, data=request.data, partial=True
            )

            serializer.is_valid(raise_exception=True)

            response: Response = super().update(request, *args, **kwargs)
            logger.info(f"Bond updated with ID {kwargs['pk']}")
            return response
        except NotFound as e:
            logger.error(
                f"Bond not found with ID {kwargs['pk']} for user {request.user.username}"
            )
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating bond with ID {kwargs['pk']}: {e}")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """Deletes a bond if owned by the current user."""
        logger.debug(
            f"Deleting bond with ID {kwargs['pk']} for user {request.user.username}"
        )
        try:
            get_object_or_404(Bond, pk=kwargs["pk"], owner=request.user)
            response: Response = super().destroy(request, *args, **kwargs)
            logger.info(f"Bond with ID {kwargs['pk']} deleted")
            return response
        except NotFound as e:
            logger.error(
                f"Bond not found with ID {kwargs['pk']} for user {request.user.username}"
            )
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting bond with ID {kwargs['pk']}: {e}")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class PortfolioAnalysisView(APIView):
    # Endpoint for portfolio analysis
    permission_classes: list[type[IsAuthenticated]] = [IsAuthenticated]

    @staticmethod
    def is_near_maturity(maturity_date) -> bool:
        """Checks if the bond is near maturity (within 30 days)."""
        return maturity_date <= datetime.now().date() + timedelta(days=30)

    @staticmethod
    def future_value(
        value: Decimal, interest_rate: Decimal, maturity_date: date
    ) -> Decimal:
        """Calculates the future value of a bond based on interest rate and maturity."""
        getcontext().prec = 10
        time_to_maturity: Decimal = Decimal(
            (maturity_date - date.today()).days
        ) / Decimal(365.0)
        return Decimal(value) * (
            Decimal(1) + (Decimal(interest_rate) / Decimal(100)) * time_to_maturity
        )

    def get(self, request: Request) -> Response:
        """Performs portfolio analysis for the current user's bonds."""
        logger.debug(f"Performing portfolio analysis for user {request.user}")
        bonds: QuerySet[Bond] = Bond.objects.filter(owner=request.user)

        if not bonds.exists():
            logger.info(
                f"No bonds found for user {request.user}, returning default analysis"
            )
            return Response(
                {
                    "average_interest_rate": 0,
                    "nearest_maturity_bond": None,
                    "total_value": 0,
                    "future_value": 0,
                },
                status=status.HTTP_200_OK,
            )

        total_interest_rate: Decimal | float = sum(bond.interest_rate for bond in bonds)
        average_interest_rate: Decimal | float = total_interest_rate / len(bonds)

        nearest_bond: Bond = min(bonds, key=lambda bond: bond.maturity_date)

        total_value: Decimal | float = sum(bond.tval for bond in bonds)
        future_value: Decimal | float = sum(
            self.future_value(bond.tval, bond.interest_rate, bond.maturity_date)
            for bond in bonds
        )

        logger.debug(f"Portfolio analysis for user {request.user.username}:")
        logger.debug(f"Average Interest Rate: {average_interest_rate}")
        logger.debug(f"Nearest Maturity Bond: {nearest_bond.ison}")
        logger.debug(f"Total Value: {total_value}")
        logger.debug(f"Future Value: {future_value}")

        return Response(
            {
                "average_interest_rate": average_interest_rate,
                "nearest_maturity_bond": nearest_bond.ison,
                "total_value": total_value,
                "future_value": future_value,
            },
            status=status.HTTP_200_OK,
        )
