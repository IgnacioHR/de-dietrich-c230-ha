"""Support for setting values to the boiler registers"""
from __future__ import annotations
from typing import Any
import asyncio
import logging

from homeassistant.components.timer_programmer import TimerProgrammerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from diematic_client import DiematicError, DiematicStatus
from .diematic_bolier import DiematicBoiler
from .const import DOMAIN
from .entity import DiematicEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """add switch entities"""
    diematic_boiler: DiematicBoiler = hass.data[DOMAIN][config_entry.entry_id]

    if (unique_id := config_entry.unique_id) is None:
        unique_id = config_entry.unique_id

    config = await diematic_boiler.boiler_config()

    timer_programmers: list[TimerProgrammerEntity] = []

    bitstypes = []
    for sub in config:
        if "type" in list(sub) and "bits" in list(sub) and sub["type"] == "bits":
            for item in sub["bits"]:
                bitstypes.append(item)

    for circuit in ("a", "b", "c", "acs"):
        week_timer_programmers: list[TimerProgrammerEntity] = []
        for day_of_week in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            varname = f"{day_of_week}_{circuit}"
            varnamein = varname + "_0000_0030" in bitstypes
            if varnamein:
                timer_programmer = DiematicBoilerConfortTimerProgrammer(
                    config_entry.entry_id,
                    unique_id,
                    diematic_boiler,
                    varname,
                    day_of_week,
                    circuit,
                )
                timer_programmers.append(timer_programmer)
                week_timer_programmers.append(timer_programmer)
        if len(week_timer_programmers) == 7:
            timer_programmers.append(
                DiematicBoilerConfortGroupTimerProgrammer(
                    config_entry.entry_id,
                    unique_id,
                    diematic_boiler,
                    week_timer_programmers,
                    circuit,
                )
            )

    async_add_entities(timer_programmers, True)


class DiematicTimerProgrammer(DiematicEntity, TimerProgrammerEntity):
    """Defines a dimeatic timer programmer."""

    def __init__(
        self,
        *,
        diematic_boiler: DiematicBoiler,
        enabled_default: bool = True,
        entry_id: str,
        unique_id: str,
        icon: str,
        varname: str,
        key: str,
        name: str,
        unit_of_measurement: str | None = None,
    ) -> None:
        """Initialize Diematic sensor."""
        self._key = key
        self.varname = varname
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

    @property
    def value(self) -> int:
        bitsvalue = 0
        i = 47
        for starthour in range(0, 24):
            for startminute in ("00", "30"):
                endhour = starthour if startminute == "00" else starthour + 1
                if endhour == 24:
                    endhour = 0
                endminute = "00" if startminute == "30" else "30"
                varname = f"{self.varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                bitsvalue |= (1 if self.coordinator.data.variables[varname] else 0) << i
                i -= 1

        return bitsvalue

    async def async_set_value(self, value: int) -> None:
        i = 47
        for starthour in range(0, 24):
            for startminute in ("00", "30"):
                endhour = starthour if startminute == "00" else starthour + 1
                if endhour == 24:
                    endhour = 0
                endminute = "00" if startminute == "30" else "30"
                varname = f"{self.varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                checkvalue = (value & 2**i) >> i
                if self.coordinator.data.variables[varname] != checkvalue:
                    await self._async_write_register_value(varname, checkvalue)
                i -= 1

    async def _async_write_register_value(
        self, variable: str, write_value: int, wait_confirmation=True
    ):
        try:
            result = await self._diematic_boiler.update_boiler_register(
                variable, write_value
            )
            if result == DiematicStatus.OK:
                if wait_confirmation:
                    await self.async_read_confirm_value(variable, write_value)
            else:
                _LOGGER.error(
                    "Setting parameter value '%s' returned error but no additional information",
                    variable,
                )
        except DiematicError as error:
            _LOGGER.error(
                "Error setting parameter '%s' value to diematic boiler: {%s}",
                variable,
                error,
            )

    async def async_read_confirm_value(self, variable: str, write_value: int):
        """Read register value until matches write_value or timeout happens."""
        i = 0
        while i < 20:
            i += 1
            readresult = await self._diematic_boiler.read_boiler_register(variable)
            if (
                "status" in readresult
                and "read" == readresult["status"]
                and readresult["value"] == write_value
            ):
                self.async_schedule_update_ha_state(True)
                break
            else:
                await asyncio.sleep(1)
        if i >= 20:
            _LOGGER.warning(
                "Timeout setting value '%s' to register '%s'",
                write_value,
                variable,
            )

    async def async_turn_on(self, bit: int, **kwargs: Any) -> None:
        """Turn on specific bit and write register to boiler."""
        new_value = self.value | (2**bit)
        await self.async_set_value(new_value)

    async def async_turn_off(self, bit: int, **kwargs: Any) -> None:
        """Turn off specific bit and write register to boiler."""
        new_value = self.value & ~(2**bit)
        await self.async_set_value(new_value)


