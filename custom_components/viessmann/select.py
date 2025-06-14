"""Viessmann Selector"""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.select import DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import ViessmannBaseEntity
from .const import (
    MQTT_ROOT_TOPIC,
    SELECTS,
    ViessmannSelectEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    integrationUniqueID = config_entry.unique_id
    mqttRoot = config_entry.data[MQTT_ROOT_TOPIC]

    selectList = []
    global_selects = copy.deepcopy(SELECTS)
    for description in global_selects:
        description.mqttTopicCommand = f"{mqttRoot}/{description.mqttTopicCommand}"
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.mqttTopicCurrentValue}"
        selectList.append(
            ViessmannSelect(
                unique_id=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )
    async_add_entities(selectList)


class ViessmannSelect(ViessmannBaseEntity, SelectEntity):
    """Entity representing the inverter operation mode."""

    entity_description: ViessmannSelectEntityDescription

    def __init__(
        self,
        unique_id: str,
        device_friendly_name: str,
        description: ViessmannSelectEntityDescription,
        mqtt_root: str,
    ) -> None:
        """Initialize the sensor and the Viessmann device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )
        """Initialize the inverter operation mode setting entity."""
        self.entity_description = description

        self._attr_unique_id = slugify(f"{unique_id}-{description.name}")
        self.entity_id = f"{DOMAIN}.{unique_id}-{description.name}"
        self._attr_name = description.name

        self._attr_options = description.modes
        self._attr_current_option = None

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            _LOGGER.debug(f"received: {message=}")
            try:
                val = message.payload
                if self.entity_description.value_fn: val = self.entity_description.value_fn(val) 
                self._attr_current_option = self.entity_description.valueMapCurrentValue.get(val)
            except ValueError as e:
                _LOGGER.error(e)
                self._attr_current_option = None

            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        if self.entity_description.mqttTopicCurrentValue is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                message_received,
                1,
            )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        try:
            payload = self.entity_description.valueMapCommand.get(option)
            _LOGGER.debug("MQTT payload: %s", payload)
            publish_mqtt_message = True
        except ValueError:
            publish_mqtt_message = False

        if publish_mqtt_message:
            await mqtt.async_publish(self.hass, topic, payload)
        """After select --> the result is published to MQTT. 
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, Viessmann has changed the setting as well.
        """
        # self._attr_current_option = option
        # self.async_write_ha_state()

