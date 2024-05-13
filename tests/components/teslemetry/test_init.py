"""Test the Tessie init."""

from freezegun.api import FrozenDateTimeFactory
import pytest
from tesla_fleet_api.exceptions import (
    InvalidToken,
    SubscriptionRequired,
    TeslaFleetError,
    VehicleOffline,
)

from homeassistant.components.teslemetry.coordinator import VEHICLE_INTERVAL
from homeassistant.components.teslemetry.models import TeslemetryData
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import setup_platform

from tests.common import async_fire_time_changed

ERRORS = [
    (InvalidToken, ConfigEntryState.SETUP_ERROR),
    (SubscriptionRequired, ConfigEntryState.SETUP_ERROR),
    (TeslaFleetError, ConfigEntryState.SETUP_RETRY),
]


async def test_load_unload(hass: HomeAssistant) -> None:
    """Test load and unload."""

    entry = await setup_platform(hass)
    assert entry.state is ConfigEntryState.LOADED
    assert isinstance(entry.runtime_data, TeslemetryData)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert not hasattr(entry, "runtime_data")


@pytest.mark.parametrize(("side_effect", "state"), ERRORS)
async def test_init_error(
    hass: HomeAssistant, mock_products, side_effect, state
) -> None:
    """Test init with errors."""

    mock_products.side_effect = side_effect
    entry = await setup_platform(hass)
    assert entry.state is state


# Vehicle Coordinator
async def test_vehicle_refresh_offline(
    hass: HomeAssistant, mock_vehicle_data, freezer: FrozenDateTimeFactory
) -> None:
    """Test coordinator refresh with an error."""
    entry = await setup_platform(hass, [Platform.CLIMATE])
    assert entry.state is ConfigEntryState.LOADED
    mock_vehicle_data.assert_called_once()
    mock_vehicle_data.reset_mock()

    mock_vehicle_data.side_effect = VehicleOffline
    freezer.tick(VEHICLE_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    mock_vehicle_data.assert_called_once()


@pytest.mark.parametrize(("side_effect", "state"), ERRORS)
async def test_vehicle_refresh_error(
    hass: HomeAssistant, mock_vehicle_data, side_effect, state
) -> None:
    """Test coordinator refresh with an error."""
    mock_vehicle_data.side_effect = side_effect
    entry = await setup_platform(hass)
    assert entry.state is state


# Test Energy Live Coordinator
@pytest.mark.parametrize(("side_effect", "state"), ERRORS)
async def test_energy_live_refresh_error(
    hass: HomeAssistant, mock_live_status, side_effect, state
) -> None:
    """Test coordinator refresh with an error."""
    mock_live_status.side_effect = side_effect
    entry = await setup_platform(hass)
    assert entry.state is state


# Test Energy Site Coordinator
@pytest.mark.parametrize(("side_effect", "state"), ERRORS)
async def test_energy_site_refresh_error(
    hass: HomeAssistant, mock_site_info, side_effect, state
) -> None:
    """Test coordinator refresh with an error."""
    mock_site_info.side_effect = side_effect
    entry = await setup_platform(hass)
    assert entry.state is state
