"""Exceptions for Diematic."""


class DiematicError(Exception):
    """Generic Diematic exception."""


class DiematicConnectionError(DiematicError):
    """Diematic connection exception."""


class DiematicParseError(DiematicError):
    """Diematic parse exception."""


class DiematicResponseError(DiematicError):
    """Diematic response exception."""
