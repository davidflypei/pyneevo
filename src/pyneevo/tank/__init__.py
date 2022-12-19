"""Define Nee-Vo tank classes."""

import logging

from enum import Enum

_LOGGER = logging.getLogger(__name__)


class Tank:
    """Define a Nee-Vo tank."""

    def __init__(self, tank_data: dict, api_interface):
        """Initialize."""
        self._api_interface = api_interface
        self._data = tank_data

    @property
    def id(self) -> str:
        """Return the ID of the tank."""
        return self._data['Id']

    @property
    def name(self) -> str:
        """Return the name of the tank."""
        return self._data['CustomName']

    @property
    def product(self) -> str:
        """Return the type of the tank."""
        return self._data['product']

    @property
    def data(self) -> dict:
        """Return the raw data of the tank."""
        return self._data

    @property
    def level(self) -> float:
        """Return the level of the tank."""
        return self._data['Level']

    @property
    def serial_number(self) -> str:
        """Return the serial number of the tank."""
        return self._data['SerialNumber']

