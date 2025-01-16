import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from bond_service_demonstrator.logger import logger


class Bond(models.Model):
    """Represents a bond."""

    cval = models.CharField(max_length=12)
    ison = models.CharField(max_length=255)
    tval = models.DecimalField(max_digits=10, decimal_places=2)
    pdcp = models.CharField(max_length=50)
    regdt = models.DateField()
    eico = models.CharField(max_length=20)
    ename = models.CharField(max_length=255)
    elei = models.CharField(max_length=255)
    purchase_date = models.DateField()
    maturity_date = models.DateField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    interest_frequency = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return the ISIN of the bond."""
        return self.ison

    @staticmethod
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

    @staticmethod
    def validate_positive(value) -> None:
        """
        Validates the value of the bond to ensure it is positive.
        """
        if value < 0:
            raise ValidationError("The value must be positive.")
        return None

    def clean_fields(self, exclude=None):
        """
        Custom validation logic for individual fields in the Bond model.
        """
        super().clean_fields(exclude=exclude)
        self.validate_cval_format(self.cval)
        self.validate_positive(self.interest_rate)
        return None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
