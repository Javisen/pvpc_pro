"""
Sensor to collect the reference daily prices.
PVPC REE Data Integration.
Developed and maintained by Javisen.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import logging
from typing import Any

from .aiopvpc.const import (
    KEY_INJECTION,
    KEY_MAG,
    KEY_OMIE,
    KEY_PVPC,
    KEY_INDEXED,
    KEY_CO2,
    KEY_DEMAND,
    KEY_RENEWABLES,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElecPricesDataUpdateCoordinator, PVPCConfigEntry
from .helpers import make_sensor_unique_id

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1

KEY_PERIOD = "current_period"

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=KEY_PVPC,
        icon="mdi:currency-eur",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        name="Precio PVPC",
    ),
    SensorEntityDescription(
        key=KEY_INDEXED,
        icon="mdi:calculator-variant",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        name="Precio Tarifa Indexada",
    ),
    SensorEntityDescription(
        key=KEY_INJECTION,
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        name="Precio Inyección",
    ),
    SensorEntityDescription(
        key=KEY_PERIOD,
        icon="mdi:clock-digital",
        name="Periodo Tarifario",
    ),
    SensorEntityDescription(
        key=KEY_MAG,
        icon="mdi:bank-transfer",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        name="Cargo MAG",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=KEY_OMIE,
        icon="mdi:shopping",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        name="Precio OMIE",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=KEY_CO2,
        icon="mdi:molecule-co2",
        native_unit_of_measurement="tCO2eq/MWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        name="Intensidad de CO2",
    ),
    SensorEntityDescription(
        key=KEY_DEMAND,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        name="Demanda Real",
    ),
    SensorEntityDescription(
        key=KEY_RENEWABLES,
        icon="mdi:leaf",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        name="Generacion Renovables",
    ),
)

_PRICE_SENSOR_ATTRIBUTES_MAP = {
    "data_id": "data_id",
    "name": "data_name",
    "tariff": "tariff",
    "period": "period",
    "available_power": "available_power",
    "next_period": "next_period",
    "hours_to_next_period": "hours_to_next_period",
    "next_better_price": "next_better_price",
    "hours_to_better_price": "hours_to_better_price",
    "num_better_prices_ahead": "num_better_prices_ahead",
    "price_position": "price_position",
    "price_ratio": "price_ratio",
    "max_price": "max_price",
    "max_price_at": "max_price_at",
    "min_price": "min_price",
    "min_price_at": "min_price_at",
    "next_best_at": "next_best_at",
    "price_00h": "price_00h",
    "price_01h": "price_01h",
    "price_02h": "price_02h",
    "price_02h_d": "price_02h_d",
    "price_03h": "price_03h",
    "price_04h": "price_04h",
    "price_05h": "price_05h",
    "price_06h": "price_06h",
    "price_07h": "price_07h",
    "price_08h": "price_08h",
    "price_09h": "price_09h",
    "price_10h": "price_10h",
    "price_11h": "price_11h",
    "price_12h": "price_12h",
    "price_13h": "price_13h",
    "price_14h": "price_14h",
    "price_15h": "price_15h",
    "price_16h": "price_16h",
    "price_17h": "price_17h",
    "price_18h": "price_18h",
    "price_19h": "price_19h",
    "price_20h": "price_20h",
    "price_21h": "price_21h",
    "price_22h": "price_22h",
    "price_23h": "price_23h",
    "next_better_price (next day)": "next_better_price (next day)",
    "hours_to_better_price (next day)": "hours_to_better_price (next day)",
    "num_better_prices_ahead (next day)": "num_better_prices_ahead (next day)",
    "price_position (next day)": "price_position (next day)",
    "price_ratio (next day)": "price_ratio (next day)",
    "max_price (next day)": "max_price (next day)",
    "max_price_at (next day)": "max_price_at (next day)",
    "min_price (next day)": "min_price (next day)",
    "min_price_at (next day)": "min_price_at (next day)",
    "next_best_at (next day)": "next_best_at (next day)",
    "price_next_day_00h": "price_next_day_00h",
    "price_next_day_01h": "price_next_day_01h",
    "price_next_day_02h": "price_next_day_02h",
    "price_next_day_02h_d": "price_next_day_02h_d",
    "price_next_day_03h": "price_next_day_03h",
    "price_next_day_04h": "price_next_day_04h",
    "price_next_day_05h": "price_next_day_05h",
    "price_next_day_06h": "price_next_day_06h",
    "price_next_day_07h": "price_next_day_07h",
    "price_next_day_08h": "price_next_day_08h",
    "price_next_day_09h": "price_next_day_09h",
    "price_next_day_10h": "price_next_day_10h",
    "price_next_day_11h": "price_next_day_11h",
    "price_next_day_12h": "price_next_day_12h",
    "price_next_day_13h": "price_next_day_13h",
    "price_next_day_14h": "price_next_day_14h",
    "price_next_day_15h": "price_next_day_15h",
    "price_next_day_16h": "price_next_day_16h",
    "price_next_day_17h": "price_next_day_17h",
    "price_next_day_18h": "price_next_day_18h",
    "price_next_day_19h": "price_next_day_19h",
    "price_next_day_20h": "price_next_day_20h",
    "price_next_day_21h": "price_next_day_21h",
    "price_next_day_22h": "price_next_day_22h",
    "price_next_day_23h": "price_next_day_23h",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PVPCConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the electricity price sensor from config_entry."""
    coordinator = entry.runtime_data
    sensors = [
        ElecPriceSensor(coordinator, SENSOR_TYPES[0], entry.unique_id),
        ElecPriceSensor(coordinator, SENSOR_TYPES[1], entry.unique_id),
        ElecPriceSensor(coordinator, SENSOR_TYPES[3], entry.unique_id),
    ]
    if coordinator.api.using_private_api:
        sensors.append(ElecPriceSensor(coordinator, SENSOR_TYPES[2], entry.unique_id))
        sensors.extend(
            ElecPriceSensor(coordinator, s, entry.unique_id) for s in SENSOR_TYPES[4:]
        )
    async_add_entities(sensors)


