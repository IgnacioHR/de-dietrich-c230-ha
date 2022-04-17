"""Coordinator for the De Dietrich boiler integration"""
from __future__ import annotations

import logging
from datetime import timedelta

from diematic_client import Boiler, DiematicBoilerClient, DiematicError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


class DiematicCoordinator(DataUpdateCoordinator[Boiler]):
    """Class to manage fetching Boiler data from single endpoint"""

    def __init__(
        self, hass: HomeAssistant, boiler_client: DiematicBoilerClient
    ) -> None:
        """Initialize global Boiler data updater"""
        self.boiler_client = boiler_client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Boiler:
        """Fetch data from server"""
        try:
            return await self.boiler_client.boiler()
        except DiematicError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
