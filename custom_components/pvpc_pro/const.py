"""
Constant values for PVPC REE Data (Pro Version).
Modified and maintained by Javisen - 2026.
"""

from .aiopvpc.const import TARIFFS
import voluptuous as vol

DOMAIN = "pvpc_pro"
DEFAULT_NAME = "PVPC REE Data"
ATTR_POWER = "power"
ATTR_POWER_P3 = "power_p3"
ATTR_TARIFF = "tariff"
CONF_USE_API_TOKEN = "use_api_token"
VALID_POWER = vol.All(vol.Coerce(float), vol.Range(min=1.0, max=15.0))
VALID_TARIFF = vol.In(TARIFFS)
DEFAULT_TARIFF = TARIFFS[0]
