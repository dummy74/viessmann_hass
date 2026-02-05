"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
from datetime import timedelta
import logging
import re

from homeassistant.components import mqtt
from homeassistant.components.sensor import DOMAIN, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt, slugify

from .common import ViessmannBaseEntity

# Import global values.
from .const import (
    MQTT_ROOT_TOPIC,
    SENSORS,
    ViessmannSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for openWB."""

    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]

    sensorList = []
    # Create all global sensors.
    global_sensors = copy.deepcopy(SENSORS)
    for description in global_sensors:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        sensorList.append(
            ViessmannSensor(
                uniqueID=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )

    async_add_entities(sensorList)


class ViessmannSensor(ViessmannBaseEntity, SensorEntity):
    """Representation of an Viessmann sensor that is updated via MQTT."""

    entity_description: ViessmannSensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: ViessmannSensorEntityDescription,
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description

        self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
        self.entity_id = f"{DOMAIN}.{uniqueID}_{description.name}".lower()
        self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_native_value = message.payload

            # Convert data if a conversion function is defined
            if self.entity_description.value_fn is not None:
                self._attr_native_value = self.entity_description.value_fn(self._attr_native_value)

            # Map values as defined in the value map dict.
            if self.entity_description.valueMap is not None:
                try:
                    self._attr_native_value = self.entity_description.valueMap.get(self._attr_native_value)
                except ValueError:
                    self._attr_native_value = self._attr_native_value

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
