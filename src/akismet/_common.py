"""
Common definitions used by both the sync and async Akismet implementations.

"""

# SPDX-License-Identifier: BSD-3-Clause

import enum
import os
import sys
import textwrap
from collections.abc import Mapping
from importlib.metadata import version
from typing import Literal, NamedTuple, NoReturn, TypedDict, cast

import httpx

from . import _exceptions

# Private constants.
# -------------------------------------------------------------------------------

_API_URL = "https://rest.akismet.com"
_API_V11 = "1.1"
_API_V12 = "1.2"
_COMMENT_CHECK = "comment-check"
_KEY_SITES = "key-sites"
_REQUEST_METHODS = Literal["GET", "POST"]  # pylint: disable=invalid-name
_SUBMISSION_RESPONSE = "Thanks for making the web a better place."
_SUBMIT_HAM = "submit-ham"
_SUBMIT_SPAM = "submit-spam"
_USAGE_LIMIT = "usage-limit"
_VERIFY_KEY = "verify-key"

_KEY_ENV_VAR = "PYTHON_AKISMET_API_KEY"
_URL_ENV_VAR = "PYTHON_AKISMET_BLOG_URL"

_TIMEOUT = float(os.getenv("PYTHON_AKISMET_TIMEOUT", "1.0"))


# Public constants.
# -------------------------------------------------------------------------------

USER_AGENT = (
    f"akismet.py/{version('akismet')} | Python/"
    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
)


# Public classes.
# -------------------------------------------------------------------------------


class AkismetArguments(TypedDict, total=False):
    """
    A :class:`~typing.TypedDict` representing the optional keyword arguments accepted by
    the comment-check, submit-ham, and submit-spam Akismet API operations.

    """

    blog_charset: str
    blog_lang: str
    comment_author: str
    comment_author_email: str
    comment_author_url: str
    comment_content: str
    comment_context: str
    comment_date_gmt: str
    comment_post_modified_gmt: str
    comment_type: str
    honeypot_field_name: str
    is_test: bool
    permalink: str
    recheck_reason: str
    referrer: str
    user_agent: str
    user_role: str


class CheckResponse(enum.IntEnum):
    """
    Possible response values from an Akismet content check, including the
    possibility of the "discard" response, modeled as an :class:`enum.IntEnum`.

    """

    HAM = 0
    SPAM = 1
    DISCARD = 2


class Config(NamedTuple):
    """
    A :func:`~collections.namedtuple` representing Akismet configuration, consisting
    of a key and a URL.

    You only need to use this if you're manually configuring an Akismet API client
    rather than letting the configuration be read automatically from environment
    variables.

    """

    key: str
    url: str


# Private helper functions.
# -------------------------------------------------------------------------------


# Functions which throw errors for various situations.
# -------------------------------------------------------------------------------


def _configuration_error(config: Config) -> NoReturn:
    """
    Raise an appropriate exception for invalid configuration.

    """
    raise _exceptions.APIKeyError(
        textwrap.dedent(
            f"""
            Akismet API key and/or blog URL were invalid.

            Found API key: {config.key}
            Found URL: {config.url}
            """
        )
    )


def _protocol_error(operation: str, response: httpx.Response) -> NoReturn:
    """
    Raise an appropriate exception for unexpected API responses.

    """
    raise _exceptions.ProtocolError(
        textwrap.dedent(
            f"""
        Received unexpected or non-standard response from Akismet API.

        API operation was: {operation}
        API response received was: {response.text}
        Debug header value was: {response.headers.get('X-akismet-debug-help', None)}
        """
        )
    )


# Functions which help autodiscover/autofill configuration.
# -------------------------------------------------------------------------------


def _get_async_http_client() -> httpx.AsyncClient:
    """
    Return an asynchronous HTTP client for interacting with the Akismet API.

    """
    return httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=_TIMEOUT)


def _get_sync_http_client() -> httpx.Client:
    """
    Return a synchronous HTTP client for interacting with the Akismet API.

    """
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=_TIMEOUT)


def _try_discover_config() -> Config:
    """
    Attempt to discover and return an Akismet configuration from the environment.

    :raises akismet.ConfigurationError: When either or both of the API key and
       URL are missing, or if the URL does not begin with ``"http://"`` or
       ``https://``.

    """
    key = os.getenv(_KEY_ENV_VAR, None)
    url = os.getenv(_URL_ENV_VAR, None)

    if key is None or url is None:
        raise _exceptions.ConfigurationError(
            textwrap.dedent(
                f"""
        Could not find full Akismet configuration.

        Found API key: {key}
        Found blog URL: {url}
        """
            )
        )

    if not url.startswith(("http://", "https://")):
        raise _exceptions.ConfigurationError(
            textwrap.dedent(
                f"""
            Invalid Akismet site URL specified: {url}

            Akismet requires the full URL including the leading 'http://' or 'https://'.
            """
            )
        )
    return Config(key=key, url=url)


# Functions which help process Akismet requests and responses.
# -------------------------------------------------------------------------------


def _handle_akismet_response(endpoint: str, response: httpx.Response) -> httpx.Response:
    """
    Check the response to see if it indicates an invalid key.

    """
    # It's possible to construct a client without performing up-front API key
    # validation, in which case the responses will all have text "invalid". So we check
    # for that and raise an exception when it's detected.
    if endpoint != _VERIFY_KEY and response.text == "invalid":
        raise _exceptions.APIKeyError("Akismet API key and/or site URL are invalid.")
    return response


def _handle_check_response(response: httpx.Response) -> CheckResponse:
    """
    Return the correct result for a response from the comment-check endpoint.

    """
    if response.text == "true":
        if response.headers.get("X-akismet-pro-tip", "") == "discard":
            return CheckResponse.DISCARD
        return CheckResponse.SPAM
    if response.text == "false":
        return CheckResponse.HAM
    _protocol_error(_COMMENT_CHECK, response)


def _handle_submit_response(endpoint: str, response: httpx.Response) -> bool:
    """
    Proces the response from a submit (ham/spam) request.

    """
    if response.text == _SUBMISSION_RESPONSE:
        return True
    _protocol_error(endpoint, response)


def _handle_verify_key_response(response: httpx.Response) -> bool:
    """
    Handle the response from a verify_key() request.

    """
    if response.text == "valid":
        return True
    if response.text == "invalid":
        return False
    _protocol_error(_VERIFY_KEY, response)


def _prepare_post_kwargs(kwargs: Mapping, endpoint: str) -> AkismetArguments:
    """
    Verify that the provided set of keyword arguments is valid for an Akismet POST
    request, returning them if they are or raising UnknownArgumentError if they aren't.

    """
    if unknown_args := [
        k
        for k in kwargs
        if k not in AkismetArguments.__optional_keys__  # pylint: disable=no-member
    ]:
        raise _exceptions.UnknownArgumentError(
            f"Received unknown argument(s) for Akismet operation {endpoint}: "
            f"{', '.join(unknown_args)}"
        )
    return cast(AkismetArguments, kwargs)


def _prepare_request(
    method: _REQUEST_METHODS, api_version: str, endpoint: str, data: dict
) -> tuple[str, dict]:
    """
    From the raw arguments passed to _request(), prepare the correct argument set to
    pass to the HTTP client and return them.

    """
    if method not in ("GET", "POST"):
        raise _exceptions.AkismetError(
            f"Unrecognized request method attempted: {method}."
        )
    request_kwarg = "data" if method == "POST" else "params"
    return f"{_API_URL}/{api_version}/{endpoint}", {request_kwarg: data}
