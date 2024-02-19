"""
Exceptions used by the Akismet clients.

"""

# SPDX-License-Identifier: BSD-3-Clause


class AkismetError(Exception):
    """
    Base exception class for Akismet errors.

    """


class UnknownArgumentError(TypeError, AkismetError):
    """
    Raised when an unknown argument was used as part of an API request.

    """


class RequestError(AkismetError):
    """
    Raised when an unexpected error occurred when making a request to Akismet.

    This is almost always going to be a `chained exception
    <https://peps.python.org/pep-3134/>`_ wrapping an underlying error from the HTTP
    client, so inspecting the exception chain may yield useful debugging information.

    """


class ProtocolError(AkismetError):
    """
    Raised when an unexpected or non-standard response was received from Akismet.

    """


class ConfigurationError(AkismetError):
    """
    Raised when an Akismet configuration error is detected (config missing or
    invalid).

    """


class APIKeyError(ConfigurationError):
    """
    Raised when the supplied Akismet API key/URL are invalid according to the
    verify-key operation.

    This is a subclass of :exc:`~akismet.ConfigurationError`. If you want to detect the
    specific case of an invalid key/URL, catch this exception, while if you just want to
    catch all configuration-related errors (including missing configuration), catch
    ``ConfigurationError`` instead.

    """
