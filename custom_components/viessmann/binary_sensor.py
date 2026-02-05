"""The Viessmannmqtt component for controlling the Viessmann wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import DOMAIN, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import ViessmannBaseEntity

# Import global values.
from .const import (
    BINARY_SENSORS,
    MQTT_ROOT_TOPIC,
    ViessmannBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for Viessmann."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]

    sensorList = []
    # Create all global sensors.
    global_sensors = copy.deepcopy(BINARY_SENSORS)
    for description in global_sensors:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        sensorList.append(
            ViessmannBinarySensor(
                uniqueID=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )

    async_add_entities(sensorList)


class ViessmannBinarySensor(ViessmannBaseEntity, BinarySensorEntity):
    """Representation of an Viessmann sensor that is updated via MQTT."""

    entity_description: ViessmannBinarySensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: ViessmannBinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""

        """Initialize the sensor and the Viessmann device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description
        self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
        self.entity_id = f"{DOMAIN}.{uniqueID}-{description.name}".lower()
        self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_is_on = bool(float(message.payload))

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
