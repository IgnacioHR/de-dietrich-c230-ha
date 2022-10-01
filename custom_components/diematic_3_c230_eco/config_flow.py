"""Config flow to configure the Diematic integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from diematic_client import (
    DiematicBoilerClient,
    DiematicConnectionError,
    DiematicParseError,
    DiematicResponseError,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_UUID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input"""
    session = async_get_clientsession(hass)
    boilerclient = DiematicBoilerClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        tls=data[CONF_SSL],
        verify_ssl=data[CONF_VERIFY_SSL],
        session=session,
    )

    boiler = await boilerclient.boiler()

    return {CONF_UUID: boiler.info.uuid}


class DiematicFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Diematic config flow."""

    VERSION = 1

    def __init__(self):
        """Set up the instance."""
        self.discovery_info = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        if user_input is None:
            return self._show_setup_form()

        try:
            info = await validate_input(self.hass, user_input)
        except (DiematicConnectionError, DiematicResponseError):
            _LOGGER.debug("Diematic Connection/Response Error", exc_info=True)
            return self._show_setup_form({"base": "cannot_connect"})
        except DiematicParseError:
            _LOGGER.debug("Diematic Parse Error", exc_info=True)
            return self.async_abort(reason="parse_error")
        # except DiematicError:
        #     _LOGGER.debug("Diematic Error", exc_info=True)
        #     return self.async_abort(reason="diematic_error")

        unique_id = user_input[CONF_UUID] = info[CONF_UUID]

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: user_input[CONF_HOST]})

        return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

    def _show_setup_form(self, errors: dict | None = None) -> FlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, msg="Host where diematic server is running"
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        msg="Port where the server is listening",
                        default=8080,
                    ): int,
                    vol.Required(
                        CONF_SSL,
                        msg="is the server is using ssl?",
                        default=False,
                    ): bool,
                    vol.Required(
                        CONF_VERIFY_SSL,
                        msg="Verify the server certificate?",
                        default=False,
                    ): bool,
                }
            ),
            errors=errors or {},
        )
