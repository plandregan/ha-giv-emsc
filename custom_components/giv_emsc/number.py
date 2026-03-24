"""Number entities for GIV EMS-C — writable numeric settings."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GivEMSCCoordinator
from .sensor import _device_info


@dataclass(frozen=True, kw_only=True)
class GivEMSCNumberDescription(NumberEntityDescription):
    register: str = ""
    min_value: float = 0
    max_value: float = 100
    step: float = 1


NUMBER_DESCRIPTIONS: tuple[GivEMSCNumberDescription, ...] = (
    GivEMSCNumberDescription(
        key="battery_reserve_soc",
        register="battery_reserve_soc",
        name="Battery Reserve SOC",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:battery-lock",
    ),
    GivEMSCNumberDescription(
        key="charge_rate",
        register="charge_rate",
        name="Charge Rate",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-charging",
    ),
    GivEMSCNumberDescription(
        key="discharge_rate",
        register="discharge_rate",
        name="Discharge Rate",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-minus",
    ),
    GivEMSCNumberDescription(
        key="export_limit_value",
        register="export_limit_value",
        name="Export Power Limit",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=600,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:transmission-tower-export",
    ),
    GivEMSCNumberDescription(
        key="peak_shaving_power",
        register="peak_shaving_power",
        name="Peak Shaving Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=3000,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:chart-timeline-variant",
    ),
    GivEMSCNumberDescription(
        key="valley_fill_power",
        register="valley_fill_power",
        name="Valley Fill Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=3000,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:chart-timeline-variant",
    ),
    GivEMSCNumberDescription(
        key="low_soc_force_chg",
        register="low_soc_force_chg",
        name="Low SOC Force Charge Threshold",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:battery-alert",
    ),
    GivEMSCNumberDescription(
        key="battery_reserve",
        register="battery_reserve",
        name="Battery Reserve",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:battery-lock-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GivEMSCCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GivEMSCNumber(coordinator, entry, desc)
        for desc in NUMBER_DESCRIPTIONS
    )


class GivEMSCNumber(CoordinatorEntity, NumberEntity):
    """A writable numeric setting."""

    entity_description: GivEMSCNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GivEMSCCoordinator,
        entry: ConfigEntry,
        description: GivEMSCNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.register)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(
            self.entity_description.register, value
        )
