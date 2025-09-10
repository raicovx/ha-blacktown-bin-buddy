"""Data update coordinator for the Blacktown Bin Buddy integration."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .council_service import CannotConnect, CouncilService

_LOGGER = logging.getLogger(__name__)


class BinBuddyCoordinator(DataUpdateCoordinator[dict[str, date]]):
    """Manages fetching data from the council API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data update coordinator."""
        session = async_get_clientsession(hass)
        self.service: CouncilService = CouncilService(session)
        self.geolocation_id = entry.data["id"]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=24),  # Check for new dates once a day
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict[str, date]:
        """Fetch the latest waste collection dates from the service."""
        try:
            return await self.service.get_waste_collection_data(self.geolocation_id)
        except CannotConnect as err:
            raise UpdateFailed("Failed to connect to the council's service") from err
