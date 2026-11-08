# PyNeeVo

An unofficial asynchronous Python library for interacting with the Nee-Vo tank monitoring platform API.

PyNeeVo allows Python applications to authenticate with Nee-Vo and retrieve propane tank information and readings from connected devices.

## Features

* Asynchronous API built with `aiohttp`
* Username and password authentication
* Retrieve all available tank information
* Refresh tank data from the Nee-Vo platform
* Specific errors for bad credentials, connection problems, timeouts and unexpected responses
* Optional shared `aiohttp` session and configurable timeout

## Installation

```bash
pip install pyneevo
```

## Quick Start

```python
import asyncio

from pyneevo import NeeVoApiInterface
from pyneevo.errors import InvalidCredentialsError, PyNeeVoError

email = "user@example.com"
password = "your-password"

async def main():
    try:
        api = await NeeVoApiInterface.login(email, password)
        tanks = await api.get_tanks_info()
    except InvalidCredentialsError:
        print("Invalid credentials")
        return
    except PyNeeVoError as err:
        print(f"Failed to retrieve tank information: {err}")
        return

    for tank in tanks.values():
        print(
            f"ID: {tank.id} "
            f"Name: {tank.name} "
            f"Level: {tank.level}%"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Refreshing Tank Data

Refreshing indevidual devices is not yet implemented. As a result, refreshing data updates all devices associated with the account.

```python
await api.refresh_tanks()

tanks = await api.get_tanks_info()

for tank in tanks.values():
    print(
        f"ID: {tank.id} "
        f"Name: {tank.name} "
        f"Level: {tank.level}%"
    )
```

## Available Methods

### Authentication

```python
api = await NeeVoApiInterface.login(email, password)
```

Checks the credentials with the Nee-Vo platform and returns an API interface instance.

Two optional arguments are available:

```python
api = await NeeVoApiInterface.login(
    email,
    password,
    session=my_aiohttp_session,  # Shared session. You stay responsible for closing it.
    timeout=30,  # Limit in seconds for each request. The default is 30.
)
```

### Get Tank Information

```python
tanks = await api.get_tanks_info()
```

Returns a dictionary of all tanks associated with the account, keyed by tank ID.

### Refresh Tank Data

```python
await api.refresh_tanks()
```

Requests that Nee-Vo refresh all tank readings associated with the account.

## Error Handling

Every error raised by PyNeeVo is a `PyNeeVoError`.

```python
from pyneevo.errors import (
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
    NeeVoConnectionError,
    NeeVoTimeoutError,
    PyNeeVoError,
)

try:
    tanks = await api.get_tanks_info()
except InvalidCredentialsError:
    print("Invalid credentials")
except InvalidResponseFormat:
    print("Unexpected response from Nee-Vo")
except NeeVoTimeoutError:
    print("Nee-Vo did not answer in time")
except NeeVoConnectionError:
    print("Could not reach Nee-Vo")
except GenericHTTPError as err:
    print(f"HTTP error communicating with Nee-Vo: {err.status}")
```

`NeeVoTimeoutError` is a kind of `NeeVoConnectionError`, so catch it first if you handle them differently.

## Current API Coverage

PyNeeVo currently implements support for the Nee-Vo `GetAllDisplayPropaneDevices` endpoint.

Additional endpoints may be added in future releases.

If there is a endpoint you need please create an issue. Pull Requests are also welcome.

## Intended Audience

PyNeeVo is intended for Python developers who want to integrate Nee-Vo tank data into:

* Home automation platforms
* Monitoring dashboards
* Notification systems
* Reporting tools
* Custom integrations

## Development

The tests use only the standard library plus `aiohttp`, and never touch the network:

```bash
pip install -e .
python -m unittest discover -s tests -t .
```

## License

This project is licensed under the MIT License.