class ElecPriceSensor(CoordinatorEntity[ElecPricesDataUpdateCoordinator], SensorEntity):
    """Class to hold the prices of electricity as a sensor."""

    def __init__(
        self,
        coordinator: ElecPricesDataUpdateCoordinator,
        description: SensorEntityDescription,
        unique_id: str | None,
    ) -> None:
        """Initialize ESIOS sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_attribution = coordinator.api.attribution
        self._attr_unique_id = make_sensor_unique_id(unique_id, description.key)

        # --- BLOQUE DE COMPATIBILIDAD CRÍTICA ---
        if description.key == KEY_PVPC:
            # Forzamos el ID original que usan todos los usuarios
            self.entity_id = "sensor.esios_pvpc"
            self._attr_name = "Precio PVPC"
            self._attr_has_entity_name = False
        else:
            # Para los sensores nuevos de la versión Pro, usamos nombres limpios
            self._attr_has_entity_name = False
            slug = (
                description.name.lower()
                .replace(" ", "_")
                .replace("á", "a")
                .replace("ó", "o")
            )
            self.entity_id = f"sensor.{slug}"
        # ----------------------------------------

        self._attr_device_info = DeviceInfo(
            configuration_url="https://api.esios.ree.es",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.entry_id)},
            manufacturer="REE",
            name="PVPC REE Data (Pro)",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        k = (
            KEY_PVPC
            if self.entity_description.key == KEY_PERIOD
            else self.entity_description.key
        )
        return self.coordinator.data.availability.get(k, False)

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        source_key = (
            KEY_PVPC
            if self.entity_description.key == KEY_PERIOD
            else self.entity_description.key
        )
        self.coordinator.api.update_active_sensors(source_key, True)
        self.async_on_remove(
            lambda: self.coordinator.api.update_active_sensors(source_key, False)
        )
        self.async_on_remove(
            async_track_time_change(
                self.hass, self.update_current_price, second=[0], minute=[0]
            )
        )

    @callback
    def update_current_price(self, now: datetime) -> None:
        """Update the sensor state."""
        source_key = (
            KEY_PVPC
            if self.entity_description.key == KEY_PERIOD
            else self.entity_description.key
        )
        self.coordinator.api.process_state_and_attributes(
            self.coordinator.data, source_key, now
        )
        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.key == KEY_PERIOD:
            return self.coordinator.api.sensor_attributes.get(KEY_PVPC, {}).get(
                "period"
            )
        return self.coordinator.api.states.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.entity_description.key == KEY_PERIOD:
            return {}
        attrs = self.coordinator.api.sensor_attributes.get(
            self.entity_description.key, {}
        )
        return {
            _PRICE_SENSOR_ATTRIBUTES_MAP[k]: v
            for k, v in attrs.items()
            if k in _PRICE_SENSOR_ATTRIBUTES_MAP
        }
