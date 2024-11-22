"""Support for setting values to the boiler registers."""

import asyncio
import logging

from diematic_client import DiematicError, DiematicStatus

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .diematic_bolier import DiematicBoiler
from .entity import DiematicEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add number entities."""
    diematic_boiler: DiematicBoiler = hass.data[DOMAIN][config_entry.entry_id]

    if (unique_id := config_entry.unique_id) is None:
        unique_id = config_entry.unique_id

    config = await diematic_boiler.boiler_config()

    numbers: list[NumberEntity] = [
        DiematicNumber(
            config_entry.entry_id,
            unique_id,
            diematic_boiler,
            cal["name"],
            cal["desc"],
            float(cal["step"]),
            float(cal["max"]),
            float(cal["min"]),
        )
        for cal in config
        if (
            "ha" in list(cal)
            and cal["ha"]
            and "unit" in list(cal)
            and (
                cal["unit"] == "CelsiusTemperature"
                or cal["unit"] == "°C"
                or cal["unit"] == "K"
            )
            and "step" in list(cal)
            and "max" in list(cal)
            and "min" in list(cal)
        )
    ]

    async_add_entities(numbers, True)


class DiematicNumber(DiematicEntity, NumberEntity):
    """Define a numeric parameter that can be set to the boiler."""

    def __init__(
        self,
        entry_id: str,
        unique_id: str,
        diematic_boiler: DiematicBoiler,
        variable: str,
        name: str,
        step: float,
        max_value: float,
        min_value: float,
    ) -> None:
        """Initialize a Diematic Number."""
        self.variable = variable
        self._attr_native_step = step
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value
        self._attr_unique_id = f"{unique_id}_{variable}"
        self._attr_native_unit_of_measurement = "°C"
        super().__init__(
            diematic_boiler=diematic_boiler,
            entry_id=entry_id,
            icon="mdi:thermometer",
            name=name,
            device_id=unique_id,
        )

    @property
    def native_value(self) -> float:
        """Obtain the native value."""
        return self.coordinator.data.variables[self.variable]

    async def async_set_native_value(self, value: float) -> None:
        """Set the native value asynchronusly."""
        try:
            result = await self._diematic_boiler.update_boiler_register(
                self.variable, value
            )
            if result == DiematicStatus.OK:
                i = 0
                while i < 20:
                    i += 1
                    await asyncio.sleep(1)
                    readresult = await self._diematic_boiler.read_boiler_register(
                        self.variable
                    )
                    if (
                        "status" in readresult
                        and readresult["status"] == "read"
                        and readresult["value"] == value
                    ):
                        self.async_schedule_update_ha_state(True)
                        break
            else:
                _LOGGER.error(
                    "Setting parameter value '%s' returned error but no additional information",
                    self.variable,
                )
        except DiematicError as error:
            _LOGGER.error(
                "Error setting parameter '%s' value to diematic boiler: {%s}",
                self.variable,
                error,
            )
