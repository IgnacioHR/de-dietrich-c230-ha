"""Representation of a Diematic boiler."""

from diematic_client import DiematicBoilerClient, DiematicError, DiematicStatus

from homeassistant.core import HomeAssistant

from .coordinator import DiematicCoordinator, UpdateFailed


class DiematicBoiler:
    """Diematic Boiler with access to services."""

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
        """Initialize Diematic boiler."""
        self.boiler_client = DiematicBoilerClient(
            host=host,
            port=port,
            base_path=base_path,
            tls=tls,
            verify_ssl=verify_ssl,
            request_timeout=20,
        )

        self.coordinator = DiematicCoordinator(
            hass,
            boiler_client=self.boiler_client,
        )

    async def boiler_config(self) -> list:
        """Fetch configuration from server daemon."""
        try:
            return await self.boiler_client.config()
        except DiematicError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error

    async def update_boiler_register(
        self, parameter: str, value: float | str
    ) -> DiematicStatus:
        """Update a boiler register."""
        try:
            return await self.boiler_client.update_boiler_register(parameter, value)
        except DiematicError as error:
            raise UpdateFailed(f"Cannot update register value: {error}") from error

    async def read_boiler_register(self, parameter: str) -> dict:
        """Read the content of a single register."""
        try:
            return await self.boiler_client.read_boiler_register(parameter)
        except DiematicError as error:
            raise UpdateFailed(f"Cannot read register value: {error}") from error
