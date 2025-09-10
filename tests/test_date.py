"""Tests for the date platform of the Blacktown Bin Buddy integration."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.blacktown_bin_buddy.date import (
    async_setup_entry,
    BinBuddyDateEntity,
    ENTITIES,
)
from custom_components.blacktown_bin_buddy.coordinator import BinBuddyCoordinator

MOCK_COORDINATOR_DATA = {
    "red": date(2025, 9, 16),
    "yellow": date(2025, 9, 23),
    "green": date(2025, 10, 1),
}


@pytest.fixture
def mock_coordinator():
    """Fixture for a mock BinBuddyCoordinator."""
    coordinator = MagicMock(spec=BinBuddyCoordinator)
    coordinator.data = MOCK_COORDINATOR_DATA
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "test-entry-id"
    return coordinator


@pytest.fixture
def mock_hass():
    """Fixture for HomeAssistant."""
    return MagicMock(spec=HomeAssistant)


@pytest.fixture
def mock_add_entities():
    """Fixture for the add entities callback."""
    return MagicMock(spec=AddEntitiesCallback)


async def test_async_setup_entry(mock_hass, mock_coordinator, mock_add_entities):
    """Test the setup of date entities."""
    mock_config_entry = MagicMock()
    mock_config_entry.runtime_data = mock_coordinator

    await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)

    # Check that add_entities was called
    mock_add_entities.assert_called_once()

    # Get the list of entities that were added
    added_entities = mock_add_entities.call_args[0][0]

    # Ensure we have the correct number of entities
    assert len(list(added_entities)) == len(MOCK_COORDINATOR_DATA)


def test_bin_buddy_date_entity_properties(mock_coordinator):
    """Test properties of the BinBuddyDateEntity."""
    # Test with the 'red' bin description
    description = ENTITIES[0]
    assert description.key == "red"

    entity = BinBuddyDateEntity(mock_coordinator, description)

    # Test unique_id
    assert entity.unique_id == "test-entry-id_red"

    # Test device_info
    assert entity.device_info["identifiers"] == {("blacktown_bin_buddy", "test-entry-id")}
    assert entity.device_info["name"] == "Bin Collection"

    # Test native_value
    assert entity.native_value == date(2025, 9, 16)

    # Test a different entity to be sure
    description_green = ENTITIES[2]
    assert description_green.key == "green"
    entity_green = BinBuddyDateEntity(mock_coordinator, description_green)
    assert entity_green.native_value == date(2025, 10, 1)


def test_bin_buddy_date_entity_no_data(mock_coordinator):
    """Test entity behavior when its specific data is not available."""
    # Create a coordinator with missing data for one bin type
    mock_coordinator.data = {"red": date(2025, 9, 16)}

    # Test the 'yellow' bin, which has no data
    description = ENTITIES[1]
    assert description.key == "yellow"

    entity = BinBuddyDateEntity(mock_coordinator, description)

    # The native_value should be None
    assert entity.native_value is None
