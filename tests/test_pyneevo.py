"""Tests for pyneevo. All data is synthetic and nothing touches the network."""

import asyncio
import json
import unittest
from unittest.mock import patch

from aiohttp.client_exceptions import ClientError

from pyneevo import NeeVoApiInterface
from pyneevo.api import HEADERS
from pyneevo.errors import (
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
    NeeVoConnectionError,
    NeeVoTimeoutError,
    PyNeeVoError,
)

EMAIL = "tester@example.com"
PASSWORD = "not-a-real-password"


def device(tank_id="tank-1", **fields):
    """Build a synthetic device record."""
    record = {"Id": tank_id, "CustomName": "Test Tank", "Level": 62}
    record.update(fields)
    return record


class FakeResponse:
    """Stand in for an aiohttp response."""

    def __init__(self, status=200, payload=None):
        self.status = status
        self.payload = payload

    async def json(self, content_type="application/json"):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeRequest:
    """Stand in for the context manager returned by ``session.get``."""

    def __init__(self, result):
        self.result = result

    async def __aenter__(self):
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result

    async def __aexit__(self, *exc_info):
        return False


class FakeSession:
    """Stand in for an aiohttp session that plays back queued results."""

    def __init__(self, *results):
        self.results = list(results)
        self.requests = []
        self.closed = False

    def get(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return FakeRequest(self.results.pop(0))

    async def close(self):
        self.closed = True


def client(*results):
    """Return a client using a fake session, plus that session."""
    session = FakeSession(*results)
    return NeeVoApiInterface(EMAIL, PASSWORD, session=session), session


class ErrorTests(unittest.IsolatedAsyncioTestCase):
    """Every failure surfaces as a specific library error."""

    async def test_login_success(self):
        session = FakeSession(FakeResponse(200))
        api = await NeeVoApiInterface.login(EMAIL, PASSWORD, session=session)
        self.assertIsInstance(api, NeeVoApiInterface)
        self.assertTrue(session.requests[0][0].endswith(".svc/Login"))

    async def test_credentials_sent_as_basic_auth_header(self):
        session = FakeSession(FakeResponse(200))
        await NeeVoApiInterface.login("a@example.com", "pw", session=session)
        kwargs = session.requests[0][1]
        # base64 of "a@example.com:pw"
        self.assertEqual(
            kwargs["headers"]["Authorization"], "Basic YUBleGFtcGxlLmNvbTpwdw=="
        )
        self.assertNotIn("auth", kwargs)

    async def test_shared_headers_do_not_keep_credentials(self):
        session = FakeSession(FakeResponse(200))
        await NeeVoApiInterface.login(EMAIL, PASSWORD, session=session)
        self.assertNotIn("Authorization", HEADERS)

    async def test_login_401_is_invalid_credentials(self):
        with self.assertRaises(InvalidCredentialsError):
            await NeeVoApiInterface.login(
                EMAIL, PASSWORD, session=FakeSession(FakeResponse(401))
            )

    async def test_fetch_401_is_invalid_credentials(self):
        api, _ = client(FakeResponse(401))
        with self.assertRaises(InvalidCredentialsError):
            await api.get_tanks_info()

    async def test_refresh_401_is_invalid_credentials(self):
        api, _ = client(FakeResponse(401))
        with self.assertRaises(InvalidCredentialsError):
            await api.refresh_tanks()

    async def test_http_error_carries_status(self):
        for call in ("get_tanks_info", "refresh_tanks", "_authenticate"):
            with self.subTest(call=call):
                api, _ = client(FakeResponse(502))
                with self.assertRaises(GenericHTTPError) as caught:
                    await getattr(api, call)()
                self.assertEqual(caught.exception.status, 502)
                self.assertIn("502", str(caught.exception))

    def test_http_error_message_only_still_works(self):
        err = GenericHTTPError("503")
        self.assertEqual(str(err), "503")
        self.assertIsNone(err.status)

    async def test_network_error_is_wrapped_and_compatible(self):
        api, _ = client(ClientError("connection reset"))
        with self.assertRaises(NeeVoConnectionError) as caught:
            await api.get_tanks_info()
        self.assertIsInstance(caught.exception, PyNeeVoError)
        self.assertIsInstance(caught.exception, ClientError)
        self.assertIsInstance(caught.exception.__cause__, ClientError)

    async def test_timeout_is_wrapped_and_compatible(self):
        api, _ = client(asyncio.TimeoutError())
        with self.assertRaises(NeeVoTimeoutError) as caught:
            await api.get_tanks_info()
        self.assertIsInstance(caught.exception, PyNeeVoError)
        self.assertIsInstance(caught.exception, NeeVoConnectionError)
        self.assertIsInstance(caught.exception, TimeoutError)

    async def test_invalid_json_is_invalid_format(self):
        bad_json = json.JSONDecodeError("bad", "<html>", 0)
        api, _ = client(FakeResponse(200, bad_json))
        with self.assertRaises(InvalidResponseFormat):
            await api.get_tanks_info()

    async def test_unexpected_shapes_are_invalid_format(self):
        for payload in (
            {"Message": "Error"},
            "oops",
            None,
            ["not-a-record"],
            [{"CustomName": "no id"}],
            [{"Id": None}],
        ):
            with self.subTest(payload=payload):
                api, _ = client(FakeResponse(200, payload))
                with self.assertRaises(InvalidResponseFormat):
                    await api.get_tanks_info()

    async def test_credentials_absent_from_error_text(self):
        api, _ = client(ClientError("connection reset"))
        with self.assertRaises(NeeVoConnectionError) as caught:
            await api.get_tanks_info()
        self.assertNotIn(PASSWORD, str(caught.exception))


class SessionTests(unittest.IsolatedAsyncioTestCase):
    """Sessions are shared when supplied and cleaned up when owned."""

    async def test_supplied_session_is_left_open(self):
        api, session = client(FakeResponse(200, [device()]))
        await api.refresh_tanks()
        self.assertFalse(session.closed)

    async def test_own_session_is_closed_on_success(self):
        session = FakeSession(FakeResponse(200, [device()]))
        with patch("pyneevo.api.ClientSession", return_value=session):
            await NeeVoApiInterface(EMAIL, PASSWORD).refresh_tanks()
        self.assertTrue(session.closed)

    async def test_own_session_is_closed_on_failure(self):
        session = FakeSession(FakeResponse(500))
        with patch("pyneevo.api.ClientSession", return_value=session):
            with self.assertRaises(GenericHTTPError):
                await NeeVoApiInterface(EMAIL, PASSWORD).refresh_tanks()
        self.assertTrue(session.closed)

    async def test_timeout_setting_reaches_the_request(self):
        session = FakeSession(FakeResponse(200))
        await NeeVoApiInterface.login(EMAIL, PASSWORD, session=session, timeout=5)
        self.assertEqual(session.requests[0][1]["timeout"].total, 5)


if __name__ == "__main__":
    unittest.main()
