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
from .coordinator import DiematicCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Diematic from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    if not (coordinator := hass.data[DOMAIN].get(entry.entry_id)):
        # Create IPP instance for this entry
        coordinator = DiematicCoordinator(
            hass,
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            tls=entry.data[CONF_SSL],
            verify_ssl=entry.data[CONF_VERIFY_SSL],
        )
        hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
