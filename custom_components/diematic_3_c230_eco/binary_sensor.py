"""De Dietrich C-230 Boiler binary sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .diematic_bolier import DiematicBoiler
from .entity import DiematicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform."""
    diematic_boiler: DiematicBoiler = hass.data[DOMAIN][entry.entry_id]

    if (unique_id := entry.unique_id) is None:
        unique_id = entry.unique_id

    config = await diematic_boiler.boiler_config()

    bitstypes = [
        bit
        for sub in config
        if "type" in list(sub) and "bits" in list(sub) and sub["type"] == "bits"
        for bit in sub["bits"]
    ]

    sensors: list[BinarySensorEntity] = []

    sensors.extend(
        DiematicBoilerBinarySensor(
            entry_id=entry.entry_id,
            unique_id=unique_id,
            diematic_boiler=diematic_boiler,
            variable=f"io_circ_{circuit}_pump_on",
            name=f"Pump circuit {circuit}",
            icon="mdi:pump",
        )
        for circuit in ("a", "b", "c")
        if f"monday_{circuit}_0000_0030" in bitstypes
    )

    sensors.append(
        DiematicBoilerBinarySensor(
            entry_id=entry.entry_id,
            unique_id=unique_id,
            diematic_boiler=diematic_boiler,
            variable="io_boiler_pump",
            name="Boiler Pump",
            icon="mdi:pump",
        )
    )

    sensors.append(
        DiematicBoilerBinarySensor(
            entry_id=entry.entry_id,
            unique_id=unique_id,
            diematic_boiler=diematic_boiler,
            variable="io_dhw_pump_on",
            name="DHW Pump",
            icon="mdi:pump",
        )
    )

    sensors.extend(
        DiematicBoilerBinarySensor(
            entry_id=entry.entry_id,
            unique_id=unique_id,
            diematic_boiler=diematic_boiler,
            variable=f"io_aux_pump_{n}_on",
            name=f"Aux {n} Pump",
            icon="mdi:pump",
        )
        for n in ("1", "2", "3")
    )

    sensors.append(
        DiematicBoilerBinarySensor(
            entry_id=entry.entry_id,
            unique_id=unique_id,
            diematic_boiler=diematic_boiler,
            variable="io_secondary_pump",
            name="Secondary Pump",
            icon="mdi:pump",
        )
    )

    async_add_entities(sensors, True)


class DiematicBoilerBinarySensor(DiematicEntity, BinarySensorEntity):
    """Defines a diematic binary sensor."""

    def __init__(
        self,
        *,
        entry_id: str,
        unique_id: str,
        diematic_boiler: DiematicBoiler,
        name: str,
        icon: str,
        variable: str,
        enabled_default: bool = True,
    ) -> None:
        """Initialize Diematic binary sensor."""
        self.variable = variable
        self._attr_unique_id = f"{unique_id}_{variable}"
        super().__init__(
            entry_id=entry_id,
            device_id=unique_id,
            diematic_boiler=diematic_boiler,
            name=name,
            icon=icon,
            enabled_default=enabled_default,
        )

    @property
    def is_on(self) -> bool | None:
        """Returns true if the binary sensor is on."""
        return self.coordinator.data.variables[self.variable]
