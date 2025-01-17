from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Bond
from .services.cdcp_service import CDCPService
from bond_service_demonstrator.logger import logger


class BondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bond
        fields: str = "__all__"
        read_only_fields: list[str] = ["owner"]
