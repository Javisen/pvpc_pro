"""
Constants for the Spanish Electricity hourly prices (PVPC).
Maintained by Javisen.
Includes sustainability indicators and 2026 grid data.
"""

import zoneinfo
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

DATE_CHANGE_TO_20TD = date(2021, 6, 1)
REFERENCE_TZ = zoneinfo.ZoneInfo("Europe/Madrid")
UTC_TZ = zoneinfo.ZoneInfo("UTC")
DEFAULT_TIMEOUT = 10
PRICE_PRECISION = 5

KEY_PVPC = "PVPC"
KEY_INJECTION = "INJECTION"
KEY_MAG = "MAG"
KEY_OMIE = "OMIE"
KEY_ADJUSTMENT = "ADJUSTMENT"
KEY_CO2 = "CO2_EMISSIONS"
KEY_DEMAND = "DEMAND"
KEY_RENEWABLES = "RENEWABLES"
KEY_INDEXED = "INDEXED"
KEY_PERIOD = "current_period"

ESIOS_PVPC = "1001"
ESIOS_INJECTION = "1739"
ESIOS_MAG = "1900"
ESIOS_OMIE = "10211"
ESIOS_MARKET_ADJUSTMENT = "2108"
ESIOS_CO2 = "570"  # Emisiones CO2 eq. por generación
ESIOS_DEMAND = "1293"  # Demanda real
ESIOS_RENEWABLES = "10491"  # % Generación renovable sobre el total

TARIFF_20TD_IDS = ["PCB", "CYM"]
TARIFFS = ["2.0TD", "2.0TD (Ceuta/Melilla)"]
TARIFF2ID = dict(zip(TARIFFS, TARIFF_20TD_IDS))
DEFAULT_POWER_KW = 3.3

DataSource = Literal["esios_public", "esios"]
GEOZONES = ["Península", "Canarias", "Baleares", "Ceuta", "Melilla", "España"]
GEOZONE_ID2NAME: dict[int, str] = {
    3: "Península",  # ID Histórico
    8741: "Península",
    8742: "Canarias",
    8743: "Baleares",
    8744: "Ceuta",
    8745: "Melilla",
}

ALL_SENSORS = (
    KEY_PVPC,
    KEY_INJECTION,
    KEY_MAG,
    KEY_OMIE,
    KEY_ADJUSTMENT,
    KEY_INDEXED,
    KEY_PERIOD,
    KEY_CO2,
    KEY_DEMAND,
    KEY_RENEWABLES,
)

SENSOR_KEY_TO_DATAID = {
    KEY_PVPC: ESIOS_PVPC,
    KEY_INJECTION: ESIOS_INJECTION,
    KEY_MAG: ESIOS_MAG,
    KEY_OMIE: ESIOS_OMIE,
    KEY_ADJUSTMENT: ESIOS_MARKET_ADJUSTMENT,
    KEY_CO2: ESIOS_CO2,
    KEY_DEMAND: ESIOS_DEMAND,
    KEY_RENEWABLES: ESIOS_RENEWABLES,
}

SENSOR_KEY_TO_NAME = {
    KEY_PVPC: "PVPC T. 2.0TD",
    KEY_INJECTION: "Precio excedente",
    KEY_MAG: "Ajuste liquidación MAG",
    KEY_OMIE: "Precio OMIE",
    KEY_ADJUSTMENT: "Ajuste mercado",
    KEY_INDEXED: "Tarifa Indexada",
    KEY_PERIOD: "Periodo actual",
    KEY_CO2: "Intensidad CO2",
    KEY_DEMAND: "Demanda Real",
    KEY_RENEWABLES: "Generación Renovables",
}

SENSOR_KEY_TO_API_SERIES = {
    KEY_PVPC: [KEY_PVPC],
    KEY_INJECTION: [KEY_INJECTION],
    KEY_MAG: [KEY_MAG],
    KEY_OMIE: [KEY_OMIE],
    KEY_ADJUSTMENT: [KEY_ADJUSTMENT],
    KEY_INDEXED: [KEY_PVPC, KEY_ADJUSTMENT],
    KEY_PERIOD: [KEY_PVPC],
    KEY_CO2: [KEY_CO2],
    KEY_DEMAND: [KEY_DEMAND],
    KEY_RENEWABLES: [KEY_RENEWABLES],
}


URL_PUBLIC_PVPC_RESOURCE = (
    "https://api.esios.ree.es/archives/70/download_json?locale=es&date={day:%Y-%m-%d}"
)
URL_ESIOS_TOKEN_RESOURCE = (
    "https://api.esios.ree.es/indicators/{ind}?"
    "start_date={day:%Y-%m-%d}T00:00&end_date={day:%Y-%m-%d}T23:59"
)

ATTRIBUTIONS: dict[DataSource, str] = {
    "esios_public": "Data retrieved from api.esios.ree.es by REE",
    "esios": "Data retrieved with API token from api.esios.ree.es by REE",
}


@dataclass
class EsiosResponse:

    name: str
    data_id: str
    last_update: datetime
    unit: str
    series: dict[str, dict[datetime, float]]


@dataclass
class EsiosApiData:

    last_update: datetime
    data_source: str
    sensors: dict[str, dict[datetime, float]]
    availability: dict[str, bool]
