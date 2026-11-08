"""Define Nee-Vo tank classes."""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Callable, NamedTuple, Optional

_LOGGER = logging.getLogger(__name__)

# .NET JSON date: epoch milliseconds (absolute UTC) plus an optional display
# offset that does not change the instant.
_NET_DATE = re.compile(r"/Date\((-?\d+)(?:[-+]\d{4})?\)/")


def parse_net_date(value: Any) -> Optional[datetime]:
    """Convert a .NET JSON date to a UTC datetime, or ``None`` if it is invalid."""
    if not isinstance(value, str):
        return None
    match = _NET_DATE.fullmatch(value)
    if match is None:
        return None
    try:
        return datetime.fromtimestamp(int(match.group(1)) / 1000, timezone.utc)
    except (OverflowError, ValueError, OSError):
        return None


class LevelReading(NamedTuple):
    """One entry from a tank's level history."""

    date: datetime
    level: Optional[float]
    consumption: Optional[float]


class Tank:
    """Define a Nee-Vo tank.

    Optional properties return ``None`` when the API omits the field, so one
    renamed field cannot crash the code reading the others.
    """

    def __init__(self, tank_data: dict, api_interface: Any) -> None:
        """Initialize."""
        self._api_interface = api_interface
        self._tank_data = tank_data
        self._update_callback: Optional[Callable[[], None]] = None

    def set_update_callback(self, callback: Callable[[], None]) -> None:
        """Set a function to call whenever this tank's data is replaced."""
        self._update_callback = callback

    def _update_tank_info(self, update: dict) -> None:
        """Replace this tank's data with a newer record for the same tank.

        Replacing rather than merging means a field the API stops sending
        disappears instead of keeping its last value and looking current.
        """
        if update.get("Id") != self.id:
            _LOGGER.debug("Ignoring an update meant for a different tank")
            return

        self._tank_data = update
        if self._update_callback is not None:
            self._update_callback()

    def _first_value(self, *keys: str) -> Any:
        """Return the first non-null value among possible field names."""
        for key in keys:
            value = self._tank_data.get(key)
            if value is not None:
                return value
        return None

    @property
    def id(self) -> Any:
        """Return the ID of the tank."""
        return self._tank_data["Id"]

    @property
    def name(self) -> Optional[str]:
        """Return the name of the tank."""
        return self._tank_data.get("CustomName")

    @property
    def product(self) -> Optional[str]:
        """Return the product type of the tank."""
        return self._first_value("Product", "product")

    @property
    def data(self) -> dict:
        """Return the raw data of the tank."""
        return self._tank_data

    @property
    def level(self) -> Any:
        """Return the fill level of the tank in percent."""
        return self._first_value("CurrentLevel", "Level")

    @property
    def serial_number(self) -> Any:
        """Return the serial number of the tank."""
        return self._tank_data.get("SerialNumber")

    @property
    def tank_capacity(self) -> Any:
        """Return the capacity of the tank."""
        return self._tank_data.get("TankCapacity")

    @property
    def tank_last_pressure(self) -> Any:
        """Return the last reported pressure of the tank."""
        return self._tank_data.get("TankLastPressure")

    @property
    def tank_last_pressure_unit(self) -> Optional[str]:
        """Return the unit of the last reported pressure."""
        return self._tank_data.get("TankPressureDisplayUnitSymbol")

    @property
    def last_reading(self) -> Optional[datetime]:
        """Return when the monitor last reported, in UTC, or ``None`` if unknown."""
        return parse_net_date(self._tank_data.get("LastReadingDate"))
