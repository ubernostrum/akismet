"""
Tests for the synchronous Akismet API client.

"""

# SPDX-License-Identifier: BSD-3-Clause

import csv
import os
import typing
from http import HTTPStatus
from unittest import mock

import httpx

import akismet
from akismet import _common, _test_clients

from . import base


def make_fixed_response_sync_client(
    response_text: str = "true",
    status_code: HTTPStatus = HTTPStatus.OK,
    response_json: typing.Optional[dict] = None,
) -> httpx.Client:
    """
    Return a synchronous HTTP client that produces a fixed repsonse, for use in
    testing.

    """
    return httpx.Client(
        transport=base.make_fixed_response_transport(
            response_text, status_code, response_json
        )
    )


def make_exception_sync_client(
    exception_class: Exception, message: str = "Error!"
) -> httpx.Client:
    """
    Return a synchronous HTTP client that raises the given exception/message.

    """
    return mock.Mock(
        spec_set=httpx.Client,
        get=mock.Mock(side_effect=exception_class(message)),
        post=mock.Mock(side_effect=exception_class(message)),
    )


class ValidConfig(akismet.TestSyncClient):
    """
    Test client with valid config.

    """

    verify_key_response = True


class InvalidConfig(akismet.TestSyncClient):
    """
    Test client with invalid config.

    """

    verify_key_response = False


class AlwaysBlatantSpam(akismet.TestSyncClient):
    """
    Test client which marks all content as "blatant" spam.

    """

    comment_check_response = akismet.CheckResponse.DISCARD


class AlwaysSpam(akismet.TestSyncClient):
    """
    Test client which marks all content as spam.

    """

    comment_check_response = akismet.CheckResponse.SPAM


class NeverSpam(akismet.TestSyncClient):
    """
    Test client which marks all content as not spam.

    """

    comment_check_response = akismet.CheckResponse.HAM


class SyncAkismetConstructorTests(base.AkismetTests):
    """
    Test the constructors of the synchronous Akismet API client.

    """

    def test_construct_config_explicit(self):
        """
        Passing explicit config to the default constructor uses that config.

        """
        config = akismet.Config(key="other-invalid-test-key", url=self.config.url)
        with ValidConfig(config=config) as client:
            assert client._config == config

    def test_construct_config_alternate_constructor_explicit(self):
        """
        Passing explicit config to the alternate constructor uses that config.

        """
        config = akismet.Config(key="other-invalid-test-key", url=self.config.url)
        client = ValidConfig.validated_client(config=config)
        assert client._config == config

    def test_construct_config_from_env(self):
        """
        Instantiating via the default constructor, without passing explicit config,
        reads the config from the environment.

        """
        config = akismet.Config(key=self.api_key, url=self.site_url)
        with ValidConfig() as client:
            assert client._config == config

    def test_construct_alternate_constructor_config_from_env(self):
        """
        Instantiating via the alternate constructor, without passing explicit
        config, reads the config from the environment.

        """
        config = akismet.Config(key=self.api_key, url=self.site_url)
        client = ValidConfig.validated_client()
        assert client._config == config

    def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        ValidConfig.validated_client()

    def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            InvalidConfig.validated_client()

    def test_construct_config_valid_context_manager(self):
        """
        With a valid configuration, constructing a client as a context manager succeeds.

        """
        with ValidConfig():
            pass

    def test_construct_config_invalid_key_context_manager(self):
        """
        With an invalid API key, constructing a client as a context manager raises
        an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            with InvalidConfig():
                pass

    def test_construct_config_valid_explicit(self):
        """
        With an explicit valid configuration, constructing a client succeeds.

        """
        ValidConfig.validated_client(config=self.config)

    def test_construct_config_invalid_key_explicit(self):
        """
        With an explicit invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            InvalidConfig.validated_client(config=self.config)

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
                ValidConfig.validated_client()
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
                ValidConfig.validated_client()
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
                ValidConfig.validated_client()
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_construct_default_client(self):
        """
        Constructing a client without an explicit HTTP client uses the default HTTP
        client.

        """
        client = akismet.SyncClient()
        http_client = client._http_client
        assert "user-agent" in http_client.headers
        assert http_client.headers["user-agent"] == _common.USER_AGENT


