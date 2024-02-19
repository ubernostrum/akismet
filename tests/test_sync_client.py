"""
Tests for the synchronous Akismet API client.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os
import textwrap
from http import HTTPStatus

import httpx

import akismet
from akismet import _common

from .base import AkismetTests


class SyncAkismetConstructorTests(AkismetTests):
    """
    Test the ``client()`` constructor of the synchronous Akismet API client.

    """

    def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        akismet.SyncClient.validated_client(
            http_client=self.custom_response_sync_client()
        )

    def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            akismet.SyncClient.validated_client(
                http_client=self.custom_response_sync_client(config_valid=False)
            )

    def test_construct_config_bad_url(self):
        """
        With an invalid URL, constructing a client raises a ConfigurationError.

        """
        try:
            os.environ[_common._URL_ENV_VAR] = "ftp://example.com"
            with self.assertRaises(akismet.ConfigurationError):
                akismet.SyncClient.validated_client()
        finally:
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_construct_config_missing_key(self):
        """
        Without an API key present, constructing a client raises a
        ConfigurationError.

        """
        try:
            if _common._KEY_ENV_VAR in os.environ:
                del os.environ[_common._KEY_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                akismet.SyncClient.validated_client(
                    http_client=self.custom_response_sync_client()
                )
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key

    def test_construct_config_missing_url(self):
        """
        Without a registered site URL present, constructing a client raises a
        ConfigurationError.

        """
        try:
            if _common._URL_ENV_VAR in os.environ:
                del os.environ[_common._URL_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                akismet.SyncClient.validated_client(
                    http_client=self.custom_response_sync_client()
                )
        finally:
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_construct_config_missing_all(self):
        """
        Without any config present, constructing a client raises a
        ConfigurationError.

        """
        try:
            if _common._KEY_ENV_VAR in os.environ:
                del os.environ[_common._KEY_ENV_VAR]
            if _common._URL_ENV_VAR in os.environ:
                del os.environ[_common._URL_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                akismet.SyncClient.validated_client(
                    http_client=self.custom_response_sync_client()
                )
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_construct_default_client(self):
        """
        Constructing a client without an explicit HTTP client uses the default HTTP
        client.

        """
        client = akismet.SyncClient(config=self.config)
        http_client = client._http_client
        assert "user-agent" in http_client.headers
        assert http_client.headers["user-agent"] == _common.USER_AGENT


class SyncAkismetAPITests(AkismetTests):
    """
    Test the API behavior of the synchronous Akismet API client.

    """

    def test_unsupported_request_method(self):
        """
        Attempting to make a request with an unsupported method raises
        ``AkismetError``.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(),
        )
        # The tested set of methods here are all the methods that are in Python 3.11's
        # http.HTTPMethod enum but not supported for Akismet requests.
        for bad_method in (
            "CONNECT",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "PATCH",
            "PUT",
            "TRACE",
        ):
            with self.subTest(method=bad_method):
                with self.assertRaises(akismet.AkismetError):
                    client._request(
                        bad_method,
                        _common._API_V11,
                        _common._COMMENT_CHECK,
                        {"api_key", client._config.key},
                    )

    def test_verify_key_valid(self):
        """
        ``verify_key()`` returns True when the config is valid.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(),
        )
        assert client.verify_key(key=self.api_key, url=self.site_url)

    def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(config_valid=False),
        )
        assert not client.verify_key(key=self.api_key, url=self.site_url)

    def test_request_with_invalid_key(self):
        """
        The request methods other than ``verify_key()`` raise
        ``akismet.APIKeyError`` if called with an invalid API key/URL.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text="invalid"),
        )
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.APIKeyError):
                    getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.APIKeyError):
                    getattr(client, method)()

    def test_comment_check_spam(self):
        """
        ``comment_check()`` returns the SPAM value when Akismet declares the content
        to be spam.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text="true"),
        )
        assert (
            client.comment_check(comment_content="test", **self.common_kwargs)
            == akismet.CheckResponse.SPAM
        )

    def test_comment_check_spam_discard(self):
        """
        ``comment_check()`` returns the DISCARD value when Akismet declares the content
        to be spam and sends the "discard"" header value.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(
                response_text="true", headers={"X-akismet-pro-tip": "discard"}
            ),
        )
        assert (
            client.comment_check(comment_content="test", **self.common_kwargs)
            == akismet.CheckResponse.DISCARD
        )

    def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text="false"),
        )
        assert (
            client.comment_check(comment_content="test", **self.common_kwargs)
            == akismet.CheckResponse.HAM
        )

    def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(
                response_text=_common._SUBMISSION_RESPONSE
            ),
        )
        assert client.submit_ham(**self.common_kwargs)

    def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(
                response_text=_common._SUBMISSION_RESPONSE
            ),
        )
        assert client.submit_spam(**self.common_kwargs)

    def test_key_sites_json(self):
        """
        ``key_sites()`` returns key usage information in JSON format by default.

        """
        # Sample response data taken from Akismet's dev docs.
        response_json = {
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
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_json=response_json),
        )
        assert client.key_sites() == response_json

    def test_key_sites_csv(self):
        """
        ``key_sites()`` returns key usage information in CSV format when requested.

        """
        # Sample response data taken from Akismet's dev docs.
        response_csv = textwrap.dedent(
            """
        Active sites for 123YourAPIKey during 2022-09 (limit:10, offset: 0, total: 4)
        Site,Total API Calls,Spam,Ham,Missed Spam,False Positives,Is Revoked
        site6735.example.com,14446,33,13,0,9,false
        site3026.example.com,8677,101,6,0,0,false
        site3737.example.com,4230,65,5,2,0,true
        site5653.example.com,2921,30,1,2,6,false
        """
        )
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text=response_csv),
        )
        assert client.key_sites(result_format="csv") == response_csv

    def test_usage_limit(self):
        """
        ``usage_limit()`` returns the API usage statistics in JSON format.

        """
        # Sample response data taken from Akismet's dev docs.
        response_json = {
            "limit": 350000,
            "usage": 7463,
            "percentage": "2.13",
            "throttled": False,
        }
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_json=response_json),
        )
        assert client.usage_limit() == response_json


