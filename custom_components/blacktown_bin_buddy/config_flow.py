"""Config flow for the bin_buddy integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import urllib.parse

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .council_service import CouncilService
from .const import DOMAIN, ADD_SEARCH_URL

_LOGGER = logging.getLogger(__name__)

ADDRESS_SEARCH_DATA = vol.Schema(
    {
        vol.Required("Search Address"): str,
    }
)


class BinBuddyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for bin_buddy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.search_results = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial step where user searches for their address."""
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            service = CouncilService(session)
            query = user_input["Search Address"]

            try:
                data = await service.search_address(query)

                if not data:
                    errors["base"] = "no_results"
                else:
                    items_list = data.get("Items", [])
                    self.search_results = {
                        result["AddressSingleLine"]: result for result in items_list
                    }
                    return await self.async_step_select_address()
            except Exception:
                _LOGGER.exception("Failed to connect to council address API")
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user", data_schema=ADDRESS_SEARCH_DATA, errors=errors
        )

    async def async_step_select_address(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the step where the user selects their address."""
        if user_input is not None:
            selected_display_name = user_input["Select Address"]

            # Get the full data object we stored earlier
            final_address_data = self.search_results[selected_display_name]

            # Extract the GUID for the address
            address_guid = final_address_data.get("Id")

            # --- Create the config entry ---
            return self.async_create_entry(
                title=selected_display_name,  # A user-friendly title for the entry
                data={"id": address_guid},
            )
        # --- STEP 2: SCHEMA FOR THE SELECTION DROPDOWN ---
        # The keys of our stored search_results become the dropdown options
        SELECTION_SCHEMA = vol.Schema(
            {vol.Required("Select Address"): vol.In(list(self.search_results.keys()))}
        )

        return self.async_show_form(
            step_id="select_address", data_schema=SELECTION_SCHEMA
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