class SyncAkismetAPITests(base.AkismetTests):
    """
    Test the API behavior of the synchronous Akismet API client.

    """

    def test_unsupported_request_method(self):
        """
        Attempting to make a request with an unsupported method raises
        ``AkismetError``.

        """
        client = ValidConfig()
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
        with ValidConfig() as client:
            assert client.verify_key()

    def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        client = InvalidConfig()
        assert not client.verify_key()

    def test_verify_key_valid_explicit(self):
        """
        ``verify_key()`` returns True when the config is valid and explicitly passed
        in.

        """
        with ValidConfig() as client:
            assert client.verify_key(key=self.api_key, url=self.site_url)

    def test_verify_key_invalid_explicit(self):
        """
        ``verify_key()`` returns False when the config is invalid and explicitly
        passed in.

        """
        client = InvalidConfig()
        assert not client.verify_key(key=self.api_key, url=self.site_url)

    def test_request_with_invalid_key(self):
        """
        The request methods other than ``verify_key()`` raise
        ``akismet.APIKeyError`` if called with an invalid API key/URL.

        """
        client = akismet.SyncClient(
            http_client=make_fixed_response_sync_client(response_text="invalid"),
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
        with AlwaysSpam() as client:
            assert (
                client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.SPAM
            )

    def test_comment_check_spam_discard(self):
        """
        ``comment_check()`` returns the DISCARD value when Akismet declares the content
        to be spam and sends the "discard"" header value.

        """
        with AlwaysBlatantSpam() as client:
            assert (
                client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.DISCARD
            )

    def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        with NeverSpam() as client:
            assert (
                client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.HAM
            )

    def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        with ValidConfig() as client:
            assert client.submit_ham(**self.common_kwargs)

    def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        with ValidConfig() as client:
            assert client.submit_spam(**self.common_kwargs)

    def test_key_sites_json(self):
        """
        ``key_sites()`` returns key usage information in JSON format by default.

        """
        with ValidConfig() as client:
            response_json = client.key_sites()
        for key in ["2022-09", "limit", "offset", "total"]:
            assert key in response_json
        sites = response_json["2022-09"]
        for site in sites:
            for key in [
                "site",
                "api_calls",
                "spam",
                "ham",
                "missed_spam",
                "false_positives",
                "is_revoked",
            ]:
                assert key in site

    def test_key_sites_csv(self):
        """
        ``key_sites()`` returns key usage information in CSV format when requested.

        """
        with ValidConfig() as client:
            first, *rest = (client.key_sites(result_format="csv")).splitlines()
        assert first.startswith("Active sites for")
        reader = csv.DictReader(rest)
        row = next(reader)
        assert set(row.keys()) == {
            "Site",
            "Total API Calls",
            "Spam",
            "Ham",
            "Missed Spam",
            "False Positives",
            "Is Revoked",
        }

    def test_usage_limit(self):
        """
        ``usage_limit()`` returns the API usage statistics in JSON format.

        """
        with ValidConfig() as client:
            response_json = client.usage_limit()
        assert set(response_json.keys()) == {
            "limit",
            "usage",
            "percentage",
            "throttled",
        }


class SyncAkismetErrorTests(base.AkismetTests):
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
                http_client=make_fixed_response_sync_client(status_code=code),
            )
            with self.subTest(method="verify_key"):
                with self.assertRaises(akismet.RequestError):
                    client.verify_key()
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
            http_client=make_exception_sync_client(
                httpx.TimeoutException, "Timed out."
            ),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key()
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
            http_client=make_exception_sync_client(httpx.RequestError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key()
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
            http_client=make_exception_sync_client(TypeError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                client.verify_key()
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
            http_client=_test_clients._make_test_async_http_client()
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
            http_client=make_fixed_response_sync_client(response_text="bad"),
        )
        with self.assertRaises(akismet.ProtocolError):
            client.comment_check(**self.common_kwargs)

    def test_protocol_error_submit_ham_spam(self):
        """
        ProtocolError is raised when ``submit_ham()`` or ``submit_spam()`` receive an
        unexpected response.

        """
        client = akismet.SyncClient(
            http_client=make_fixed_response_sync_client(response_text="bad"),
        )
        for method in ("submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.ProtocolError):
                    getattr(client, method)(**self.common_kwargs)

    def test_protocol_error_verify_key(self):
        """
        ProtocolError is raised when ``verify_key()`` receives an unexpected response.

        """

        client = akismet.SyncClient(
            http_client=make_fixed_response_sync_client(response_text="bad"),
        )
        with self.assertRaises(akismet.ProtocolError):
            client.verify_key()
