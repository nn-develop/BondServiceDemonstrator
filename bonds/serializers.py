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

    def validate(
        self, attrs: dict[str, str | Decimal | date]
    ) -> dict[str, str | Decimal | date]:
        """
        Main validation method that orchestrates the validation process by:
        1. Retrieving and validating the ISIN (cval) if it exists.
        2. Fetching bond data from the CDCP API using the ISIN.
        3. Ensuring the CDCP data is complete and valid.
        4. Preparing the bond data, converting it to the correct types and merging with the original attrs.
        """
        logger.debug(f"Starting validation for bond data: {attrs}")

        # 1. Retrieve and validate the ISIN (cval) field if it exists.
        cval: str = str(attrs.get("cval", ""))

        if cval:
            # 2. Fetch bond data from CDCP API based on the ISIN.
            cdcp_service = CDCPService()
            cdcp_service.cdcp_data = cdcp_service.get_cdcp_bond_data(cval)

            # 3. Validate that the CDCP bond data contains all necessary fields and values.
            cleaned_cdcp_bond: dict[str, str] = (
                cdcp_service.validate_and_clean_cdcp_data()
            )

            # 4. Prepare the CDCP bond data by converting its fields to the appropriate types and merging with the original attrs.
            prepared_cdcp_bond: dict[str, str | Decimal | date] = (
                cdcp_service.compare_bond_data(attrs)
            )
            logger.debug(f"Finished validation. Prepared data: {prepared_cdcp_bond}")

            # Merge the prepared CDCP bond data with the original attrs
            attrs.update(prepared_cdcp_bond)

        return attrs
