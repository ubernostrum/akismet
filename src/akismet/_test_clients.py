"""
Test versions of the Akismet clients, for use both in Akismet's own testing and for
testing by applications and libraries which use Akismet.

"""

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Optional

import httpx

from . import _common
from ._async_client import AsyncClient
from ._sync_client import SyncClient

if TYPE_CHECKING:  # pragma: no cover
    import akismet

_TEST_KEY = "invalid-test-key"
_TEST_URL = "http://example.com/"

_COMMENT_CHECK_URL = f"/{_common._API_V11}/{_common._COMMENT_CHECK}"
_KEY_SITES_URL = f"/{_common._API_V12}/{_common._KEY_SITES}"
_SUBMIT_HAM_URL = f"/{_common._API_V11}/{_common._SUBMIT_HAM}"
_SUBMIT_SPAM_URL = f"/{_common._API_V11}/{_common._SUBMIT_SPAM}"
_USAGE_LIMIT_URL = f"/{_common._API_V12}/{_common._USAGE_LIMIT}"
_VERIFY_KEY_URL = f"/{_common._API_V11}/{_common._VERIFY_KEY}"

_COMMENT_CHECK_DISCARD_RESPONSE = {
    "content": "true",
    "headers": {"X-akismet-pro-tip": "discard"},
}
_COMMENT_CHECK_HAM_RESPONSE = {"content": "false"}
_COMMENT_CHECK_SPAM_RESPONSE = {"content": "true"}
_VERIFY_KEY_VALID_RESPONSE = {"content": "valid"}
_VERIFY_KEY_INVALID_RESPONSE = {"content": "invalid"}

_KEY_SITES_CSV = {
    # Sample CSV data taken from Akismet's dev docs.
    "content": """Active sites for 123YourAPIKey during 2022-09 (limit:10, offset: 0, total: 4)
Site,Total API Calls,Spam,Ham,Missed Spam,False Positives,Is Revoked
site6735.example.com,14446,33,13,0,9,false
site3026.example.com,8677,101,6,0,0,false
site3737.example.com,4230,65,5,2,0,true
site5653.example.com,2921,30,1,2,6,false"""
}
_KEY_SITES_JSON = {
    # Sample JSON from Akismet's dev docs.
    "json": {
        "2022-09": [
            {
                "site": "site6735.example.com",
                "api_calls": "2072",
                "spam": "2069",
                "ham": "3",
                "missed_spam": "0",
                "false_positives": "4",
                "is_revoked": False,
            },
            {
                "site": "site4748.example.com",
                "api_calls": "1633",
                "spam": "3",
                "ham": "1630",
                "missed_spam": "0",
                "false_positives": "0",
                "is_revoked": True,
            },
        ],
        "limit": 10,
        "offset": 0,
        "total": 2,
    }
}

_BASE_RESPONSE_MAP = {
    _COMMENT_CHECK_URL: _COMMENT_CHECK_SPAM_RESPONSE,
    _SUBMIT_HAM_URL: {"content": _common._SUBMISSION_RESPONSE},
    _SUBMIT_SPAM_URL: {"content": _common._SUBMISSION_RESPONSE},
    _USAGE_LIMIT_URL: {
        # Sample JSON from Akismet's dev docs.
        "json": {
            "limit": 350000,
            "usage": 7463,
            "percentage": "2.13",
            "throttled": False,
        }
    },
    _VERIFY_KEY_URL: _VERIFY_KEY_VALID_RESPONSE,
}


def _make_test_transport(
    comment_check_response: _common.CheckResponse = _common.CheckResponse.SPAM,
    verify_key_response: bool = True,
) -> httpx.MockTransport:
    """
    Build and return an ``httpx`` mock transport based on the given arguments:

    :param comment_check_response: How to classify submitted content.

    :param verify_key_response: Whether to treat the Akismet key/URL as valid.

    """
    custom_responses = {
        _COMMENT_CHECK_URL: {
            _common.CheckResponse.DISCARD: _COMMENT_CHECK_DISCARD_RESPONSE,
            _common.CheckResponse.HAM: _COMMENT_CHECK_HAM_RESPONSE,
            _common.CheckResponse.SPAM: _COMMENT_CHECK_SPAM_RESPONSE,
        }[comment_check_response],
        _VERIFY_KEY_URL: (
            _VERIFY_KEY_VALID_RESPONSE
            if verify_key_response
            else _VERIFY_KEY_INVALID_RESPONSE
        ),
    }
    response_map = {**_BASE_RESPONSE_MAP, **custom_responses}

    def _handler(request: httpx.Request) -> httpx.Response:
        """
        Mock transport handler which returns controlled responses.

        """
        if request.url.path != _KEY_SITES_URL:
            response_args = response_map[request.url.path]
        else:
            # key-sites is the only operation where anything other than the path
            # matters; it has a single query param which controls the response format,
            # so we have to adjust the response to match what was requested.
            response_args = (
                _KEY_SITES_CSV
                if request.url.query == b"format=csv"
                else _KEY_SITES_JSON
            )
        return httpx.Response(
            status_code=HTTPStatus.OK, **response_args
        )  # type: ignore

    return httpx.MockTransport(_handler)


