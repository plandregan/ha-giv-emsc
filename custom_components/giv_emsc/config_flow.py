"""Config flow for GIV EMS-C — drives the HA setup wizard."""

from __future__ import annotations

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback

from .const import CONF_SLAVE, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_SLAVE, DOMAIN


async def _test_connection(host: str, port: int, slave: int) -> str | None:
    """
    Try a single Modbus read to validate the connection.
    Returns None on success, or an error key string on failure.
    """
    client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
    try:
        connected = await client.connect()
        if not connected:
            return "cannot_connect"
        # Read one input register (address 0 = EMS Status) as a smoke test
        result = await client.read_input_registers(address=0, count=1, slave=slave)
        if result.isError():
            return "modbus_error"
        return None
    except Exception:  # noqa: BLE001
        return "cannot_connect"
    finally:
        client.close()


class GivEMSCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup flow shown to the user."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host  = user_input[CONF_HOST].strip()
            port  = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            # Prevent adding the same device twice
            await self.async_set_unique_id(f"{host}:{port}:{slave}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(host, port, slave)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=f"GIV EMS-C ({host})",
                    data={
                        CONF_HOST:          host,
                        CONF_PORT:          port,
                        CONF_SLAVE:         slave,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT,          default=DEFAULT_PORT):          int,
                vol.Optional(CONF_SLAVE,         default=DEFAULT_SLAVE):         int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GivEMSCOptionsFlow(config_entry)


class GivEMSCOptionsFlow(config_entries.OptionsFlow):
    """Handles the Options dialog — lets users change settings after setup."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.data

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): int,
                vol.Optional(
                    CONF_SLAVE,
                    default=current.get(CONF_SLAVE, DEFAULT_SLAVE),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
