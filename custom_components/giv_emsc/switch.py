"""Switch entities for GIV EMS-C — on/off controls."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GivEMSCCoordinator
from .sensor import _device_info


@dataclass(frozen=True, kw_only=True)
class GivEMSCSwitchDescription(SwitchEntityDescription):
    register: str = ""
    on_value: int = 1
    off_value: int = 0


SWITCH_DESCRIPTIONS: tuple[GivEMSCSwitchDescription, ...] = (
    GivEMSCSwitchDescription(
        key="charge_enable",
        register="charge_enable",
        name="AC Charge Enable",
        icon="mdi:battery-charging",
    ),
    GivEMSCSwitchDescription(
        key="discharge_enable",
        register="discharge_enable",
        name="Battery Discharge Enable",
        icon="mdi:battery-minus",
    ),
    GivEMSCSwitchDescription(
        key="export_power_switch",
        register="export_power_switch",
        name="Export Power Limit Switch",
        icon="mdi:transmission-tower-export",
    ),
    GivEMSCSwitchDescription(
        key="peak_cut_switch",
        register="peak_cut_switch",
        name="Peak Cutting Switch",
        icon="mdi:chart-timeline-variant",
    ),
    GivEMSCSwitchDescription(
        key="dod_enable",
        register="dod_enable",
        name="Depth of Discharge Enable",
        icon="mdi:battery-lock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GivEMSCCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GivEMSCSwitch(coordinator, entry, desc)
        for desc in SWITCH_DESCRIPTIONS
    )


class GivEMSCSwitch(CoordinatorEntity, SwitchEntity):
    """An on/off control entity."""

    entity_description: GivEMSCSwitchDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GivEMSCCoordinator,
        entry: ConfigEntry,
        description: GivEMSCSwitchDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data.get(self.entity_description.register)
        if val is None:
            return None
        return int(val) == self.entity_description.on_value

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_register(
            self.entity_description.register,
            float(self.entity_description.on_value),
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write_register(
            self.entity_description.register,
            float(self.entity_description.off_value),
        )
