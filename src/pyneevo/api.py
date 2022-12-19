
# Class for interfacing with http api
import requests

from src.pyneevo.tank import Tank
from typing import Type, TypeVar, List, Dict, Optional

ApiType = TypeVar("ApiType", bound="EcoNetApiInterface")


class NeeVoApiInterface:
    # Constructor
    def __init__(self, email: str, password: str):
        # Set email and password
        self.email = email
        self.password = password

        # Set base url
        self.base_url = "https://ws.otodatanetwork.com"

        # Set headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "pyneevo/1.0.0",
        }

        # Set session
        self.session = requests.Session()

        # Set class properties
        self._tanks: Dict = {}

    # Get Devices
    async def _get_all_tanks(self):
        # Get devices
        response = self.session.get(
            f"{self.base_url}/neevoapp/v1/DataService.svc/GetAllDisplayPropaneDevices",
            headers=self.headers,
            auth=(self.email, self.password)
        )

        for _tank in response.json():
            _equip_obj = Tank(_tank, self)
            self._tanks[_tank.get('Id')] = _equip_obj

    async def get_tanks(self):
        if not self._tanks:
            await self._get_all_tanks()
        return self._tanks

        # Get Device Status
    def get_device_status(self, device_id: str):
        # Get device status
        response = self.session.get(
            f"{self.base_url}/neevoapp/v1/DataService.svc/GetPropaneLevels/{device_id}",
            headers=self.headers,
            auth=(self.email, self.password)
        )

        for _tank in response.json():
            _equip_obj = Tank(_tank, self)
            self._tanks[_tank.get('Id')] = _equip_obj

        # Return response
        return response