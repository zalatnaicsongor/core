"""Describe group states."""

from typing import TYPE_CHECKING

from homeassistant.const import STATE_OK, STATE_PROBLEM
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.components.group import GroupIntegrationRegistry


@callback
def async_describe_on_off_states(
    hass: HomeAssistant, registry: "GroupIntegrationRegistry"
) -> None:
    """Describe group on off states."""
    registry.on_off_states(DOMAIN, {STATE_PROBLEM}, STATE_PROBLEM, STATE_OK)
