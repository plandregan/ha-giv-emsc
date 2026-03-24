"""GIV EMS-C Home Assistant Integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SLAVE, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_SLAVE, DOMAIN
from .coordinator import GivEMSCCoordinator

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GIV EMS-C from a config entry."""
    coordinator = GivEMSCCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        slave=entry.data.get(CONF_SLAVE, DEFAULT_SLAVE),
        scan_interval=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    # Do the first poll — raises ConfigEntryNotReady if it fails,
    # which makes HA retry automatically rather than showing an error.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: GivEMSCCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator._client:
            coordinator._client.close()
    return unloaded
