"""The Viessmannmqtt component for controlling the Viessmann wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
import logging
from datetime import datetime
import re

from homeassistant.components import mqtt
from homeassistant.components.datetime import DOMAIN, DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import ViessmannBaseEntity

# Import global values.
from .const import (
    DATETIMES,
    MQTT_ROOT_TOPIC,
    ViessmannDatetimeEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for Viessmann."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]

    entities = []
    # Create all global sensors.
    descriptions = copy.deepcopy(DATETIMES)
    for description in descriptions:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        entities.append(
            ViessmannDatetimeEntity(
                uniqueID=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )

    async_add_entities(entities)


class ViessmannDatetimeEntity(ViessmannBaseEntity, DateTimeEntity):
    """Representation of an Viessmann sensor that is updated via MQTT."""

    entity_description: ViessmannDatetimeEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: ViessmannDatetimeEntityDescription,
    ) -> None:
        """Initialize the sensor."""

        """Initialize the sensor and the Viessmann device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description
        self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
        self.entity_id = f"{DOMAIN}.{uniqueID}-{description.name}"
        self._attr_name = description.name
        self._attr_native_value = datetime.astimezone(datetime.now())

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            try:
                val = self.entity_description.value_fn(message.payload)
                _LOGGER.info(f"{val=}")
                self._attr_native_value = val
            except Exception as e:
                _LOGGER.error(e)
                self._attr_native_value = None

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
        
    async def async_set_value(self, value: datetime) -> None:
        """Update the current value."""
        
        self._attr_native_value = value
        self.publishToMQTT()
        # self.async_write_ha_state()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        payload = self.entity_description.ivalue_fn(self._attr_native_value)
        _LOGGER.debug("MQTT payload: %s", payload)
        self.hass.components.mqtt.publish(self.hass, topic, payload)