class SyncAkismetErrorTests(AkismetTests):
    """
    Test the error behavior of the synchronous Akismet API client.

    """

    def test_error_status(self):
        """
        RequestError is raised when a POST request to Akismet responds with an HTTP
        status code indicating an error.

        """
        codes = [code for code in HTTPStatus if 400 <= code <= 599]
        for code in codes:
            client = akismet.SyncClient(
                config=self.config,
                http_client=self.custom_response_sync_client(status_code=code),
            )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key(self.config.key, self.config.url)
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)()

    def test_error_timeout(self):
        """
        RequestError is raised when the request to Akismet times out.

        """

        client = akismet.SyncClient(
            config=self.config,
            http_client=self.exception_sync_client(
                httpx.TimeoutException, "Timed out."
            ),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key(self.config.key, self.config.url)
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)()

    def test_error_other_httpx(self):
        """
        RequestError is raised when a generic ``httpx`` request error occurs.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.exception_sync_client(httpx.RequestError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key(self.config.key, self.config.url)
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)()

    def test_error_other(self):
        """
        RequestError is raised when any other (non-``httpx``) exception occurs during
        the request.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.exception_sync_client(TypeError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key(self.config.key, self.config.url)
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    getattr(client, method)()

    def test_unknown_argument(self):
        """
        UnknownArgumentError is raised when an argument outside the supported set is
        passed to one of the POST request methods.

        """
        client = akismet.SyncClient(
            config=self.config, http_client=self.custom_response_sync_client()
        )
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.UnknownArgumentError):
                    getattr(client, method)(bad_argument=1, **self.common_kwargs)

    def test_protocol_error_comment_check(self):
        """
        ProtocolError is raised when ``comment_check()`` receives an unexpected
        response.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text="bad"),
        )
        with self.assertRaises(akismet.ProtocolError):
            client.comment_check(**self.common_kwargs)

    def test_protocol_error_submit_ham_spam(self):
        """
        ProtocolError is raised when ``submit_ham()`` or ``submit_spam()`` receive an
        unexpected response.

        """
        client = akismet.SyncClient(
            config=self.config,
            http_client=self.custom_response_sync_client(response_text="bad"),
        )
        for method in ("submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.ProtocolError):
                    getattr(client, method)(**self.common_kwargs)

    def test_protocol_error_verify_key(self):
        """
        ProtocolError is raised when ``verify_key()`` receives an unexpected response.

        """

        def _handler(  # pylint: disable=unused-argument
            request: httpx.Request,
        ) -> httpx.Response:
            """
            Mock transport handler which returns a controlled response.

            """
            return httpx.Response(status_code=HTTPStatus.OK, content="bad")

        client = akismet.SyncClient(
            config=self.config,
            http_client=httpx.Client(transport=httpx.MockTransport(_handler)),
        )
        with self.assertRaises(akismet.ProtocolError):
            client.verify_key(self.config.key, self.config.url)
