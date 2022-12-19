"""Define package errors."""


class PyNeeVoError(Exception):
    """A base error."""

    pass


class InvalidCredentialsError(PyNeeVoError):
    """An error related to invalid requests."""

    pass


class InvalidResponseFormat(PyNeeVoError):
    """An error related to invalid requests."""

    pass


class GenericHTTPError(PyNeeVoError):
    """An error related to invalid requests."""

    pass