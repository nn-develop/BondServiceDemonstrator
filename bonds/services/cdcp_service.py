import requests
from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from bonds.models import Bond
from bond_service_demonstrator.logger import logger


class CDCPService:
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

    cdcp_data: dict = {}

    def get_cdcp_bond_data(self, cval: str) -> dict[str, str]:
        """
        Fetch bond data from the CDCP API for a given ISIN.
        """
        api_url: str = f"https://www.cdcp.cz/isbpublicjson/api/VydaneISINy?isin={cval}"
        logger.debug(f"Calling CDCP API to aquire data for ISIN: {cval}")
        try:
            response: requests.Response = requests.get(api_url)
            response.raise_for_status()

            logger.debug(f"CDCP API response status: {response.status_code}")
            data: dict = response.json()

            if "vydaneisiny" in data and data["vydaneisiny"]:
                logger.debug(
                    f"CDCP data found for ISIN {cval}: {data['vydaneisiny'][0]}"
                )
                self.cdcp_data = data["vydaneisiny"][
                    0
                ]  # Update cdcp_data with fetched data
                return self.cdcp_data
            else:
                logger.error(f"ISIN {cval} not found in CDCP data.")
                raise serializers.ValidationError("ISIN not found in CDCP data.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while validating ISIN {cval}: {e}")
            raise serializers.ValidationError("Error occurred while validating ISIN.")

    def validate_and_clean_cdcp_data(self) -> dict[str, str]:
        """
        Validates that all CDCP_FIELDS are present and non-empty in the CDCP API response,
        and returns the cleaned data if complete.
        """
        missing_or_empty: list[str] = [
            field for field in self.CDCP_FIELDS if not self.cdcp_data.get(field)
        ]
        if missing_or_empty:
            logger.error(
                f"Missing or empty fields in CDCP data: {', '.join(missing_or_empty)}"
            )
            raise serializers.ValidationError(
                f"CDCP data is missing or contains empty values for the following fields: {', '.join(missing_or_empty)}"
            )

        cleaned_cdcp_bond: dict[str, str] = {
            key: value for key, value in self.cdcp_data.items() if value is not None
        }

        logger.debug(f"CDCP data validated successfully: {self.cdcp_data}")
        return cleaned_cdcp_bond

    def compare_bond_data(
        self,
        bond_data_to_compare: dict[str, str | Decimal | date] | None = None,
    ) -> dict[str, str | Decimal | date]:
        """
        Prepares CDCP data by converting its fields to match the expected types in the serializer.
        If the bond is being updated, it will merge existing data with the updated CDCP data.
        """
        logger.debug(f"Preparing bond data: {self.cdcp_data}")
        prepared_data: dict[str, str | Decimal | date] = bond_data_to_compare or {}

        for key, value in self.cdcp_data.items():
            match (prepared_data.get(key), value):
                case (existing_value, new_value) if existing_value != new_value:
                    logger.debug(
                        f"Data for {key} differ: existing value = {existing_value}, new value = {new_value}. Keeping existing value."
                    )
                case _:
                    prepared_data[key] = value

        logger.debug(f"Bond data prepared: {self.cdcp_data}")
        return prepared_data
