from django.db import models
from django.contrib.auth.models import User


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
