"""The De Dietrich C-230 Eco integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .diematic_bolier import DiematicBoiler
from . import schedule

PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
    # "timer_programmer",
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Diematic from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    if not (diematic_boiler := hass.data[DOMAIN].get(entry.entry_id)):
        # Create IPP instance for this entry
        diematic_boiler = DiematicBoiler(
            hass,
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            tls=entry.data[CONF_SSL],
            verify_ssl=entry.data[CONF_VERIFY_SSL],
        )
        hass.data[DOMAIN][entry.entry_id] = diematic_boiler

    await diematic_boiler.coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await schedule.async_setup(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
