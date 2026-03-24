"""
DataUpdateCoordinator for GIV EMS-C.

Handles all Modbus communication and caches the latest data.
All entity platforms read from this shared cache — only one
Modbus connection and one poll cycle per interval.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    MAX_BLOCK_SIZE,
    MIN_CMD_INTERVAL_MS,
    DOMAIN,
)
from . import registers as reg_module

_LOGGER = logging.getLogger(__name__)

FUNC_HOLDING = 0x03
FUNC_INPUT   = 0x04


class GivEMSCCoordinator(DataUpdateCoordinator):
    """Polls the EMS-C and provides data to all entity platforms."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int = DEFAULT_PORT,
        slave: int = DEFAULT_SLAVE,
        scan_interval: int = 30,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self.slave = slave
        self._client: Optional[AsyncModbusTcpClient] = None
        self._last_cmd: float = 0.0
        self._lock = asyncio.Lock()

        # Pre-build the register maps once
        self._ir = reg_module.input_registers()
        self._hr = reg_module.holding_registers()

    # ------------------------------------------------------------------ #
    #  Modbus helpers                                                      #
    # ------------------------------------------------------------------ #

    async def _ensure_connected(self) -> None:
        if self._client is None or not self._client.connected:
            self._client = AsyncModbusTcpClient(host=self.host, port=self.port, timeout=5)
            connected = await self._client.connect()
            if not connected:
                raise UpdateFailed(f"Cannot connect to EMS-C at {self.host}:{self.port}")
            _LOGGER.debug("Connected to EMS-C at %s:%s", self.host, self.port)

    async def _throttle(self) -> None:
        elapsed_ms = (time.monotonic() - self._last_cmd) * 1000
        if elapsed_ms < MIN_CMD_INTERVAL_MS:
            await asyncio.sleep((MIN_CMD_INTERVAL_MS - elapsed_ms) / 1000)

    async def _read_block(self, function: int, start: int, count: int) -> List[int]:
        await self._throttle()
        self._last_cmd = time.monotonic()
        try:
            if function == FUNC_HOLDING:
                result = await self._client.read_holding_registers(
                    address=start, count=count, slave=self.slave
                )
            else:
                result = await self._client.read_input_registers(
                    address=start, count=count, slave=self.slave
                )
        except ModbusException as exc:
            raise UpdateFailed(f"Modbus read error (func={function:#04x} addr={start}): {exc}") from exc

        if result.isError():
            raise UpdateFailed(f"Modbus error response (func={function:#04x} addr={start}): {result}")
        return result.registers

    async def _read_sparse(
        self, function: int, addresses: List[int]
    ) -> Dict[int, int]:
        """Read a set of addresses by grouping into 60-register aligned blocks."""
        block_ids = sorted({addr // MAX_BLOCK_SIZE for addr in addresses})
        raw: Dict[int, int] = {}
        for block_id in block_ids:
            start = block_id * MAX_BLOCK_SIZE
            regs = await self._read_block(function, start, MAX_BLOCK_SIZE)
            for i, val in enumerate(regs):
                raw[start + i] = val
        return {addr: raw[addr] for addr in addresses if addr in raw}

    # ------------------------------------------------------------------ #
    #  DataUpdateCoordinator interface                                     #
    # ------------------------------------------------------------------ #

    async def _async_update_data(self) -> Dict[str, Any]:
        async with self._lock:
            try:
                await self._ensure_connected()
                return await self._fetch_all()
            except UpdateFailed:
                # Close the connection so next poll reconnects cleanly
                if self._client:
                    self._client.close()
                    self._client = None
                raise

    async def _fetch_all(self) -> Dict[str, Any]:
        """Fetch input registers and the holding registers we care about."""
        data: Dict[str, Any] = {}

        # --- Input registers (real-time) ---
        ir_addrs = sorted(self._ir.keys())
        ir_raw = await self._read_sparse(FUNC_INPUT, ir_addrs)
        for addr, raw_val in ir_raw.items():
            if addr in self._ir:
                data[self._ir[addr].name] = self._ir[addr].decode(raw_val)

        # --- Holding registers (config/settings) ---
        hr_addrs = sorted(self._hr.keys())
        hr_raw = await self._read_sparse(FUNC_HOLDING, hr_addrs)
        for addr, raw_val in hr_raw.items():
            if addr in self._hr:
                data[self._hr[addr].name] = self._hr[addr].decode(raw_val)

        _LOGGER.debug("Fetched %d values from EMS-C", len(data))
        return data

    # ------------------------------------------------------------------ #
    #  Write helper (used by Number / Switch / Select entities)           #
    # ------------------------------------------------------------------ #

    async def async_write_register(self, register_name: str, value: float) -> bool:
        """
        Write a holding register by friendly name.
        `value` is the engineering value — encoding to raw int is done here.
        """
        reg = reg_module.by_name(register_name)
        if reg is None:
            _LOGGER.error("Unknown register: %s", register_name)
            return False

        raw = reg.encode(value)
        async with self._lock:
            try:
                await self._ensure_connected()
                await self._throttle()
                self._last_cmd = time.monotonic()
                result = await self._client.write_register(
                    address=reg.address, value=raw, slave=self.slave
                )
                if result.isError():
                    _LOGGER.error("Write failed for %s: %s", register_name, result)
                    return False
                _LOGGER.debug("Wrote %s = %s (raw %d)", register_name, value, raw)
                # Refresh coordinator data so entities update immediately
                await self.async_request_refresh()
                return True
            except ModbusException as exc:
                _LOGGER.error("Modbus write error for %s: %s", register_name, exc)
                if self._client:
                    self._client.close()
                    self._client = None
                return False
