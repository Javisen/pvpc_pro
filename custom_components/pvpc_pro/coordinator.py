"""
DataUpdateCoordinator for PVPC REE Data.
Maintains the connection with ESIOS API and manages data refresh.
Updated by Javisen - 2026.
"""

from datetime import timedelta
import logging

from .aiopvpc import BadApiTokenAuthError, EsiosApiData, PVPCData
from .aiopvpc.const import KEY_ADJUSTMENT, KEY_INDEXED, KEY_PVPC

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import ATTR_POWER, ATTR_POWER_P3, ATTR_TARIFF, DOMAIN

_LOGGER = logging.getLogger(__name__)

type PVPCConfigEntry = ConfigEntry[ElecPricesDataUpdateCoordinator]


class ElecPricesDataUpdateCoordinator(DataUpdateCoordinator[EsiosApiData]):
    """Class to manage fetching Electricity prices data from API."""

    config_entry: PVPCConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: PVPCConfigEntry, sensor_keys: set[str]
    ) -> None:
        """Initialize the coordinator."""
        config = entry.data.copy()
        config.update({attr: value for attr, value in entry.options.items() if value})

        # --- PARCHE DE SEGURIDAD PARA DEPENDENCIAS (Optimizado por Javisen) ---
        final_keys = list(sensor_keys)

        if KEY_INDEXED in final_keys and KEY_ADJUSTMENT not in final_keys:
            _LOGGER.debug(
                "Añadiendo KEY_ADJUSTMENT automáticamente para el cálculo de Tarifa Indexada"
            )
            final_keys.append(KEY_ADJUSTMENT)

        if not final_keys:
            final_keys = [KEY_PVPC]
        # ---------------------------------------------------------------------

        self.api = PVPCData(
            session=async_get_clientsession(hass),
            tariff=config[ATTR_TARIFF],
            local_timezone=hass.config.time_zone,
            power=config[ATTR_POWER],
            power_valley=config[ATTR_POWER_P3],
            api_token=config.get(CONF_API_TOKEN),
            sensor_keys=tuple(final_keys),
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,  # Usará "pvpc_pro"
            update_interval=timedelta(minutes=30),
        )

    @property
    def entry_id(self) -> str:
        """Return entry ID."""
        return self.config_entry.entry_id

    async def _async_update_data(self) -> EsiosApiData:
        """Update electricity prices from the ESIOS API."""
        try:
            api_data = await self.api.async_update_all(self.data, dt_util.utcnow())
        except BadApiTokenAuthError as exc:
            _LOGGER.error("Error de autenticación con el Token de ESIOS en PVPC Pro")
            raise ConfigEntryAuthFailed from exc
        except KeyError as exc:
            _LOGGER.error(
                "Falta una clave en el diccionario de la API (ESIOS): %s", exc
            )
            raise UpdateFailed(f"Clave no encontrada: {exc}") from exc
        except Exception as exc:
            _LOGGER.error("Error inesperado en PVPC Pro: %s", exc)
            raise UpdateFailed(exc) from exc

        if (
            not api_data
            or not api_data.sensors
            or not any(api_data.availability.values())
        ):
            _LOGGER.warning(
                "PVPC Pro: No se han podido recuperar datos de ESIOS (sensores vacíos)"
            )
            raise UpdateFailed

        return api_data
