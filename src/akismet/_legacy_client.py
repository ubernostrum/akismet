"""
Legacy/deprecated Akismet client.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os
import textwrap
import warnings
from typing import Optional

import httpx

from . import _common, _exceptions


class Akismet:
    """
    Legacy class-based Akismet client.

    This class is deprecated and will be removed in a future release. It receives no new
    features and only minimal security-oriented bugfixes. Please migrate as quickly as
    possible to one of the two supported client classes: akismet.SyncClient or
    akismet.AsyncClient.

    Two configuration parameters -- your Akismet API key and registered URL -- are
    required; they can be passed when instantiating, or set in the environment variables
    ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``.

    The following operations of the Akismet API are exposed here:

    * :meth:`verify_key`

    * :meth:`comment_check`

    * :meth:`submit_spam`

    * :meth:`submit_ham`

    For full details of the Akismet API, see the Akismet documentation:

    https://akismet.com/development/api/#detailed-docs

    The verify_key operation will be automatically called for you as this class is
    instantiated; :exc:`~akismet.ConfigurationError` will be raised if the configuration
    cannot be found or if the supplied key/URL are invalid.

    """

    COMMENT_CHECK_URL = "https://rest.akismet.com/1.1/comment-check"
    SUBMIT_HAM_URL = "https://rest.akismet.com/1.1/submit-ham"
    SUBMIT_SPAM_URL = "https://rest.akismet.com/1.1/submit-spam"
    VERIFY_KEY_URL = "https://rest.akismet.com/1.1/verify-key"

    SUBMIT_SUCCESS_RESPONSE = "Thanks for making the web a better place."

    OPTIONAL_KEYS = [
        "blog_charset",
        "blog_lang",
        "comment_author",
        "comment_author_email",
        "comment_author_url",
        "comment_content",
        "comment_date_gmt",
        "comment_post_modified_gmt",
        "comment_type",
        "is_test",
        "permalink",
        "recheck_reason",
        "referrer",
        "user_role",
    ]

    user_agent_header = {"User-Agent": _common.USER_AGENT}

    def __init__(
        self,
        key: Optional[str] = None,
        blog_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        warnings.warn(
            textwrap.dedent(
                """
            The akismet.Akismet API client is deprecated and will be removed in
            version 2.0. Please migrate to either akismet.SyncClient or
            akismet.AsyncClient.  """,
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        maybe_key = key if key is not None else os.getenv(_common._KEY_ENV_VAR, "")
        maybe_url = (
            blog_url if blog_url is not None else os.getenv(_common._URL_ENV_VAR, "")
        )
        if maybe_key == "" or maybe_url == "":
            raise _exceptions.ConfigurationError(
                textwrap.dedent(
                    f"""
                Could not find full Akismet configuration.

                Found API key: {maybe_key}
                Found blog URL: {maybe_url}
                """
                )
            )
        self.http_client = http_client or _common._get_sync_http_client()
        if not self.verify_key(maybe_key, maybe_url, http_client=self.http_client):
            raise _exceptions.APIKeyError(
                f"Akismet key ({maybe_key}, {maybe_url}) is invalid."
            )
        self.api_key = maybe_key
        self.blog_url = maybe_url

    def _api_request(
        self, endpoint: str, user_ip: str, user_agent: str, **kwargs: str
    ) -> httpx.Response:
        """
        Make a request to the Akismet API.

        This method is used for all API calls except key verification, since all
        endpoints other than key verification must interpolate the API key into the URL
        and supply certain basic data.

        """
        unknown_args = [k for k in kwargs if k not in self.OPTIONAL_KEYS]
        if unknown_args:
            raise _exceptions.UnknownArgumentError(
                "Unknown arguments while making request: {', '.join(unknown_args)}."
            )

        data = {
            "api_key": self.api_key,
            "blog": self.blog_url,
            "user_ip": user_ip,
            "user_agent": user_agent,
            **kwargs,
        }
        return self.http_client.post(endpoint, data=data)

    def _submission_request(  # pylint: disable=inconsistent-return-statements
        self, operation: str, user_ip: str, user_agent: str, **kwargs: str
    ) -> bool:
        """
        Submit spam or ham to the Akismet API.

        """
        endpoint = {
            "submit_spam": self.SUBMIT_SPAM_URL,
            "submit_ham": self.SUBMIT_HAM_URL,
        }[operation]
        response = self._api_request(endpoint, user_ip, user_agent, **kwargs)
        if response.text == self.SUBMIT_SUCCESS_RESPONSE:
            return True
        self._protocol_error(operation, response)

    @classmethod
    def _protocol_error(cls, operation: str, response: httpx.Response) -> None:
        """
        Raise an appropriate exception for unexpected API responses.

        """
        raise _exceptions.ProtocolError(
            textwrap.dedent(
                f"""
            Received unexpected or non-standard response from Akismet API.

            API operation was: {operation}
            API response received was: {response.text}
            Debug header value was: {response.headers.get('X-akismet-debug-help')}
            """
            )
        )

    @classmethod
    def verify_key(  # pylint: disable=inconsistent-return-statements
        cls, key: str, blog_url: str, http_client: Optional[httpx.Client] = None
    ) -> bool:
        """
        Verify an Akismet API key and URL.

        Returns :data:`True` if the key and URL are valid, :data:`False` otherwise.

        """
        if not blog_url.startswith(("http://", "https://")):
            raise _exceptions.ConfigurationError(
                textwrap.dedent(
                    f"""
                Invalid site URL specified: {blog_url}

                Akismet requires the full URL including the leading
                'http://' or 'https://'.
                """
                )
            )
        if http_client is None:  # pragma: no cover
            http_client = _common._get_sync_http_client()
        response = http_client.post(
            cls.VERIFY_KEY_URL,
            data={"key": key, "blog": blog_url},
        )
        if response.text == "valid":
            return True
        if response.text == "invalid":
            return False
        cls._protocol_error("verify_key", response)

    def comment_check(  # pylint: disable=inconsistent-return-statements
        self, user_ip: str, user_agent: str, **kwargs: str
    ) -> bool:
        """
        Check a comment to determine whether it is spam.

        The IP address and user-agent string of the remote user are required. All other
        arguments documented by Akismet (other than the PHP server information) are also
        optionally accepted.  See the Akismet API documentation for a full list:

        https://akismet.com/developers/comment-check/

        Like the Akismet web API, returns True for a comment that is spam, and False for
        a comment that is not spam.

        """
        response = self._api_request(
            self.COMMENT_CHECK_URL, user_ip, user_agent, **kwargs
        )
        if response.text == "true":
            return True
        if response.text == "false":
            return False
        self._protocol_error("comment_check", response)

    def submit_spam(self, user_ip: str, user_agent: str, **kwargs: str) -> bool:
        """
        Inform Akismet that a comment is spam.

        The IP address and user-agent string of the remote user are required. All other
        arguments documented by Akismet (other than the PHP server information) are also
        optionally accepted.  See the Akismet API documentation for a full list:

        https://akismet.com/developers/submit-spam-missed-spam/

        Returns True on success (the only expected response).

        """
        return self._submission_request("submit_spam", user_ip, user_agent, **kwargs)

    def submit_ham(self, user_ip: str, user_agent: str, **kwargs: str) -> bool:
        """
        Inform Akismet that a comment is not spam.

        The IP address and user-agent string of the remote user are required. All other
        arguments documented by Akismet (other than the PHP server information) are also
        optionally accepted.  See the Akismet API documentation for a full list:

        https://akismet.com/developers/submit-ham-false-positives/

        Returns True on success (the only expected response).

        """
        return self._submission_request("submit_ham", user_ip, user_agent, **kwargs)
