"""
ESIOS API handler for HomeAssistant. Utilities.
Modified and maintained by Javisen - 2026.
"""

from datetime import datetime
from .const import UTC_TZ


def ensure_utc_time(ts: datetime) -> datetime:

    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC_TZ)

    if str(ts.tzinfo) != str(UTC_TZ):
        return ts.astimezone(UTC_TZ)

    return ts
