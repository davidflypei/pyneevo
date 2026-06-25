# PyNeeVo

An unofficial asynchronous Python library for interacting with the Nee-Vo tank monitoring platform API.

PyNeeVo allows Python applications to authenticate with Nee-Vo and retrieve propane tank information and readings from connected devices.

## Features

* Asynchronous API built with `aiohttp`
* Username and password authentication
* Retrieve all available tank information
* Refresh tank data from the Nee-Vo platform

## Installation

```bash
pip install pyneevo
```

## Quick Start

```python
from pyneevo import NeeVoApiInterface
from pyneevo.errors import (
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)

email = "user@example.com"
password = "your-password"

async def main():
    # Login
    try:
        api = await NeeVoApiInterface.login(
            email,
            password=password,
        )
    except InvalidCredentialsError:
        print("Invalid credentials")
        return

    # Retrieve tank information
    try:
        tanks = await api.get_tanks_info()
    except (GenericHTTPError, InvalidResponseFormat) as err:
        print(f"Failed to retrieve tank information: {err}")
        return

    # Display tank data
    for tank in tanks:
        print(
            f"ID: {tank.id} "
            f"Name: {tank.name} "
            f"Level: {tank.level}%"
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Refreshing Tank Data

Refreshing indevidual devices is not yet implemented. As a result, refreshing data updates all devices associated with the account.

```python
await api.refresh_tanks()

tanks = await api.get_tanks_info()

for tank in tanks:
    print(
        f"ID: {tank.id} "
        f"Name: {tank.name} "
        f"Level: {tank.level}%"
    )
```

## Available Methods

### Authentication

```python
api = await NeeVoApiInterface.login(
    email,
    password=password,
)
```

Authenticates with the Nee-Vo platform and returns an authenticated API interface instance.

### Get Tank Information

```python
tanks = await api.get_tanks_info()
```

Returns a list of all tanks associated with the authenticated account.

### Refresh Tank Data

```python
await api.refresh_tanks()
```

Requests that Nee-Vo refresh all tank readings associated with the account.

## Error Handling

PyNeeVo exposes several exceptions that can be used for handling API and authentication failures.

```python
from pyneevo.errors import (
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
    PyNeeVoError,
)

try:
    tanks = await api.get_tanks_info()
except InvalidCredentialsError:
    print("Invalid credentials")
except InvalidResponseFormat:
    print("Unexpected response from Nee-Vo")
except GenericHTTPError:
    print("HTTP error communicating with Nee-Vo")
except PyNeeVoError:
    print("General PyNeeVo error")
```

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

## License

This project is licensed under the MIT License.
