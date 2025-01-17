import requests
from django.core.exceptions import ValidationError
from bond_service_demonstrator.logger import logger


class CDCPService:
    API_URL_TEMPLATE = "https://www.cdcp.cz/isbpublicjson/api/VydaneISINy?isin={}"

    def is_cdcp_bond_data_matching(self, cval: str) -> bool:
        """
        Fetch bond data from the CDCP API for a given ISIN and compare if the cval matches.
        """
        data: dict = self._fetch_cdcp_data(cval)
        return self._is_cval_matching(data, cval)

    def _fetch_cdcp_data(self, cval: str) -> dict:
        """
        Fetch data from the CDCP API.
        """
        api_url: str = self.API_URL_TEMPLATE.format(cval)
        logger.debug(f"Calling CDCP API to acquire data for ISIN: {cval}")
        try:
            response: requests.Response = requests.get(api_url)
            logger.debug(f"CDCP API response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while fetching data for ISIN {cval}: {e}")
            raise ValidationError(
                f"Error occurred while fetching data from CDCP API for ISIN {cval}."
            )

    def _is_cval_matching(self, data: dict, cval: str) -> bool:
        """
        Check if the cval from the response matches the given cval.
        """
        if "vydaneisiny" in data and data["vydaneisiny"]:
            logger.debug(f"CDCP data found for ISIN {cval}: {data['vydaneisiny'][0]}")
            fetched_cval = data["vydaneisiny"][0].get("cval")
            if fetched_cval == cval:
                return True
            else:
                logger.error(
                    f"Fetched cval {fetched_cval} does not match provided cval {cval}."
                )
                return False
        else:
            logger.error(f"ISIN {cval} not found in CDCP data.")
            return False
