"""Sensor entities for GIV EMS-C — read-only real-time data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EMS_STATUS, SYSTEM_MODE
from .coordinator import GivEMSCCoordinator


@dataclass(frozen=True, kw_only=True)
class GivEMSCSensorDescription(SensorEntityDescription):
    """Extends the standard description with our register name."""
    register: str = ""
    value_map: Optional[dict] = None   # for status → string translation


SENSOR_DESCRIPTIONS: tuple[GivEMSCSensorDescription, ...] = (
    # ---- System status ----
    GivEMSCSensorDescription(
        key="ems_status",
        register="ems_status",
        name="EMS Status",
        icon="mdi:information-outline",
        value_map=EMS_STATUS,
    ),
    GivEMSCSensorDescription(
        key="system_mode",
        register="system_mode",
        name="System Mode",
        icon="mdi:transmission-tower",
        value_map=SYSTEM_MODE,
    ),

    # ---- Battery ----
    GivEMSCSensorDescription(
        key="average_soc",
        register="average_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="battery_power",
        register="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
    ),
    GivEMSCSensorDescription(
        key="battery_voltage",
        register="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="battery_current",
        register="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # ---- Grid ----
    GivEMSCSensorDescription(
        key="grid_power",
        register="grid_power",
        name="Grid Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
    ),
    GivEMSCSensorDescription(
        key="grid_frequency",
        register="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="grid_voltage_a",
        register="grid_voltage_a",
        name="Grid Voltage L1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="grid_voltage_b",
        register="grid_voltage_b",
        name="Grid Voltage L2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="grid_voltage_c",
        register="grid_voltage_c",
        name="Grid Voltage L3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="grid_export_today",
        register="grid_export_today",
        name="Grid Export Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
    ),
    GivEMSCSensorDescription(
        key="grid_import_today",
        register="grid_import_today",
        name="Grid Import Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
    ),

    # ---- Solar PV ----
    GivEMSCSensorDescription(
        key="pv1_power",
        register="pv1_power",
        name="PV1 Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    GivEMSCSensorDescription(
        key="pv2_power",
        register="pv2_power",
        name="PV2 Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
    ),
    GivEMSCSensorDescription(
        key="pv1_voltage",
        register="pv1_voltage",
        name="PV1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="pv2_voltage",
        register="pv2_voltage",
        name="PV2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="pv1_current",
        register="pv1_current",
        name="PV1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="pv2_current",
        register="pv2_current",
        name="PV2 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # ---- Inverter / Load ----
    GivEMSCSensorDescription(
        key="inv_active_power",
        register="inv_active_power",
        name="Inverter Active Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GivEMSCSensorDescription(
        key="load_power",
        register="load_power",
        name="Load Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    GivEMSCSensorDescription(
        key="inv_charge_today",
        register="inv_charge_today",
        name="Battery Charge Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-plus",
    ),
    GivEMSCSensorDescription(
        key="inv_discharge_today",
        register="inv_discharge_today",
        name="Battery Discharge Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-minus",
    ),
    GivEMSCSensorDescription(
        key="power_factor",
        register="power_factor",
        name="Power Factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # ---- Backup ----
    GivEMSCSensorDescription(
        key="backup_voltage",
        register="backup_voltage",
        name="Backup Output Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:power-socket",
    ),
    GivEMSCSensorDescription(
        key="backup_frequency",
        register="backup_frequency",
        name="Backup Output Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:power-socket",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GivEMSCCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GivEMSCSensor(coordinator, entry, desc)
        for desc in SENSOR_DESCRIPTIONS
    )


class GivEMSCSensor(CoordinatorEntity, SensorEntity):
    """A single read-only sensor entity."""

    entity_description: GivEMSCSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GivEMSCCoordinator,
        entry: ConfigEntry,
        description: GivEMSCSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        val = self.coordinator.data.get(self.entity_description.register)
        if val is None:
            return None
        if self.entity_description.value_map:
            return self.entity_description.value_map.get(int(val), f"Unknown ({val})")
        return val


def _device_info(entry: ConfigEntry) -> dict:
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": f"GIV EMS-C ({entry.data['host']})",
        "manufacturer": "GivEnergy",
        "model": "GIV-EMS-C",
    }
