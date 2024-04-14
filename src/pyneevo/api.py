import logging

from aiohttp import ClientSession, ClientTimeout, BasicAuth
from aiohttp.client_exceptions import ClientError

from pyneevo.tank import Tank
from pyneevo.errors import PyNeeVoError, InvalidCredentialsError, GenericHTTPError, InvalidResponseFormat
from typing import Type, TypeVar, List, Dict, Optional

_LOGGER = logging.getLogger(__name__)

ApiType = TypeVar("ApiType", bound="EcoNetApiInterface")

HOST = "ws.otodatanetwork.com"
REST_URL = f"https://{HOST}/neevoapp/v1/DataService.svc/"
HEADERS = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "pyneevo/1.0.0",
        }


class NeeVoApiInterface:
    # Constructor
    def __init__(self, email: str, password: str):
        # Set email and password
        self.email = email
        self.password = password

        # Set class properties
        self._tanks: Dict = {}

    @classmethod
    async def login(cls: Type[ApiType], email: str, password: str) -> ApiType:
        """Login to the Nee-Vo API."""
        # Create instance
        instance = cls(email, password)

        await instance._authenticate()
        return instance

    # Authenticate
    async def _authenticate(self) -> None:
        _LOGGER.debug(f"Authenticating with Nee-Vo API")
        _session = ClientSession()
        try:
            async with _session.get(
                f"{REST_URL}/Login",
                headers=HEADERS,
                auth=BasicAuth(self.email, self.password),
            ) as response:
                if response.status == 401:
                    raise InvalidCredentialsError("Invalid credentials")
                elif response.status != 200:
                    raise GenericHTTPError(f"HTTP error: {response.status}")
        except ClientError as err:
            raise err
        finally:
            await _session.close()

    async def GetAllDisplayPropaneDevices(self) -> Dict:
        _session = ClientSession()
        responsejson = {}
        try:
            async with _session.get(
                f"{REST_URL}/GetAllDisplayPropaneDevices",
                headers=HEADERS,
                auth=BasicAuth(self.email, self.password)
            ) as response:
                if response.status == 200:
                    responsejson = await response.json()
                else:
                    raise GenericHTTPError(response.status)
        except ClientError as err:
            raise err
        finally:
            await _session.close()
            return responsejson

    # Get Tanks
    async def _get_tanks(self) -> None:
        tanks = await self.GetAllDisplayPropaneDevices()
        for _tank in tanks:
            _tank_obj = Tank(_tank, self)
            self._tanks[_tank.get('Id')] = _tank_obj

    async def get_tanks_info(self) -> Dict:
        if not self._tanks:
            await self._get_tanks()
        return self._tanks

    async def refresh_tanks(self) -> None:
        """Refresh the tank data."""
        _tanks: Dict = await self.GetAllDisplayPropaneDevices()
        for _tank in _tanks:
            _tank_obj: Tank = None
            tank = self._tanks.get(_tank.get('Id'))
            if tank:
                tank._update_tank_info(_tank)


    #     # Get Device Status
    # def get_device_status(self, device_id: str):
    #     # Get device status
    #     response = self.session.get(
    #         f"{self.base_url}/neevoapp/v1/DataService.svc/GetPropaneLevels/{device_id}",
    #         headers=self.headers,
    #         auth=(self.email, self.password)
    #     )
    #
    #     for _tank in response.json():
    #         _equip_obj = Tank(_tank, self)
    #         self._tanks[_tank.get('Id')] = _equip_obj
    #
    #     # Return response
    #     return response