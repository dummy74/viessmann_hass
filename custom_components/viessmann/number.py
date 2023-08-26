from __future__ import annotations

import copy
from dataclasses import dataclass
import logging
from os import device_encoding, stat

from sqlalchemy import desc

from homeassistant.components import mqtt
from homeassistant.components.number import DOMAIN, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_DEFAULT_NAME,
    ELECTRIC_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    ENTITY_CATEGORY_CONFIG,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import slugify

from .common import ViessmannBaseEntity

# Import global values.
from .const import (
    MQTT_ROOT_TOPIC,
    NUMBERS,
    ViessmannNumberEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for Viessmann."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]

    numberList = []

    NUMBERS_COPY = copy.deepcopy(NUMBERS)
    for description in NUMBERS_COPY:
        description.mqttTopicCommand = f"{mqttRoot}/{description.mqttTopicCommand}"
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.mqttTopicCurrentValue}"

        numberList.append(
            ViessmannNumber(
                unique_id=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
                # state=description.min_value,
            )
        )

    async_add_entities(numberList)


class ViessmannNumber(ViessmannBaseEntity, NumberEntity):
    """Entity representing Viessmann numbers"""

    entity_description: ViessmannNumberEntityDescription

    def __init__(
        self,
        unique_id: str,
        device_friendly_name: str,
        mqtt_root: str,
        description: ViessmannNumberEntityDescription,
        state: float | None = None,
        native_min_value: float | None = None,
        native_max_value: float | None = None,
        native_step: float | None = None,
        mode: NumberMode = NumberMode.AUTO,
    ) -> None:
        """Initialize the sensor and the Viessmann device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description

        self._attr_unique_id = slugify(f"{unique_id}-{description.name}")
        self.entity_id = f"{DOMAIN}.{unique_id}-{description.name}"
        self._attr_name = description.name

        # if state is not None:
        #     self._attr_value = state
        # else:
        self._attr_native_value = state

        self._attr_mode = mode

        if native_min_value is not None:
            self._attr_native_min_value = native_min_value
        if native_max_value is not None:
            self._attr_native_max_value = native_max_value
        if native_step is not None:
            self._attr_native_step = native_step

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_native_value = self.entity_description.value_fn(float(message.payload))
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

    async def async_set_native_value(self, value):
        """Update the current value.
        After set_value --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, Viessmann has changed the setting as well.
        """
        self._attr_native_value = value
        self.publishToMQTT()
        # self.async_write_ha_state()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        payload = str(self.entity_description.ivalue_fn(self._attr_native_value))
        _LOGGER.debug("MQTT payload: %s", payload)
        self.hass.components.mqtt.publish(self.hass, topic, payload)
