"""De Dietrich C-230 Boiler sensors"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .diematic_bolier import DiematicBoiler
from .entity import DiematicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform"""
    # add_entries([DeDietrichC230Sensors()])
    diematic_boiler: DiematicBoiler = hass.data[DOMAIN][entry.entry_id]

    if (unique_id := entry.unique_id) is None:
        unique_id = entry.unique_id

    config = await diematic_boiler.boiler_config()

    sensors: list[SensorEntity] = []
    sensors.append(DiematicBoilerSensor(entry.entry_id, unique_id, diematic_boiler))

    for cal in config:
        if (
            "ha" in list(cal)
            and cal["ha"]
            and "unit" in list(cal)
            and cal["unit"] == "CelsiusTemperature"
            and "step" not in list(cal)
            and "max" not in list(cal)
            and "min" not in list(cal)
        ):
            sensors.append(
                DiematicBoilerTempSensor(
                    entry.entry_id, unique_id, diematic_boiler, cal["name"], cal["desc"]
                )
            )

    async_add_entities(sensors, True)


class DiematicSensor(DiematicEntity, SensorEntity):
    """Defines a Diematic sensor."""

    def __init__(
        self,
        *,
        diematic_boiler: DiematicBoiler,
        enabled_default: bool = True,
        entry_id: str,
        unique_id: str,
        icon: str,
        key: str,
        name: str,
        unit_of_measurement: str | None = None,
    ) -> None:
        """Initialize Diematic sensor."""
        self._key = key
        self._attr_unique_id = f"{unique_id}_{key}"
        self._attr_native_unit_of_measurement = unit_of_measurement

        super().__init__(
            entry_id=entry_id,
            device_id=unique_id,
            diematic_boiler=diematic_boiler,
            name=name,
            icon=icon,
            enabled_default=enabled_default,
        )


class DiematicBoilerSensor(DiematicSensor):
    """Defines a Diematic Boiler sensor."""

    def __init__(
        self, entry_id: str, unique_id: str, diematic_boiler: DiematicBoiler
    ) -> None:
        """Initialize Diematic Boiler sensor."""
        super().__init__(
            diematic_boiler=diematic_boiler,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:boiler",
            key="boiler",
            name=diematic_boiler.coordinator.data.info.name,
            unit_of_measurement=None,
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor"""
        return self.coordinator.data.variables["error"]


class DiematicBoilerTempSensor(DiematicSensor):
    """Defines a sensor that measures temperature"""

    def __init__(
        self,
        entry_id: str,
        unique_id: str,
        diematic_boiler: DiematicBoiler,
        variable: str,
        name: str,
    ) -> None:
        self.variable = variable
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        super().__init__(
            diematic_boiler=diematic_boiler,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:thermometer",
            key=variable,
            name=name,
            unit_of_measurement="°C",
        )

    @property
    def native_value(self) -> int:
        return self.coordinator.data.variables[self.variable]
