"""Models for Diematic Boiler."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Info:
    """Object holding information from Diematic"""

    model: str | None = None
    uuid: str | None = None
    manufacturer: str = "DeDietrich"
    name: str = "DeDietrich boiler"
    version: str = "0.0.0"

    @staticmethod
    def from_dict(data: dict):
        """Obtains Info from values in the data dictionary"""
        return Info(model="TBD", uuid=data["uuid"])


@dataclass(frozen=True)
class Boiler:
    """This is a Boiler converted into a dataclass, I'm not sure this is required at all"""

    info: Info
    variables: dict[str, Any]

    @staticmethod
    def from_dict(data):
        """Return a Boiler from a dictionary"""
        return Boiler(
            info=Info.from_dict(data), variables=Boiler.merge_variables_data(data)
        )

    @staticmethod
    def merge_variables_data(data: dict):
        """Obtain variables from the json"""
        variables = {}
        for k, value in data.items():
            if k == "uuid":
                continue
            variables[k] = value

        return variables
