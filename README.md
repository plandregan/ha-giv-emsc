# GIV EMS-C — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Native Home Assistant integration for the **GivEnergy GIV-EMS-C** commercial energy management system.

Connects directly over **Modbus TCP** (no MQTT, no broker required). Entities appear automatically in Home Assistant as sensors, controls and switches.

---

## What you get

### Sensors (read-only)
| Entity | Unit |
|---|---|
| Battery SOC | % |
| Battery Power | kW |
| Battery Voltage / Current | V / A |
| Grid Power | kW |
| Grid Frequency | Hz |
| Grid Voltage L1 / L2 / L3 | V |
| Grid Export / Import Today | kWh |
| PV1 / PV2 Power | kW |
| PV1 / PV2 Voltage / Current | V / A |
| Inverter Active Power | kW |
| Load Power | kW |
| Battery Charge / Discharge Today | kWh |
| Power Factor | — |
| Backup Output Voltage / Frequency | V / Hz |
| EMS Status | text |
| System Mode | text |

### Controls (writable)
| Entity | Type |
|---|---|
| Battery Reserve SOC | Number |
| Charge Rate | Number (slider) |
| Discharge Rate | Number (slider) |
| Export Power Limit | Number |
| Peak Shaving Power | Number |
| Valley Fill Power | Number |
| Low SOC Force Charge Threshold | Number |
| AC Charge Enable | Switch |
| Battery Discharge Enable | Switch |
| Export Power Limit Switch | Switch |
| Peak Cutting Switch | Switch |
| Depth of Discharge Enable | Switch |
| Power Adjustment Mode | Select |
| Grid Code | Select |

---

## Installation via HACS

1. In Home Assistant, go to **HACS → Integrations → ⋮ → Custom repositories**
2. Add `https://github.com/YOUR_GITHUB_USERNAME/ha-giv-emsc` as an **Integration**
3. Search for **GIV EMS-C** and click **Install**
4. Restart Home Assistant

## Manual installation

1. Copy the `custom_components/giv_emsc` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **GIV EMS-C**
3. Enter the IP address of your EMS-C unit
4. Leave port as `502` and slave address as `17` unless you've changed them
5. Click **Submit** — entities will appear under a new device

## Requirements

- GIV-EMS-C firmware supporting Modbus TCP on port 502
- Network access from your HA host to the EMS-C IP address
- Home Assistant 2024.1 or later

## Protocol notes

- Slave address default: **17 (0x11)**
- Max 60 registers per read, aligned to 60-register boundaries
- Minimum 1 second between commands (enforced automatically)
- Poll interval default: **30 seconds**
