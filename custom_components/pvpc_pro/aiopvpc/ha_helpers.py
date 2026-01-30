"""
Home Assistant helper methods for PVPC REE Data.
Modified and maintained by Javisen - 2026.
"""

from .const import (
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

_ha_uniqueid_to_sensor_key = {
    TARIFFS[0]: KEY_PVPC,
    TARIFFS[1]: KEY_PVPC,
    f"{TARIFFS[0]}_{KEY_INJECTION}": KEY_INJECTION,
    f"{TARIFFS[1]}_{KEY_INJECTION}": KEY_INJECTION,
    f"{TARIFFS[0]}_INYECTION": KEY_INJECTION,
    f"{TARIFFS[1]}_INYECTION": KEY_INJECTION,
    f"{TARIFFS[0]}_{KEY_MAG}": KEY_MAG,
    f"{TARIFFS[1]}_{KEY_MAG}": KEY_MAG,
    f"{TARIFFS[0]}_{KEY_OMIE}": KEY_OMIE,
    f"{TARIFFS[1]}_{KEY_OMIE}": KEY_OMIE,
    f"{TARIFFS[0]}_{KEY_ADJUSTMENT}": KEY_ADJUSTMENT,
    f"{TARIFFS[1]}_{KEY_ADJUSTMENT}": KEY_ADJUSTMENT,
    f"{TARIFFS[0]}_{KEY_INDEXED}": KEY_INDEXED,
    f"{TARIFFS[1]}_{KEY_INDEXED}": KEY_INDEXED,
    # Mapeo de los nuevos sensores 2026
    f"{TARIFFS[0]}_{KEY_PERIOD}": KEY_PERIOD,
    f"{TARIFFS[1]}_{KEY_PERIOD}": KEY_PERIOD,
    f"{TARIFFS[0]}_{KEY_CO2}": KEY_CO2,
    f"{TARIFFS[1]}_{KEY_CO2}": KEY_CO2,
    f"{TARIFFS[0]}_{KEY_DEMAND}": KEY_DEMAND,
    f"{TARIFFS[1]}_{KEY_DEMAND}": KEY_DEMAND,
    f"{TARIFFS[0]}_{KEY_RENEWABLES}": KEY_RENEWABLES,
    f"{TARIFFS[1]}_{KEY_RENEWABLES}": KEY_RENEWABLES,
}


def get_enabled_sensor_keys(
    using_private_api: bool, disabled_sensor_ids: list[str]
) -> set[str]:
    """(HA) Get enabled API indicators filtering by user-disabled sensors."""
    sensor_keys = set(ALL_SENSORS) if using_private_api else {KEY_PVPC}

    for unique_id in disabled_sensor_ids:
        if unique_id in _ha_uniqueid_to_sensor_key:
            disabled_ind = _ha_uniqueid_to_sensor_key[unique_id]
            if disabled_ind in sensor_keys:
                sensor_keys.remove(disabled_ind)

    return sensor_keys
