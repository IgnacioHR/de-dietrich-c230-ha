"""Coordinator for the De Dietrich boiler integration"""
from __future__ import annotations

import logging

from datetime import timedelta

from .exceptions import DiematicError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .boiler_client import DiematicBoilerClient
from .const import DOMAIN
from .models import Boiler

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


class DiematicCoordinator(DataUpdateCoordinator[Boiler]):
    """Class to manage fetching Boiler data from single endpoint"""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        host: str,
        port: int,
        base_path: str = "/diematic/",
        tls: bool,
        verify_ssl: bool,
    ) -> None:
        """Initialize global Boiler data updater"""
        self.boiler_client = DiematicBoilerClient(
            host=host, port=port, base_path=base_path, tls=tls, verify_ssl=verify_ssl
        )

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

    async def boiler_config(self) -> list:
        """Fetch configuration from server daemon."""
        try:
            return await self.boiler_client.config()
        except DiematicError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
