"""Date platform for the Blacktown Bin Buddy integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from homeassistant.components.date import DateEntity, DateEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN
from .coordinator import BinBuddyCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BinBuddyDateEntityDescription(DateEntityDescription):
    """Describes a Bin Buddy date entity."""

    value_fn: Callable[[dict[str, date]], date | None]


# Define the entities for each waste type
ENTITIES: tuple[BinBuddyDateEntityDescription, ...] = (
    BinBuddyDateEntityDescription(
        key="red",
        name="General Waste",
        translation_key="general_waste",
        icon="mdi:trash-can",
        value_fn=lambda data: data.get("red"),
    ),
    BinBuddyDateEntityDescription(
        key="yellow",
        name="Recycling",
        translation_key="recycling",
        icon="mdi:recycle",
        value_fn=lambda data: data.get("yellow"),
    ),
    BinBuddyDateEntityDescription(
        key="green",
        name="Food and Garden Waste",
        translation_key="food_and_garden_waste",
        icon="mdi:leaf",
        value_fn=lambda data: data.get("green"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the date entities from a config entry."""
    coordinator: BinBuddyCoordinator = entry.runtime_data
    _LOGGER.debug("Setting up date entities %s", coordinator.data)
    # Create entities if they have data from the initial refresh
    async_add_entities(
        BinBuddyDateEntity(coordinator, description)
        for description in ENTITIES
        if description.key in coordinator.data
    )


class BinBuddyDateEntity(CoordinatorEntity[BinBuddyCoordinator], DateEntity):
    """Represents a bin collection date."""

    _attr_has_entity_name = True
    entity_description: BinBuddyDateEntityDescription

    def __init__(
        self,
        coordinator: BinBuddyCoordinator,
        description: BinBuddyDateEntityDescription,
    ) -> None:
        """Initialize the date entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "Bin Collection",
            "manufacturer": "Blacktown City Council",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> date | None:
        """Return the next collection date."""
        return self.entity_description.value_fn(self.coordinator.data)