class DiematicBoilerConfortTimerProgrammer(DiematicTimerProgrammer):
    """Defines a sensor that collects day/nignt bitmaps for onw day and one circuit into a 6 bytes single numeric value."""

    def __init__(
        self,
        entry_id: str,
        unique_id: str,
        diematic_boiler: DiematicBoiler,
        varname: str,
        day_of_week: str,
        circuit: str,
    ) -> None:
        self.day_of_week = day_of_week
        self.circuit = circuit
        self._attr_device_class = "timer_programmer"
        super().__init__(
            diematic_boiler=diematic_boiler,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:table-row",
            varname=varname,
            key=f"confort_{varname}",
            name=f"Confort {day_of_week} {circuit}",
            unit_of_measurement=None,
        )


class DiematicBoilerConfortGroupTimerProgrammer(DiematicTimerProgrammer):
    """Groups a set of timer programmers so an action on this will forward the same action to the entire group."""

    def __init__(
        self,
        entry_id: str,
        unique_id: str,
        diematic_boiler: DiematicBoiler,
        timer_programmers: list[DiematicBoilerConfortTimerProgrammer],
        circuit: str,
    ) -> None:
        self._attr_device_class = "timer_programmer"
        self._timer_programmers = timer_programmers
        super().__init__(
            diematic_boiler=diematic_boiler,
            entry_id=entry_id,
            unique_id=unique_id,
            icon="mdi:table-row",
            varname=f"group_{circuit}",
            key=f"confort_group_{circuit}",
            name=f"Confort {circuit}",
            unit_of_measurement=None,
        )

    @property
    def value(self) -> int:
        bitsvalue = 0
        i = 47
        for starthour in range(0, 24):
            for startminute in ("00", "30"):
                endhour = starthour if startminute == "00" else starthour + 1
                if endhour == 24:
                    endhour = 0
                endminute = "00" if startminute == "30" else "30"
                for timer_programmer in self._timer_programmers:
                    varname = f"{timer_programmer.varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                    bitsvalue |= (
                        1 if self.coordinator.data.variables[varname] else 0
                    ) << i
                i -= 1

        return bitsvalue

    async def async_set_value(self, value: int) -> None:
        i = 47
        for starthour in range(0, 24):
            for startminute in ("00", "30"):
                endhour = starthour if startminute == "00" else starthour + 1
                if endhour == 24:
                    endhour = 0
                endminute = "00" if startminute == "30" else "30"
                for timer_programmer in self._timer_programmers:
                    varname = f"{timer_programmer.varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                    checkvalue = (value & 2**i) >> i
                    if self.coordinator.data.variables[varname] != checkvalue:
                        await self._async_write_register_value(
                            varname, checkvalue, wait_confirmation=False
                        )
                for timer_programmer in self._timer_programmers:
                    varname = f"{timer_programmer.varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
                    checkvalue = (value & 2**i) >> i
                    if self.coordinator.data.variables[varname] != checkvalue:
                        await self.async_read_confirm_value(varname, checkvalue)
                i -= 1
