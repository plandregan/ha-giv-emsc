"""Constants for the GIV EMS-C integration."""

DOMAIN = "giv_emsc"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 0x11       # 17 — EMS-C default Modbus slave address
DEFAULT_SCAN_INTERVAL = 30 # seconds

CONF_SLAVE = "slave"

# Modbus protocol limits
MAX_BLOCK_SIZE = 60        # max registers per single read
MIN_CMD_INTERVAL_MS = 1000 # mandatory inter-command delay

# EMS status map
EMS_STATUS = {0: "Waiting", 1: "Normal", 2: "Fault", 3: "Firmware Update"}
SYSTEM_MODE = {0: "Off-grid", 1: "Grid-tied"}
POWER_ADJ_TYPE = {0: "Priority", 1: "Average", 2: "ECO", 3: "BasedSOC", 4: "Peak_Valley"}
GRID_CODE = {0: "CN (GB/T 34120)", 1: "UK (G99)", 2: "EN (EN50549)"}
