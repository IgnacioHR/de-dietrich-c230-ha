"""Parser for Diematic responses."""

import json

from .enums import DiematicStatus


def parse(raw_data: bytes) -> dict:
    """Parse raw data into a json"""

    jdata = json.loads(raw_data.decode("utf-8"))

    return {"data": jdata, "status-code": DiematicStatus.OK}
