"""
Helper functions for PVPC REE Data.
Developed by Javisen.
Relates sensors keys with Home Assistant unique IDs.
"""

from .aiopvpc.const import (
    ALL_SENSORS,
    KEY_ADJUSTMENT,
    KEY_CO2,
    KEY_DEMAND,
    KEY_INDEXED,
    KEY_INJECTION,
    KEY_MAG,
    KEY_OMIE,
    KEY_PERIOD,
    KEY_PVPC,
    KEY_RENEWABLES,
    TARIFFS,
)

from homeassistant.helpers.entity_registry import RegistryEntry

_ha_uniqueid_to_sensor_key = {
    TARIFFS[0]: KEY_PVPC,
    TARIFFS[1]: KEY_PVPC,
    f"{TARIFFS[0]}_{KEY_INJECTION}": KEY_INJECTION,
    f"{TARIFFS[1]}_{KEY_INJECTION}": KEY_INJECTION,
    f"{TARIFFS[0]}_{KEY_MAG}": KEY_MAG,
    f"{TARIFFS[1]}_{KEY_MAG}": KEY_MAG,
    f"{TARIFFS[0]}_{KEY_OMIE}": KEY_OMIE,
    f"{TARIFFS[1]}_{KEY_OMIE}": KEY_OMIE,
    f"{TARIFFS[0]}_{KEY_ADJUSTMENT}": KEY_ADJUSTMENT,
    f"{TARIFFS[1]}_{KEY_ADJUSTMENT}": KEY_ADJUSTMENT,
    f"{TARIFFS[0]}_{KEY_INDEXED}": KEY_INDEXED,
    f"{TARIFFS[1]}_{KEY_INDEXED}": KEY_INDEXED,
    f"{TARIFFS[0]}_{KEY_PERIOD}": KEY_PERIOD,
    f"{TARIFFS[1]}_{KEY_PERIOD}": KEY_PERIOD,
    # Sensores de sostenibilidad y red actualizados para 2026
    f"{TARIFFS[0]}_{KEY_CO2}": KEY_CO2,
    f"{TARIFFS[1]}_{KEY_CO2}": KEY_CO2,
    f"{TARIFFS[0]}_{KEY_DEMAND}": KEY_DEMAND,
    f"{TARIFFS[1]}_{KEY_DEMAND}": KEY_DEMAND,
    f"{TARIFFS[0]}_{KEY_RENEWABLES}": KEY_RENEWABLES,
    f"{TARIFFS[1]}_{KEY_RENEWABLES}": KEY_RENEWABLES,
}


def get_enabled_sensor_keys(
    using_private_api: bool, entries: list[RegistryEntry]
) -> set[str]:
    """Get enabled API indicators for the current config entry."""
    if not using_private_api:
        return {KEY_PVPC, KEY_PERIOD}

    if len(entries) > 1:
        enabled_keys = set()
        for sensor in entries:
            if not sensor.disabled and sensor.unique_id in _ha_uniqueid_to_sensor_key:
                enabled_keys.add(_ha_uniqueid_to_sensor_key[sensor.unique_id])
        return enabled_keys

    return {KEY_PVPC, KEY_INJECTION, KEY_INDEXED, KEY_PERIOD, KEY_CO2, KEY_RENEWABLES}


def make_sensor_unique_id(config_entry_id: str | None, sensor_key: str) -> str:
    """Generate unique_id for each sensor kind and config entry."""
    assert sensor_key in ALL_SENSORS
    assert config_entry_id is not None

    if sensor_key == KEY_PVPC:
        return config_entry_id
    return f"{config_entry_id}_{sensor_key}"
