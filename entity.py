"""Entities from the Diematic integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DiematicCoordinator


class DiematicEntity(CoordinatorEntity):
    """Defines a base Diematic entity."""

    def __init__(
        self,
        *,
        entry_id: str,
        device_id: str,
        coordinator: DiematicCoordinator,
        name: str,
        icon: str,
        enabled_default: bool = True,
    ) -> None:
        """Initialize the Diematic entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._entry_id = entry_id
        self._attr_name = name
        self._attr_icon = icon
        self._attr_entity_registry_enabled_default = enabled_default

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information about this Diematic device."""
        if self._device_id is None:
            return None

        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer=self.coordinator.data.info.manufacturer,
            model=self.coordinator.data.info.model,
            name=self.coordinator.data.info.name,
            sw_version=self.coordinator.data.info.version,
        )
