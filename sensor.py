"""De Dietrich C-230 Boiler sensors"""
from __future__ import annotations
from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import DiematicCoordinator
from .const import DOMAIN
from .entity import DiematicEntity


def setup(hass: HomeAssistant, entry: ConfigEntry):
    """Setup called."""
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform"""
    # add_entries([DeDietrichC230Sensors()])
    coordinator: DiematicCoordinator = hass.data[DOMAIN][entry.entry_id]

    if (unique_id := entry.unique_id) is None:
        unique_id = entry.unique_id

    config = await coordinator.boiler_client.config()

    sensors: list[SensorEntity] = []
    sensors.append(DiematicBoilerSensor(entry.entry_id, unique_id, coordinator))
    for circuit in ("a", "acs"):
        for day_of_week in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            sensors.append(
                DiematicBoilerConfortSensor(
                    entry.entry_id, unique_id, coordinator, day_of_week, circuit
                )
            )
    for cal in config:
        if (
            "ha" in list(cal)
            and cal["ha"]
            and "unit" in list(cal)
            and cal["unit"] == "CelsiusTemperature"
        ):
            sensors.append(
                DiematicBoilerTempSensor(
                    entry.entry_id, unique_id, coordinator, cal["name"], cal["desc"]
                )
            )

    async_add_entities(sensors, True)


class DiematicSensor(DiematicEntity, SensorEntity):
    """Defines a Diematic sensor."""

    def __init__(
        self,
        *,
        coordinator: DiematicCoordinator,
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
            coordinator=coordinator,
            name=name,
            icon=icon,
            enabled_default=enabled_default,
        )


class DiematicBoilerSensor(DiematicSensor):
    """Defines a Diematic Boiler sensor."""

    def __init__(
        self, entry_id: str, unique_id: str, coordinator: DiematicCoordinator
    ) -> None:
        """Initialize Diematic Boiler sensor."""
        super().__init__(
            coordinator=coordinator,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:boiler",
            key="boiler",
            name=coordinator.data.info.name,
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
        coordinator: DiematicCoordinator,
        variable: str,
        name: str,
    ) -> None:
        self.variable = variable
        super().__init__(
            coordinator=coordinator,
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


class DiematicBoilerConfortSensor(DiematicSensor):
    """Defines a sensor that collects day/nignt bitmaps for onw day and one circuit into a 6 bytes single numeric value."""

    def __init__(
        self,
        entry_id: str,
        unique_id: str,
        coordinator: DiematicCoordinator,
        day_of_week: str,
        circuit: str,
    ) -> None:
        self.day_of_week = day_of_week
        self.circuit = circuit
        super().__init__(
            coordinator=coordinator,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:table-row",
            key=f"confort_{day_of_week}_{circuit}",
            name=f"Confort period for {day_of_week} and circuit {circuit}",
            unit_of_measurement=None,
        )

    @property
    def native_value(self) -> int:
        asbits = ""
        for starthour in range(0, 24):
            for startminute in ["00", "30"]:
                endhour = starthour if startminute == "00" else starthour + 1
                if endhour == 24:
                    endhour = 0
                endminute = "00" if startminute == "30" else "30"
                varname = f"{self.day_of_week}_{self.circuit}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                asbits += "1" if self.coordinator.data.variables[varname] else "0"

        return int(asbits, 2)
