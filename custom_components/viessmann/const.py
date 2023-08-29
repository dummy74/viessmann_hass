"""Constants for the Viessmann integration."""

from __future__ import annotations

import re

from datetime import datetime
from dataclasses import dataclass
from collections.abc import Callable

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    PERCENTAGE,
    Platform,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import EntityCategory

PLATFORMS: list[Platform] = [
    Platform.SELECT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    #Platform.SWITCH,
    Platform.DATETIME,
]

# Global values
DOMAIN = "viessmann"
MANUFACTURER = "Viessmann"
MODEL = "Vitodens 333F"
MQTT_ROOT_TOPIC = "vcontrold"
MQTT_ROOT_TOPIC_DEFAULT = "vcontrold"

# Data schema required by configuration flow
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
    }
)


@dataclass
class ViessmannSensorEntityDescription(SensorEntityDescription):
    """Enhance the sensor entity description for Viessmann"""

    value_fn: Callable | None = lambda v: round(float(v),1)
    valueMap: dict | None = None
    mqttTopicCurrentValue: str | None = None


@dataclass
class ViessmannBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Enhance the sensor entity description for Viessmann"""

    state: Callable | None = None
    mqttTopicCurrentValue: str | None = None


@dataclass
class ViessmannSelectEntityDescription(SelectEntityDescription):
    """Enhance the select entity description for Viessmann"""

    valueMapCommand: dict | None = None
    valueMapCurrentValue: dict | None = None
    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    modes: list | None = None


@dataclass
class ViessmannSwitchEntityDescription(SwitchEntityDescription):
    """Enhance the select entity description for Viessmann"""

    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None


@dataclass
class ViessmannNumberEntityDescription(NumberEntityDescription):
    """Enhance the number entity description for Viessmann"""

    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    value_fn: Callable | None = float
    ivalue_fn: Callable | None = float
    

@dataclass
class ViessmannDatetimeEntityDescription(SwitchEntityDescription):
    """Enhance the select entity description for Viessmann"""

    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    value_fn: Callable | None = None
    ivalue_fn: Callable | None = None
    
    
SENSORS = [
    # System
    ViessmannSensorEntityDescription(
        key="getTempA",
        name="TempA",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempRaumNorSollM1",
        name="TempRaumNorSollM1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempRaumRedSollM1",
        name="TempRaumRedSollM1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempPartyM1",
        name="TempPartyM1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempKist",
        name="TempKist",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempKsoll",
        name="TempKsoll",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempAbgas",
        name="TempAbgas",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempSTSSOL",
        name="TempSTSSOL",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempVListM1",
        name="TempVListM1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempVLsollM1",
        name="TempVLsollM1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempRueck",
        name="TempRueck",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempRL17A",
        name="TempRL17A",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempStp",
        name="TempStp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempSpu",
        name="TempSpu",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    
    ViessmannSensorEntityDescription(
        key="getTempWWist",
        name="TempWWist",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getTempWWsoll",
        name="TempWWsoll",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer",
    ),
    
    ViessmannSensorEntityDescription(
        key="getBrennerStufe",
        name="BrennerStufe",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.DIAGNOSTIC,
        #icon="mdi:thermometer",
    ),
    ViessmannSensorEntityDescription(
        key="getLeistungIst",
        name="LeistungIst",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.DIAGNOSTIC,
        #icon="mdi:thermometer",
    ),
    
    ViessmannSensorEntityDescription(
        key="getPumpeDrehzahlIntern",
        name="PumpeDrehzahlIntern",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.DIAGNOSTIC,
        #icon="mdi:thermometer",
    ),
]
BINARY_SENSORS = [
    ViessmannBinarySensorEntityDescription(
        key="getBetriebPartyM1",
        name="BetriebPartyM1",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None,
        icon="mdi:update",
    ),
    ViessmannBinarySensorEntityDescription(
        key="getPumpeStatusIntern",
        name="PumpeStatusIntern",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None,
        icon="mdi:update",
    ),
    ViessmannBinarySensorEntityDescription(
        key="getPumpeStatusM1",
        name="PumpeStatusM1",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None,
        icon="mdi:update",
    ),
    ViessmannBinarySensorEntityDescription(
        key="getPumpeStatusZirku",
        name="PumpeStatusZirku",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None,
        icon="mdi:update",
    ),
    ViessmannBinarySensorEntityDescription(
        key="getVentilStatus",
        name="VentilStatus",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=None,
        icon="mdi:update",
    ),
    ]
SELECTS = [
    ViessmannSelectEntityDescription(
        key="setBetriebArtM1",
        entity_category=EntityCategory.CONFIG,
        name="BetriebArtM1",
        valueMapCurrentValue={
            "WW":       "WW",
            "RED":      "RED",
            "NORM":     "NORM",
            "H+WW FS":  "H+WW FS",
            "H*WW":     "H+WW",
            "ABSCHALT": "ABSCHALT",
        },
        valueMapCommand={
            "WW":       "WW",
            "RED":      "RED",
            "NORM":     "NORM",
            "H+WW FS":  "H+WW FS",
            "H+WW":     "H+WW",
            "ABSCHALT": "ABSCHALT",
        },
        mqttTopicCommand="setBetriebArtM1",
        mqttTopicCurrentValue="getBetriebArtM1",
        modes=[
            "WW",
            "RED",
            "NORM",
            "H+WW FS",
            "H+WW",
            "ABSCHALT",
        ],
    ),
    ViessmannSelectEntityDescription(
        key="setBetriebPartyM1",
        entity_category=EntityCategory.CONFIG,
        name="BetriebPartyM1",
        valueMapCurrentValue={
            '0': "OFF",
            '1': "ON",
        },
        valueMapCommand={
            "OFF": 0,
            "ON": 1,
        },
        mqttTopicCommand="setBetriebPartyM1",
        mqttTopicCurrentValue="getBetriebPartyM1",
        modes=[
            "OFF",
            "ON",
        ],
    ),
    ViessmannSelectEntityDescription(
        key="setPumpeStatusZirku",
        entity_category=EntityCategory.CONFIG,
        name="PumpeStatusZirku",
        valueMapCurrentValue={
            '0': "OFF",
            '1': "ON",
        },
        valueMapCommand={
            "OFF": 0,
            "ON": 1,
        },
        mqttTopicCommand="setPumpeStatusZirku",
        mqttTopicCurrentValue="getBetriebPartyM1",
        modes=[
            "OFF",
            "ON",
        ],
    ),
    ViessmannSelectEntityDescription(
        key="setUmschaltventil",
        entity_category=EntityCategory.CONFIG,
        name="Umschaltventil",
        valueMapCurrentValue={
            "UNDEV": "UNDEV",
            "Heizen": "Heizen",
            "Mittelstellung": "Mittelstellung",
            "Warmwasser": "Warmwasser",
        },
        valueMapCommand={
            "UNDEV": "UNDEV",
            "Heizen": "Heizen",
            "Mittelstellung": "Mittelstellung",
            "Warmwasser": "Warmwasser",
        },
        mqttTopicCommand="setUmschaltventil",
        mqttTopicCurrentValue="getUmschaltventil",
        modes=[
            "UNDEV",
            "Heizen",
            "Mittelstellung",
            "Warmwasser",
        ],
    ),
    ]

NUMBERS = [
    ViessmannNumberEntityDescription(
        key="setNiveauM1",
        name="NiveauM1",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        mode="box",
        native_min_value=0,
        native_max_value=15,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setNiveauM1",
        mqttTopicCurrentValue="getNiveauM1",
        icon="mdi:car-cruise-control",
        value_fn=float,
        ivalue_fn=int,
    ),
    ViessmannNumberEntityDescription(
        key="setNeigungM1",
        name="NeigungM1",
        #native_unit_of_measurement=None,
        #device_class=None,
        mode="box",
        native_min_value=0.0,
        native_max_value=2.0,
        native_step=0.05,
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setNeigungM1",
        mqttTopicCurrentValue="getNeigungM1",
        icon="mdi:car-cruise-control",
        value_fn=float,
        ivalue_fn=float,
    ),
    ViessmannNumberEntityDescription(
        key="setTempRaumNorSollM1",
        name="TempRaumNorSollM1",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        mode="box",
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=1.0,
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setTempRaumNorSollM1",
        mqttTopicCurrentValue="getTempRaumNorSollM1",
        icon="mdi:target",
        value_fn=float,
        ivalue_fn=float,
    ),
    ViessmannNumberEntityDescription(
        key="setTempRaumRedSollM1",
        name="TempRaumRedSollM1",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        mode="box",
        native_min_value=10,
        native_max_value=20.0,
        native_step=1.0,
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setTempRaumRedSollM1",
        mqttTopicCurrentValue="getTempRaumRedSollM1",
        icon="mdi:target",
        value_fn=float,
        ivalue_fn=float,
    ),
    ViessmannNumberEntityDescription(
        key="setTempPartyM1",
        name="TempPartyM1",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        mode="box",
        native_min_value=20.0,
        native_max_value=35.0,
        native_step=1.0,
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setTempPartyM1",
        mqttTopicCurrentValue="getTempPartyM1",
        icon="mdi:car-cruise-control",
        value_fn=float,
        ivalue_fn=float,
    ),
]

DATETIMES = [
    
    ViessmannDatetimeEntityDescription(
        key="setSystemTime",
        name="SystemTime",
        entity_category=EntityCategory.CONFIG,
        mqttTopicCommand="setSystemTime",
        mqttTopicCurrentValue="getSystemTime",
        # icon=None,
        value_fn=lambda v: datetime.fromisoformat(v) if re.match(r'^\d{4,4}-\d\d-\d\dT\d\d:\d\d:\d\d\+\d{4,4}$',v) else None,
        ivalue_fn=lambda v: datetime.astimezone(v).isoformat(),
    )
    
    ] 
