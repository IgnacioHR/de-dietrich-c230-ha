"""Enumerations for Diematic."""
from enum import IntEnum


class DiematicStatus(IntEnum):
    """Represent the ENUMs of a status response."""

    OK = 0x0000


class DiematicOperation(IntEnum):
    """Represent the ENUMs of an operation."""

    GET_VALUES = 0x0001
    GET_CONFIG = 0x0002
