"""Support for Imou button controls."""

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyimouapi.exceptions import ImouException

from .const import DOMAIN, PARAM_RESTART_DEVICE
from .entity import ImouEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button."""
    imou_coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in imou_coordinator.devices:
        for button_type in device.buttons:
            button_entity = ImouButton(imou_coordinator, entry, button_type, device)
            if button_type == PARAM_RESTART_DEVICE:
                button_entity._attr_device_class = ButtonDeviceClass.RESTART  # noqa: SLF001
            entities.append(button_entity)
    async_add_entities(entities)


class ImouButton(ImouEntity, ButtonEntity):
    """imou button."""

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            await self.coordinator.device_manager.async_press_button(
                self._device.device_id, self._device.channel_id, self._entity_type
            )
        except ImouException as e:
            raise HomeAssistantError(e.message)  # noqa: B904
