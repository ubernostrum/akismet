"""
Common definitions used by both the sync and async Akismet implementations.

"""

# SPDX-License-Identifier: BSD-3-Clause

import enum
import os
import sys
import textwrap
import typing

import httpx

from . import _exceptions, _version

# Private constants.
# -------------------------------------------------------------------------------

_API_URL = "https://rest.akismet.com"
_API_V11 = "1.1"
_API_V12 = "1.2"
_COMMENT_CHECK = "comment-check"
_KEY_SITES = "key-sites"
_REQUEST_METHODS = typing.Literal["GET", "POST"]  # pylint: disable=invalid-name
_SUBMISSION_RESPONSE = "Thanks for making the web a better place."
_SUBMIT_HAM = "submit-ham"
_SUBMIT_SPAM = "submit-spam"
_USAGE_LIMIT = "usage-limit"
_VERIFY_KEY = "verify-key"

_KEY_ENV_VAR = "PYTHON_AKISMET_API_KEY"
_URL_ENV_VAR = "PYTHON_AKISMET_BLOG_URL"

_TIMEOUT = float(os.getenv("PYTHON_AKISMET_TIMEOUT", "1.0"))

_OPTIONAL_KEYS = [
    "blog_charset",
    "blog_lang",
    "comment_author",
    "comment_author_email",
    "comment_author_url",
    "comment_content",
    "comment_context",
    "comment_date_gmt",
    "comment_post_modified_gmt",
    "comment_type",
    "honeypot_field_name",
    "is_test",
    "permalink",
    "recheck_reason",
    "referrer",
    "user_agent",
    "user_role",
]


# Public constants.
# -------------------------------------------------------------------------------

USER_AGENT = (
    f"akismet.py/{_version.LIBRARY_VERSION} | Python/"
    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
)


# Public classes.
# -------------------------------------------------------------------------------


class CheckResponse(enum.IntEnum):
    """
    Possible response values from an Akismet content check, including the
    possibility of the "discard" response, modeled as an :class:`enum.IntEnum`.

    """

    HAM = 0
    SPAM = 1
    DISCARD = 2


class Config(typing.NamedTuple):
    """
    A :func:`~collections.namedtuple` representing Akismet configuration, consisting
    of a key and a URL.

    You only need to use this if you're manually configuring an Akismet API client
    (which should be rare) rather than letting the ``validated_client()`` constructor
    automatically read the configuration from environment variables.

    """

    key: str
    url: str


# Private helper functions.
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


def _protocol_error(operation: str, response: httpx.Response) -> typing.NoReturn:
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


def _try_discover_config() -> Config:
    """
    Attempt to discover and return an Akismet configuration from the environment.

    :raises akismet.ConfigurationError: When either or both of the API key and
       URL are missing, or if the URL does not begin with ``"http://"`` or
       ``https://``.

    """
    key = os.getenv(_KEY_ENV_VAR, None)
    url = os.getenv(_URL_ENV_VAR, None)
    if not all([key, url]):
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

            Akismet requires the full URL including the leading
            'http://' or 'https://'.
            """
            )
        )
    return Config(key=key, url=url)
