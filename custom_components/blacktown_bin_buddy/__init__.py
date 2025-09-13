"""The bin_buddy integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .const import DOMAIN
from .council_service import CouncilService
from .coordinator import BinBuddyCoordinator


# supporting date platform - each waste type will have a separate entity
_PLATFORMS: list[Platform] = [Platform.DATE]

type BlacktownBinBuddyConfigEntry = ConfigEntry[BinBuddyCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: BlacktownBinBuddyConfigEntry
) -> bool:
    """Set up bin_buddy from a config entry."""

    coordinator = BinBuddyCoordinator(hass, entry)
    # populate data immediately
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    @callback
    def _async_update_at_one_am(now):
        """Request a refresh of the coordinator at 1:00 AM."""
        hass.async_create_task(coordinator.async_request_refresh())

    # Schedule the daily update at 1:00 AM
    remove_listener = async_track_time_change(
        hass, _async_update_at_one_am, hour=1, minute=0, second=0
    )

    # Register the listener removal callback to run when the entry is unloaded
    entry.async_on_unload(remove_listener)


    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: BlacktownBinBuddyConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
