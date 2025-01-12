import re
import requests
from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Bond
from bond_service_demonstrator.logger import logger


class BondSerializer(serializers.ModelSerializer):
    CDCP_FIELDS: list[str] = [
        "cval",
        "ison",
        "tval",
        "pdcp",
        "regdt",
        "eico",
        "ename",
        "elei",
    ]

    class Meta:
        model = Bond
        fields: str = "__all__"
        read_only_fields: list[str] = ["owner"]

    def get_cval(self, attrs: dict[str, str | Decimal | date]):
        if "cval" in attrs:
            self.validate_cval(str(attrs["cval"]))
        elif pk_from_context := self.context["view"].kwargs.get("pk"):
            bond: Bond = get_object_or_404(Bond, pk=pk_from_context)
            attrs["cval"] = bond.cval
            logger.debug(f"Retrieved cval from context: {attrs['cval']}")
        return attrs

    def validate_cval(self, value: str) -> str:
        """
        Validates the ISIN (cval) field to ensure it has the correct length and format.
        """
        logger.debug(f"Validating ISIN value: {value}")
        if len(value) != 12 or not re.match(r"^[A-Z]{2}[0-9]{10}$", value):
            logger.error(f"Invalid ISIN format for value: {value}")
            raise serializers.ValidationError(
                "Invalid ISIN format. ISIN must be 12 characters long, start with 2 letters, and followed by 10 digits."
            )
        return value

    def get_cdcp_bond_data(self, isin: str) -> dict[str, str]:
        """
        Fetch bond data from the CDCP API for a given ISIN.
        """
        api_url: str = f"https://www.cdcp.cz/isbpublicjson/api/VydaneISINy?isin={isin}"
        logger.debug(f"Calling CDCP API to validate ISIN: {isin}")
        try:
            response: requests.Response = requests.get(api_url)
            response.raise_for_status()

            logger.debug(f"CDCP API response status: {response.status_code}")
            data: dict = response.json()
            if "vydaneisiny" in data and data["vydaneisiny"]:
                logger.debug(
                    f"CDCP data found for ISIN {isin}: {data['vydaneisiny'][0]}"
                )
                return data["vydaneisiny"][0]
            else:
                logger.error(f"ISIN {isin} not found in CDCP data.")
                raise serializers.ValidationError("ISIN not found in CDCP data.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while validating ISIN {isin}: {e}")
            raise serializers.ValidationError("Error occurred while validating ISIN.")

    def validate_and_return_complete_cdcp_data(
        self, cdcp_bond: dict[str, str]
    ) -> dict[str, str]:
        """
        Validates that all CDCP_FIELDS are present and non-empty in the CDCP API response,
        and returns the cleaned data if complete.
        """
        missing_or_empty: list[str] = [
            field for field in self.CDCP_FIELDS if not cdcp_bond.get(field)
        ]
        if missing_or_empty:
            logger.error(
                f"Missing or empty fields in CDCP data: {', '.join(missing_or_empty)}"
            )
            raise serializers.ValidationError(
                f"CDCP data is missing or contains empty values for the following fields: {', '.join(missing_or_empty)}"
            )

        cleaned_cdcp_bond: dict[str, str] = {
            key: value for key, value in cdcp_bond.items() if value is not None
        }

        logger.debug(f"CDCP data validated successfully: {cdcp_bond}")
        return cleaned_cdcp_bond

    def compare_bond_data(
        self,
        cdcp_bond: dict[str, str],
        existing_data: dict[str, str | Decimal | date] | None = None,
    ) -> dict[str, str | Decimal | date]:
        """
        Prepares CDCP data by converting its fields to match the expected types in the serializer.
        If the bond is being updated, it will merge existing data with the updated CDCP data.
        """
        logger.debug(f"Preparing bond data: {cdcp_bond}")
        prepared_data: dict[str, str | Decimal | date] = existing_data or {}

        for key, value in cdcp_bond.items():
            match (prepared_data.get(key), value):
                case (existing_value, new_value) if existing_value != new_value:
                    logger.debug(
                        f"Data for {key} differ: existing value = {existing_value}, new value = {new_value}. Keeping existing value."
                    )
                case _:
                    prepared_data[key] = value

        logger.debug(f"Bond data prepared: {cdcp_bond}")
        return prepared_data

    def validate(
        self, attrs: dict[str, str | Decimal | date]
    ) -> dict[str, str | Decimal | date]:
        """
        Main validation method that orchestrates the validation process by:
        1. Retrieving and validating the ISIN (cval).
        2. Fetching bond data from the CDCP API using the validated ISIN.
        3. Ensuring the CDCP data is complete and valid.
        4. Preparing the bond data, converting it to the correct types and merging with any existing data if applicable.
        """
        logger.debug(f"Starting validation for bond data: {attrs}")

        # 1. Retrieve and validate the ISIN (cval) field.
        self.get_cval(attrs)
        cval: str = str(attrs["cval"])

        # 2. Fetch bond data from CDCP API based on the ISIN.
        # This method retrieves bond-related data from the external CDCP API.
        cdcp_bond: dict[str, str] = self.get_cdcp_bond_data(cval)

        # 3. Validate that the CDCP bond data contains all necessary fields and values.
        # This ensures that the required fields are present and non-empty.
        cleaned_cdcp_bond: dict[str, str] = self.validate_and_return_complete_cdcp_data(
            cdcp_bond
        )

        # 4. Prepare the CDCP bond data by converting its fields to the appropriate types and merging with existing data.
        # This ensures that the data is properly formatted for the model and serializer.
        prepared_cdcp_bond: dict[str, str | Decimal | date] = self.compare_bond_data(
            cleaned_cdcp_bond, attrs
        )
        logger.debug(f"Finished validation. Prepared data: {prepared_cdcp_bond}")

        # Return the fully prepared and validated bond data.
        return prepared_cdcp_bond
