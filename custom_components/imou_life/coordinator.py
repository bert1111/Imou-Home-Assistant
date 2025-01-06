"""Provides the imou DataUpdateCoordinator."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyimouapi.ha_device import ImouHaDevice, ImouHaDeviceManager

_LOGGER = logging.getLogger(__name__)


class ImouDataUpdateCoordinator(DataUpdateCoordinator):
    """DATA UPDATE COORDINATOR."""

    def __init__(
        self, hass: HomeAssistant, device_manager: ImouHaDeviceManager
    ) -> None:
        """Init ImouDataUpdateCoordinator."""
        _LOGGER.info("ImouDataUpdateCoordinator init")
        super().__init__(
            hass,
            _LOGGER,
            name="ImouDataUpdateCoordinator",
            update_interval=timedelta(seconds=900),
            always_update=True,
        )
        self._device_manager = device_manager
        self._devices: list[ImouHaDevice] = []

    @property
    def devices(self):  # noqa: D102
        return self._devices

    @property
    def device_manager(self):  # noqa: D102
        return self._device_manager

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        devices_list = await self._device_manager.async_get_devices()
        for device in devices_list:
            self._devices.append(device)

    async def async_update_all_device(self) -> bool:
        """Update all device."""
        await asyncio.gather(
            *[
                self._device_manager.async_update_device_status(device)
                for device in self._devices
            ],
            return_exceptions=True,
        )
        return True

    async def _async_update_data(self):
        _LOGGER.info("ImouDataUpdateCoordinator update_data")
        async with asyncio.timeout(120):
            try:
                return await self.async_update_all_device()
            except Exception as err:
                _LOGGER.error(f"Error fetching data: {err}")  # noqa: G004
                raise UpdateFailed from err
