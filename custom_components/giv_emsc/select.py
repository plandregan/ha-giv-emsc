"""Select entities for GIV EMS-C — dropdown controls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, GRID_CODE, POWER_ADJ_TYPE
from .coordinator import GivEMSCCoordinator
from .sensor import _device_info


@dataclass(frozen=True, kw_only=True)
class GivEMSCSelectDescription(SelectEntityDescription):
    register: str = ""
    options_map: Dict[int, str] = field(default_factory=dict)  # raw int → display string

    @property
    def options_list(self) -> list[str]:
        return list(self.options_map.values())

    def raw_to_option(self, raw: int) -> str | None:
        return self.options_map.get(int(raw))

    def option_to_raw(self, option: str) -> float | None:
        for k, v in self.options_map.items():
            if v == option:
                return float(k)
        return None


SELECT_DESCRIPTIONS: tuple[GivEMSCSelectDescription, ...] = (
    GivEMSCSelectDescription(
        key="power_adj_type",
        register="power_adj_type",
        name="Power Adjustment Mode",
        icon="mdi:tune",
        options_map=POWER_ADJ_TYPE,
    ),
    GivEMSCSelectDescription(
        key="grid_code",
        register="grid_code",
        name="Grid Code",
        icon="mdi:transmission-tower",
        options_map=GRID_CODE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GivEMSCCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GivEMSCSelect(coordinator, entry, desc)
        for desc in SELECT_DESCRIPTIONS
    )


class GivEMSCSelect(CoordinatorEntity, SelectEntity):
    """A dropdown selector entity."""

    entity_description: GivEMSCSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GivEMSCCoordinator,
        entry: ConfigEntry,
        description: GivEMSCSelectDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)
        self._attr_options = description.options_list

    @property
    def current_option(self) -> str | None:
        val = self.coordinator.data.get(self.entity_description.register)
        if val is None:
            return None
        return self.entity_description.raw_to_option(int(val))

    async def async_select_option(self, option: str) -> None:
        raw = self.entity_description.option_to_raw(option)
        if raw is None:
            return
        await self.coordinator.async_write_register(
            self.entity_description.register, raw
        )
