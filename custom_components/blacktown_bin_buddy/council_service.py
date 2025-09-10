"""A service to interface with the Blacktown Council waste collection API."""

from __future__ import annotations

from datetime import date, datetime
import logging
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from .const import ADD_SEARCH_URL, WASTE_COLLECTION_DATES_URL, BIN_COLOUR_MAP

_LOGGER = logging.getLogger(__name__)


class CouncilServiceError(Exception):
    """Base exception for council service errors."""


class CannotConnect(CouncilServiceError):
    """Exception to indicate a connection error."""


class CouncilService:
    """A class to interface with the council's waste collection service."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the council service."""
        self._session = session

    async def search_address(self, search_term: str) -> list[dict[str, Any]]:
        """
        Search for an address and return a list of matching suggestions.

        Args:
            search_term: The address to search for.

        Returns:
            A list of address suggestions, where each suggestion is a dictionary.
            Example: [{'Id': 'GUID', 'AddressSingleLine': '123 Example St' }]

        Raises:
            CannotConnect: If there is a network-related error.
            CouncilServiceError: For other unexpected errors.
        """
        search_url = f"{ADD_SEARCH_URL}{search_term}"
        try:
            async with self._session.get(search_url) as response:
                response.raise_for_status()
                # The API returns a list of address suggestions
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error searching for address: %s", err)
            raise CannotConnect from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during address search")
            raise CouncilServiceError from err

    async def get_waste_collection_data(self, geolocation_id: str) -> dict[str, date]:
        """
        Fetch and parse waste collection dates for a given geolocation ID.

        Args:
            geolocation_id: The unique identifier for the address.

        Returns:
            A dictionary mapping waste type to its next collection date object.
            Example: {'general-waste': datetime.date(2025, 9, 16)}

        Raises:
            CannotConnect: If there is a network-related error.
            CouncilServiceError: For other unexpected errors.
        """
        url = f"{WASTE_COLLECTION_DATES_URL}{geolocation_id}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                html_content = await response.json()
                return self._parse_waste_dates_html(html_content["responseContent"])
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching waste collection dates: %s", err)
            raise CannotConnect from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching waste dates")
            raise CouncilServiceError from err

    def _parse_waste_dates_html(self, html_content: str) -> dict[str, date]:
        """
        Parse the HTML content to extract waste collection dates.

        Note: This parser is based on the observed HTML structure of the council's
        website. If the website layout changes, this function will need to be updated.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        collection_dates: dict[str, date] = {}

        # Find all service containers with the 'regular-service' class
        service_elements = soup.find_all("div", class_="regular-service")
        _LOGGER.info("Found %d service elements in HTML", len(service_elements))
        for element in service_elements:
            element_classes = element.get("class", [])
            waste_type = None

            # Determine waste type from bin color class
            for color, type_name in BIN_COLOUR_MAP.items():
                if type_name in element_classes:
                    waste_type = color
                    break

            if not waste_type:
                continue

            # Find the div that contains the date information
            date_container = element.find("div", class_="next-service")

            if date_container:
                pickup_date_str = date_container.text.strip()
                try:
                    # Expected format: "Fri 12/9/2025", so we split and take the date part
                    date_part = pickup_date_str.split(" ")[1]
                    pickup_date = datetime.strptime(date_part, "%d/%m/%Y").date()
                    collection_dates[waste_type] = pickup_date
                except (IndexError, ValueError) as e:
                    _LOGGER.warning(
                        "Could not parse date string: '%s'. Error: %s",
                        pickup_date_str,
                        e,
                    )
                    # Handle special message currently being displayed for green waste - it is picked up on the same day as red waste
                    if (
                        collection_dates.get("red") is not None
                        and waste_type == "green"
                    ):
                        collection_dates["green"] = collection_dates["red"]

        if not collection_dates:
            _LOGGER.warning(
                "Could not parse any collection dates from the HTML content"
            )

        return collection_dates
