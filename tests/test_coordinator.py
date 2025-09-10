"""Tests for the BinBuddyCoordinator."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.blacktown_bin_buddy.coordinator import BinBuddyCoordinator
from custom_components.blacktown_bin_buddy.council_service import CannotConnect

MOCK_ENTRY_DATA = {"id": "test-geo-id"}
MOCK_WASTE_DATA = {"red": date(2025, 9, 16)}


class MockConfigEntry(MagicMock):
    """Mock ConfigEntry."""

    def __init__(self, data):
        super().__init__()
        self.data = data


@pytest.fixture
def mock_hass():
    """Fixture for HomeAssistant."""
    return MagicMock(spec=HomeAssistant)


@pytest.fixture
def mock_config_entry():
    """Fixture for a mock config entry."""
    return MockConfigEntry(MOCK_ENTRY_DATA)


@patch("custom_components.blacktown_bin_buddy.coordinator.async_get_clientsession")
async def test_coordinator_initialization(mock_get_session, mock_hass, mock_config_entry):
    """Test coordinator initialization."""
    coordinator = BinBuddyCoordinator(mock_hass, mock_config_entry)
    assert coordinator.geolocation_id == "test-geo-id"
    assert coordinator.update_interval == timedelta(hours=24)
    mock_get_session.assert_called_once_with(mock_hass)


@patch("custom_components.blacktown_bin_buddy.coordinator.CouncilService")
@patch("custom_components.blacktown_bin_buddy.coordinator.async_get_clientsession")
async def test_async_update_data_success(
    mock_get_session, mock_service_class, mock_hass, mock_config_entry
):
    """Test successful data update."""
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.get_waste_collection_data = AsyncMock(
        return_value=MOCK_WASTE_DATA
    )

    coordinator = BinBuddyCoordinator(mock_hass, mock_config_entry)
    data = await coordinator._async_update_data()

    assert data == MOCK_WASTE_DATA
    mock_service_instance.get_waste_collection_data.assert_called_once_with(
        "test-geo-id"
    )


@patch("custom_components.blacktown_bin_buddy.coordinator.CouncilService")
@patch("custom_components.blacktown_bin_buddy.coordinator.async_get_clientsession")
async def test_async_update_data_failure(
    mock_get_session, mock_service_class, mock_hass, mock_config_entry
):
    """Test data update failure due to CannotConnect."""
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.get_waste_collection_data = AsyncMock(
        side_effect=CannotConnect("Test connection error")
    )

    coordinator = BinBuddyCoordinator(mock_hass, mock_config_entry)

    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator._async_update_data()

    assert "Failed to connect" in str(excinfo.value)
