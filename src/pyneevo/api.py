"""Client for the Nee-Vo API."""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from pyneevo.errors import (
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
    NeeVoConnectionError,
    NeeVoTimeoutError,
)
from pyneevo.tank import Tank

_LOGGER = logging.getLogger(__name__)

ApiType = TypeVar("ApiType", bound="NeeVoApiInterface")

HOST = "ws.otodatanetwork.com"
REST_URL = f"https://{HOST}/neevoapp/v1/DataService.svc/"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "pyneevo/1.0.0",
}
DEFAULT_TIMEOUT = 30.0


class NeeVoApiInterface:
    """Talk to the Nee-Vo API for one account."""

    def __init__(
        self,
        email: str,
        password: str,
        session: Optional[ClientSession] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize.

        ``session`` is an optional aiohttp session owned by the caller, who
        stays responsible for closing it. Without one, each request opens and
        closes its own. ``timeout`` is the limit in seconds for each request.
        """
        self.email = email
        self.password = password
        self._session = session
        self._timeout = timeout
        self._tanks: Dict[Any, Tank] = {}

    @classmethod
    async def login(
        cls: Type[ApiType],
        email: str,
        password: str,
        session: Optional[ClientSession] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> ApiType:
        """Check the credentials and return a ready-to-use client."""
        instance = cls(email, password, session=session, timeout=timeout)
        await instance._authenticate()
        return instance

    async def _request(self, endpoint: str, parse_json: bool = False) -> Any:
        """Send one GET request and translate every failure to a library error."""
        # Built by hand because aiohttp is removing BasicAuth in version 4. Latin-1
        # matches what aiohttp's BasicAuth used by default.
        credentials = f"{self.email}:{self.password}".encode("latin1")
        headers = {
            **HEADERS,
            "Authorization": f"Basic {base64.b64encode(credentials).decode('ascii')}",
        }
        session = self._session if self._session is not None else ClientSession()
        try:
            async with session.get(
                f"{REST_URL}{endpoint}",
                headers=headers,
                timeout=ClientTimeout(total=self._timeout),
            ) as response:
                if response.status == 401:
                    raise InvalidCredentialsError("Invalid credentials")
                if response.status != 200:
                    raise GenericHTTPError(
                        f"HTTP error: {response.status}", status=response.status
                    )
                if not parse_json:
                    return None
                try:
                    return await response.json(content_type=None)
                except ValueError as err:
                    raise InvalidResponseFormat("Response is not valid JSON") from err
        except asyncio.TimeoutError as err:
            raise NeeVoTimeoutError(
                f"No response from Nee-Vo within {self._timeout} seconds"
            ) from err
        except ClientError as err:
            raise NeeVoConnectionError(str(err) or type(err).__name__) from err
        finally:
            if self._session is None:
                await session.close()

    async def _authenticate(self) -> None:
        """Check the credentials against the API."""
        _LOGGER.debug("Authenticating with Nee-Vo API")
        await self._request("Login")

    async def GetAllDisplayPropaneDevices(self) -> List[Dict[str, Any]]:
        """Return the raw device records for the account."""
        devices = await self._request("GetAllDisplayPropaneDevices", parse_json=True)
        if not isinstance(devices, list):
            raise InvalidResponseFormat("Expected a list of devices")
        for device in devices:
            if not isinstance(device, dict) or device.get("Id") is None:
                raise InvalidResponseFormat("Device record has no Id")
        return devices

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