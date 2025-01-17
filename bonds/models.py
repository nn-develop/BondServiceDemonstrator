from datetime import date
from decimal import Decimal
import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from bond_service_demonstrator.logger import logger
from .services.cdcp_service import CDCPService


def validate_cval_format(value: str) -> None:
    """
    Validates the ISIN (cval) field to ensure it has the correct length and format.
    """
    logger.debug(f"Validating ISIN value: {value}")
    pattern = r"^(?P<country_code>[A-Z]{2})(?P<identifier>[0-9]{10})$"
    if len(value) != 12 or not re.match(pattern, value):
        logger.error(f"Invalid ISIN format for value: {value}")
        raise ValidationError(
            "Invalid ISIN format. ISIN must be 12 characters long, start with 2 letters, and followed by 10 digits."
        )
    return None


def validate_positive(value) -> None:
    """
    Validates the value of the bond to ensure it is positive.
    """
    if value < 0:
        raise ValidationError("The value must be positive.")
    return None


def validate_cval(value: str) -> None:
    """
    Validates the ISIN (cval) field to ensure it has the correct length, format, and matches CDCP data.
    """
    validate_cval_format(value)
    cdcp_service = CDCPService()
    cdcp_service.is_cdcp_bond_data_matching(value)
    return None


class Bond(models.Model):
    """Represents a bond."""

    cval = models.CharField(max_length=12, validators=[validate_cval])
    ison = models.CharField(max_length=255)
    tval = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive]
    )
    pdcp = models.CharField(max_length=50)
    regdt = models.DateField()
    eico = models.CharField(max_length=20)
    ename = models.CharField(max_length=255)
    elei = models.CharField(max_length=255)
    purchase_date = models.DateField()
    maturity_date = models.DateField()
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[validate_positive]
    )
    interest_frequency = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return the ISIN of the bond."""
        return self.ison

    def save(self, *args, **kwargs):
        """Override the save method to validate the ISIN field."""
        self.full_clean()
        super().save(*args, **kwargs)
