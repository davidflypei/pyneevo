"""Define Nee-Vo tank classes."""

import logging

from enum import Enum
from typing import Dict, Tuple, Union

_LOGGER = logging.getLogger(__name__)


class Tank:
    """Define a Nee-Vo tank."""

    def __init__(self, tank_data: dict, api_interface):
        """Initialize."""
        self._api_interface = api_interface
        self._tank_data = tank_data
        self._update_callback = None

    def set_update_callback(self, callback):
        self._update_callback = callback

    def _update_tank_info(self, update: dict):
        _set = False
        if update.get('Id') == self.id:
            for key, value in update.items():
                _LOGGER.debug(f"Before update: {key}: {self._tank_data.get(key)}")
                try:
                    if isinstance(value, Dict):
                        for _key, _value in value.items():
                            self._tank_data[key][_key] = _value
                            _LOGGER.debug("Updating [%s][%s] = %s", key, _key, _value)
                    else:
                        if isinstance(self._tank_data.get(key), Dict):
                            if self._tank_data[key].get("value") is not None:
                                self._tank_data[key]["value"] = value
                                _LOGGER.debug("Updating [%s][value] = %s", key, value)
                        else:
                            self._tank_data[key] = value
                            _LOGGER.debug("Updating [%s] = %s", key, value)
                except Exception:
                    _LOGGER.error("Failed to update with message: %s", update)
                _LOGGER.debug("After update %s : %s", key, self._tank_data.get(key))
                _set = True
        else:
            _LOGGER.debug("Invalid update for tank: %s", update)

        if self._update_callback is not None and _set:
            _LOGGER.debug("Calling the call back to notify updates have occurred")
            self._update_callback()

    @property
    def id(self) -> str:
        """Return the ID of the tank."""
        return self._tank_data['Id']

    @property
    def name(self) -> str:
        """Return the name of the tank."""
        return self._tank_data['CustomName']

    @property
    def product(self) -> str:
        """Return the type of the tank."""
        return self._tank_data['product']

    @property
    def data(self) -> dict:
        """Return the raw data of the tank."""
        return self._tank_data

    @property
    def level(self) -> float:
        """Return the level of the tank."""
        return self._tank_data['Level']

    @property
    def serial_number(self) -> str:
        """Return the serial number of the tank."""
        return self._tank_data['SerialNumber']

