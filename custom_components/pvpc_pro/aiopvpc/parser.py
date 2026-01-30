"""
Parser for the contents of the ESIOS JSON files.
Developed by Javisen.
Robust data extraction with look-back logic and geo-fallback.
"""

from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
from typing import Any
import logging

from .const import (
    DataSource,
    EsiosResponse,
    GEOZONE_ID2NAME,
    GEOZONES,
    KEY_PVPC,
    KEY_INJECTION,
    KEY_MAG,
    KEY_OMIE,
    KEY_ADJUSTMENT,
    KEY_CO2,
    KEY_DEMAND,
    KEY_RENEWABLES,
    PRICE_PRECISION,
    REFERENCE_TZ,
    SENSOR_KEY_TO_DATAID,
    TARIFF2ID,
    TARIFFS,
    URL_ESIOS_TOKEN_RESOURCE,
    URL_PUBLIC_PVPC_RESOURCE,
    UTC_TZ,
)

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

_LOGGER = logging.getLogger(__name__)


def _timezone_offset(tz: zoneinfo.ZoneInfo = REFERENCE_TZ) -> timedelta:
    """Calculate the offset between local timezone and reference."""
    ref_ts = datetime(2021, 1, 1, tzinfo=REFERENCE_TZ).astimezone(UTC_TZ)
    loc_ts = datetime(2021, 1, 1, tzinfo=tz).astimezone(UTC_TZ)
    return loc_ts - ref_ts


def extract_prices_from_esios_public(
    data: dict[str, Any], key: str, tz: zoneinfo.ZoneInfo = REFERENCE_TZ
) -> EsiosResponse:
    """Parse the contents of a daily PVPC json file (Public API)."""
    ts_init = datetime(
        *datetime.strptime(data["PVPC"][0]["Dia"], "%d/%m/%Y").timetuple()[:3],
        tzinfo=tz,
    ).astimezone(UTC_TZ)

    def _parse_tariff_val(value, prec=PRICE_PRECISION) -> float:
        return round(float(value.replace(",", ".")) / 1000.0, prec)

    pvpc_prices = {
        ts_init + timedelta(hours=i): _parse_tariff_val(values_hour[key])
        for i, values_hour in enumerate(data["PVPC"])
    }

    return EsiosResponse(
        name="PVPC ESIOS",
        data_id="legacy",
        last_update=datetime.now(UTC_TZ).replace(microsecond=0),
        unit="€/kWh",
        series={KEY_PVPC: pvpc_prices},
    )


def extract_prices_from_esios_token(
    data: dict[str, Any],
    sensor_key: str,
    geo_zone: str,
    tz: zoneinfo.ZoneInfo = REFERENCE_TZ,
) -> EsiosResponse:
    """Parse the contents of an 'indicator' json file with ESIOS Token."""
    indicator_data = data.pop("indicator")
    _LOGGER.debug("[%s] Parsing ESIOS ID: %s", sensor_key, indicator_data.get("id"))

    offset_timezone = _timezone_offset(tz)
    ts_update = datetime.now(UTC_TZ).replace(microsecond=0)

    def _parse_dt(ts: str) -> datetime:
        return datetime.fromisoformat(ts).astimezone(UTC_TZ) + offset_timezone

    def _value_unit_conversion(value: float) -> float:
        if value is None:
            return 0.0
        # Conversión de Precios
        if sensor_key in [KEY_PVPC, KEY_INJECTION, KEY_MAG, KEY_OMIE, KEY_ADJUSTMENT]:
            return round(float(value) / 1000.0, 5)
        # Conversión de CO2
        if sensor_key == KEY_CO2:
            val = float(value)
            return round(val / 1000.0, 3) if val > 10 else round(val, 3)
        # Renovables y otros
        if sensor_key == KEY_RENEWABLES:
            val = float(value)
            return round(val * 100.0, 1) if (0 < val < 1.0) else round(val, 1)
        return round(float(value), 1)

    if not indicator_data.get("values"):
        return EsiosResponse(
            name=indicator_data["name"],
            data_id=str(indicator_data["id"]),
            last_update=ts_update,
            unit="N/A",
            series={sensor_key: {}},
        )

    value_gen = groupby(
        sorted(indicator_data["values"], key=itemgetter("geo_id")), itemgetter("geo_id")
    )
    parsed_data = {
        GEOZONE_ID2NAME.get(g_id, f"Unknown_{g_id}"): dict(
            sorted(
                [
                    (_parse_dt(i["datetime"]), _value_unit_conversion(i["value"]))
                    for i in list(group)
                ]
            )
        )
        for g_id, group in value_gen
    }

    selected_zone_values = {}
    for zone in [geo_zone, "España", "Península"]:
        if zone in parsed_data:
            selected_zone_values = parsed_data[zone]
            break

    if not selected_zone_values and parsed_data:
        selected_zone_values = list(parsed_data.values())[0]

    if selected_zone_values:
        now_utc = datetime.now(UTC_TZ).replace(minute=0, second=0, microsecond=0)
        if now_utc not in selected_zone_values:
            past_hours = [ts for ts in selected_zone_values.keys() if ts <= now_utc]
            if past_hours:
                latest_ts = max(past_hours)
                selected_zone_values[now_utc] = selected_zone_values[latest_ts]
                _LOGGER.debug(
                    "[%s] Look-back: Usando valor de %s para hora actual",
                    sensor_key,
                    latest_ts,
                )

    return EsiosResponse(
        name=indicator_data["name"],
        data_id=str(indicator_data["id"]),
        last_update=ts_update,
        unit="N/A",
        series={sensor_key: selected_zone_values},
    )


def extract_esios_data(
    data: dict[str, Any],
    url: str,
    sensor_key: str,
    tariff: str,
    tz: zoneinfo.ZoneInfo = REFERENCE_TZ,
) -> EsiosResponse:
    if "/archives/" in url:
        return extract_prices_from_esios_public(data, TARIFF2ID[tariff], tz)
    return extract_prices_from_esios_token(data, sensor_key, "Península", tz)


def get_daily_urls_to_download(
    source: DataSource,
    sensor_keys: set[str],
    now_local_ref: datetime,
    next_day_local_ref: datetime,
) -> tuple[list[str], list[str]]:
    if source == "esios_public":
        u = URL_PUBLIC_PVPC_RESOURCE.format(day=now_local_ref.date())
        un = URL_PUBLIC_PVPC_RESOURCE.format(day=next_day_local_ref.date())
        return [u], [un]

    downloadable_keys = [k for k in sensor_keys if k in SENSOR_KEY_TO_DATAID]
    today = [
        URL_ESIOS_TOKEN_RESOURCE.format(
            ind=SENSOR_KEY_TO_DATAID[k], day=now_local_ref.date()
        )
        for k in downloadable_keys
    ]
    tomorrow = [
        URL_ESIOS_TOKEN_RESOURCE.format(
            ind=SENSOR_KEY_TO_DATAID[k], day=next_day_local_ref.date()
        )
        for k in downloadable_keys
    ]
    return today, tomorrow
