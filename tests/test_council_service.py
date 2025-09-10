"""Tests for the CouncilService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

import aiohttp
from datetime import date

from custom_components.blacktown_bin_buddy.council_service import (
    CouncilService,
    CannotConnect,
    CouncilServiceError,
)

MOCK_SEARCH_RESPONSE = {"Items": [{"Id": "123", "Text": "1 Test St"}]}
MOCK_WASTE_DATES_HTML = """
<div class="regular-service general-waste">
    <div class="service-image">
        <img src="/red-lid.png">
    </div>
    <div class="next-service">       
        Tuesday, 16 September 2025
    </div>
</div>
<div class="regular-service recycling">
    <div class="service-image">
        <img src="/yellow-lid.png">
    </div>
    <div class="next-service">        
        Tuesday, 23 September 2025
    </div>
</div>
"""
MOCK_WASTE_DATES_RESPONSE = {"responseContent": MOCK_WASTE_DATES_HTML}


@pytest.fixture
def mock_session():
    """Fixture for aiohttp client session."""
    session = MagicMock()
    session.get = AsyncMock()
    return session


async def test_search_address_success(mock_session):
    """Test successful address search."""
    mock_response = mock_session.get.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=MOCK_SEARCH_RESPONSE)
    mock_response.raise_for_status = MagicMock()

    service = CouncilService(mock_session)
    result = await service.search_address("1 Test St")

    mock_session.get.assert_called_once()
    assert result == MOCK_SEARCH_RESPONSE


async def test_search_address_connection_error(mock_session):
    """Test address search with a connection error."""
    mock_session.get.side_effect = aiohttp.ClientError("Test connection error")

    service = CouncilService(mock_session)
    with pytest.raises(CannotConnect):
        await service.search_address("1 Test St")


async def test_get_waste_collection_data_success(mock_session):
    """Test successful waste collection data fetch."""
    mock_response = mock_session.get.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=MOCK_WASTE_DATES_RESPONSE)
    mock_response.raise_for_status = MagicMock()

    service = CouncilService(mock_session)
    result = await service.get_waste_collection_data("12345")

    expected_data = {
        "red": date(2025, 9, 16),
        "yellow": date(2025, 9, 23),
    }

    assert result == expected_data


async def test_get_waste_collection_data_connection_error(mock_session):
    """Test waste data fetch with a connection error."""
    mock_session.get.side_effect = aiohttp.ClientError("Test connection error")

    service = CouncilService(mock_session)
    with pytest.raises(CannotConnect):
        await service.get_waste_collection_data("12345")


async def test_get_waste_collection_data_unexpected_error(mock_session):
    """Test waste data fetch with an unexpected error."""
    mock_session.get.side_effect = Exception("Unexpected error")

    service = CouncilService(mock_session)
    with pytest.raises(CouncilServiceError):
        await service.get_waste_collection_data("12345")


def test_parse_waste_dates_html():
    """Test parsing of the waste dates HTML."""
    service = CouncilService(MagicMock())
    result = service._parse_waste_dates_html(MOCK_WASTE_DATES_HTML)

    expected_data = {
        "red": date(2025, 9, 16),
        "yellow": date(2025, 9, 23),
    }
    assert result == expected_data
