"""The De Dietrich C-230 Eco schedulers"""
import logging
from typing import Any
from .const import DOMAIN
from .diematic_bolier import DiematicBoiler

from homeassistant.components.schedule import DOMAIN as SCHEDULE_DOMAIN, Schedule
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

LOGGER = logging.getLogger(__package__)
DATA_INSTANCES = "entity_components"


class DiematicBoilerSchedule(Schedule):
    """Extension of Schedule entity baed on the information from the diematic boiler"""

    def __init__(
        self,
        config: ConfigType,
    ) -> None:
        super().__init__(config, True)


async def async_setup(hass: HomeAssistant) -> bool:
    """Set up async"""

    component: EntityComponent[Schedule] = hass.data.get(DATA_INSTANCES, {}).get(
        SCHEDULE_DOMAIN
    )

    week_timer_programmers: list[Schedule] = await _prepare_schedules(hass)

    await component.async_add_entities(week_timer_programmers)

    return True


async def _prepare_schedules(hass: HomeAssistant) -> list[Schedule]:
    """Read the information from diematic and prepare schedules"""
    week_timer_programmers: list[Schedule] = []

    for boiler_key in hass.data[DOMAIN]:
        diematic_boiler: DiematicBoiler = hass.data[DOMAIN][boiler_key]
        LOGGER.debug("Boiler {%s}", boiler_key)

        bitstypes = await _prepare_bitstypes(diematic_boiler)

        for circuit in ("a", "b", "c", "acs"):
            week_timer_programmers.append(
                _process_circuit(
                    circuit,
                    boiler_key,
                    bitstypes,
                    diematic_boiler.coordinator.data.variables,
                )
            )

    return week_timer_programmers


async def _prepare_bitstypes(diematic_boiler: DiematicBoiler) -> list[str]:
    """collect all variables of type bits"""
    config = await diematic_boiler.boiler_config()

    bitstypes = []
    for sub in config:
        if "type" in list(sub) and "bits" in list(sub) and sub["type"] == "bits":
            for item in sub["bits"]:
                bitstypes.append(item)
    return bitstypes


def _process_circuit(
    circuit: str,
    boiler_key: str,
    bitstypes: list[str],
    diematic_data: dict[str, Any],
) -> DiematicBoilerSchedule:
    """aaa"""
    scheduler_config = {}
    scheduler_config["name"] = f"Scheduler {circuit}"
    scheduler_config["id"] = f"scheduler_{circuit}_{boiler_key}"
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
            scheduler_config[day_of_week] = []
            _prepare_day_block(scheduler_config[day_of_week], varname, diematic_data)

    return DiematicBoilerSchedule(scheduler_config)


def _prepare_day_block(
    day_config: list[Any],
    varname: str,
    diematic_data: dict[str, Any],
) -> None:
    """read start - end periods from boiler data about one day and circuit and prepare array value for schedule"""
    current_block = {}
    in_range = False
    for starthour in range(0, 24):
        for startminute in ("00", "30"):
            endhour = starthour if startminute == "00" else starthour + 1
            if endhour == 24:
                endhour = 0
            endminute = "00" if startminute == "30" else "30"
            timevarname = (
                f"{varname}_{starthour:02}{startminute}_{endhour:02}{endminute}"
            )
            if not in_range:
                if diematic_data[timevarname] == 1:
                    current_block["from"] = f"{starthour:02}:{startminute}:00"
                    in_range = True
            else:
                if diematic_data[timevarname] == 0:
                    current_block["to"] = f"{starthour:02}:{startminute}:00"
                    day_config.append(current_block)
                    current_block = {}
                    in_range = False
    if in_range:
        current_block["to"] = "24:00:00"
        day_config.append(current_block)