def _make_test_async_http_client(
    comment_check_response: _common.CheckResponse = _common.CheckResponse.SPAM,
    verify_key_response: bool = True,
) -> httpx.AsyncClient:
    """
    Construct and return an ``httpx.AsyncClient`` for testing purposes, based on the
    given arguments.

    :param comment_check_response: The desired comment-check response (ham, spam, or
       discard/"blatant spam").

    :param verify_key_response: The desired verify-key response: :data:`True` for a
       valid configuration, :data:`False` for invalid.

    """
    return httpx.AsyncClient(
        transport=_make_test_transport(comment_check_response, verify_key_response)
    )


def _make_test_sync_http_client(
    comment_check_response: _common.CheckResponse = _common.CheckResponse.SPAM,
    verify_key_response: bool = True,
) -> httpx.Client:
    """
    Construct and return an ``httpx.Client`` for testing purposes, based on the
    given arguments.

    :param comment_check_response: The desired comment-check response (ham, spam, or
       discard/"blatant spam").

    :param verify_key_response: The desired verify-key response: :data:`True` for a
       valid configuration, :data:`False` for invalid.

    """
    return httpx.Client(
        transport=_make_test_transport(comment_check_response, verify_key_response)
    )


class TestAsyncClient(AsyncClient):
    """
    A version of :class:`akismet.AsyncClient` for use in testing.

    This client exposes exactly the same API as :class:`~akismet.AsyncClient`, but will
    *not* make real requests to the Akismet web service. Instead it will return fixed
    responses for most Akismet API operations. The two configurable responses are
    comment-check and verify-key, which can be controlled by subclassing this class and
    setting the following attributes:

    .. attribute:: comment_check_response

       A value from the :class:`akismet.CheckResponse` enum, indicating the desired
       return value of the comment-check operation. Defaults to
       :attr:`~akismet.CheckResponse.SPAM` if not specified. Use this to test code which
       needs to handle the various possible responses from the Akismet API.

    .. attribute:: verify_key_response

       A :data:`bool` indicating the desired return value of the verify-key
       operation. Defaults to :data:`True` if not specified. Use this to test code which
       may need to handle or recover from invalid or missing Akismet configuration.

    Note that although you *can* pass the ``http_client`` argument to the constructors
    as with the base :class:`~akismet.AsyncClient`, this class will ignore that argument
    and instead always uses its own custom HTTP client to produce the desired fixed
    responses.

    For operations other than comment-check and verify-key, the response values will be:

    * submit-ham and submit-spam: :data:`True`

    * key-sites: the sample responses (depending on requested format) given in `the
      Akismet web service documentation for key-sites
      <https://akismet.com/developers/detailed-docs/key-sites-activity/>`_.

    * usage-limit: the sample response given in `the Akismet web service documentation
      for usage-limit <https://akismet.com/developers/detailed-docs/usage-limit/>`_.

    """

    comment_check_response: akismet.CheckResponse = _common.CheckResponse.HAM
    verify_key_response: bool = True

    def __init__(
        self,
        config: Optional[akismet.Config] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Default constructor.

        This overrides the behavior of the parent class to set up a custom HTTP client
        which returns fixed test responses. As a result, any explicit HTTP client passed
        in will be ignored.

        """
        test_client = _make_test_async_http_client(
            comment_check_response=self.comment_check_response,
            verify_key_response=self.verify_key_response,
        )
        super().__init__(config=config, http_client=test_client)


class TestSyncClient(SyncClient):
    """
    A version of :class:`akismet.SyncClient` for use in testing.

    This client exposes exactly the same API as :class:`~akismet.SyncClient`, but will
    *not* make real requests to the Akismet web service. Instead it will return fixed
    responses for most Akismet API operations. The two configurable responses are
    comment-check and verify-key, which can be controlled by subclassing this class and
    setting the following attributes:

    .. attribute:: comment_check_response

       A value from the :class:`akismet.CheckResponse` enum, indicating the desired
       return value of the comment-check operation. Defaults to
       :attr:`~akismet.CheckResponse.SPAM` if not specified. Use this to test code which
       needs to handle the various possible responses from the Akismet API.

    .. attribute:: verify_key_response

       A :data:`bool` indicating the desired return value of the verify-key
       operation. Defaults to :data:`True` if not specified. Use this to test code which
       may need to handle or recover from invalid or missing Akismet configuration.

    Note that although you *can* pass the ``http_client`` argument to the constructors
    as with the base :class:`~akismet.SyncClient`, this class will ignore that argument
    and instead always uses its own custom HTTP client to produce the desired fixed
    responses.

    For operations other than comment-check and verify-key, the response values will be:

    * submit-ham and submit-spam: :data:`True`

    * key-sites: the sample responses (depending on requested format) given in `the
      Akismet web service documentation for key-sites
      <https://akismet.com/developers/detailed-docs/key-sites-activity/>`_.

    * usage-limit: the sample response given in `the Akismet web service documentation
      for usage-limit <https://akismet.com/developers/detailed-docs/usage-limit/>`_.

    """

    comment_check_response: akismet.CheckResponse = _common.CheckResponse.HAM
    verify_key_response: bool = True

    def __init__(
        self,
        config: Optional[akismet.Config] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """
        Default constructor.

        This overrides the behavior of the parent class to set up a custom HTTP client
        which returns fixed test responses. As a result, any explicit HTTP client passed
        in will be ignored.

        """
        test_client = _make_test_sync_http_client(
            comment_check_response=self.comment_check_response,
            verify_key_response=self.verify_key_response,
        )
        super().__init__(config=config, http_client=test_client)
