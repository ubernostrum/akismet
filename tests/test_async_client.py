"""
Tests for the asynchronous Akismet API client.

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


def make_fixed_response_async_client(
    response_text: str = "true",
    status_code: HTTPStatus = HTTPStatus.OK,
    response_json: typing.Optional[dict] = None,
) -> httpx.AsyncClient:
    """
    Return an asynchronous HTTP client that produces a fixed repsonse, for use in
    testing.

    """
    return httpx.AsyncClient(
        transport=base.make_fixed_response_transport(
            response_text, status_code, response_json
        )
    )


def make_exception_async_client(
    exception_class: Exception, message: str = "Error!"
) -> httpx.AsyncClient:
    """
    Return an asynchronous HTTP client that raises the given exception/message.

    """
    return mock.AsyncMock(
        spec_set=httpx.AsyncClient,
        get=mock.AsyncMock(side_effect=exception_class(message)),
        post=mock.AsyncMock(side_effect=exception_class(message)),
    )


class ValidConfig(akismet.TestAsyncClient):
    """
    Test client with valid config.

    """

    verify_key_response = True


class InvalidConfig(akismet.TestAsyncClient):
    """
    Test client with invalid config.

    """

    verify_key_response = False


class AlwaysBlatantSpam(akismet.TestAsyncClient):
    """
    Test client which marks all content as "blatant" spam.

    """

    comment_check_response = akismet.CheckResponse.DISCARD


class AlwaysSpam(akismet.TestAsyncClient):
    """
    Test client which marks all content as spam.

    """

    comment_check_response = akismet.CheckResponse.SPAM


class NeverSpam(akismet.TestAsyncClient):
    """
    Test client which marks all content as not spam.

    """

    comment_check_response = akismet.CheckResponse.HAM


class AsyncAkismetConstructorTests(base.AsyncAkismetTests):
    """
    Test the constructors of the asynchronous Akismet API client.

    """

    async def test_construct_config_explicit(self):
        """
        Passing explicit config to the default constructor uses that config.

        """
        config = akismet.Config(key="other-invalid-test-key", url=self.config.url)
        async with ValidConfig(config=config) as client:
            assert client._config == config

    async def test_construct_config_alternate_constructor_explicit(self):
        """
        Passing explicit config to the alternate constructor uses that config.

        """
        config = akismet.Config(key="other-invalid-test-key", url=self.config.url)
        client = await ValidConfig.validated_client(config=config)
        assert client._config == config

    async def test_construct_config_from_env(self):
        """
        Instantiating via the default constructor, without passing explicit config,
        reads the config from the environment.

        """
        config = akismet.Config(key=self.api_key, url=self.site_url)
        async with ValidConfig() as client:
            assert client._config == config

    async def test_construct_alternate_constructor_config_from_env(self):
        """
        Instantiating via the alternate constructor, without passing explicit
        config, reads the config from the environment.

        """
        config = akismet.Config(key=self.api_key, url=self.site_url)
        client = await ValidConfig.validated_client()
        assert client._config == config

    async def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        await ValidConfig.validated_client()

    async def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            await InvalidConfig.validated_client()

    async def test_construct_config_valid_context_manager(self):
        """
        With a valid configuration, constructing a client as a context manager succeeds.

        """
        async with ValidConfig():
            pass

    async def test_construct_config_invalid_key_context_manager(self):
        """
        With an invalid API key, constructing a client as a context manager raises
        an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            async with InvalidConfig():
                pass

    async def test_construct_config_valid_explicit(self):
        """
        With an explicit valid configuration, constructing a client succeeds.

        """
        await ValidConfig.validated_client(config=self.config)

    async def test_construct_config_invalid_key_explicit(self):
        """
        With an explicit invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            await InvalidConfig.validated_client(config=self.config)

    async def test_construct_config_bad_url(self):
        """
        With an invalid URL, constructing a client raises a ConfigurationError.

        """
        try:
            os.environ[_common._URL_ENV_VAR] = "ftp://example.com"
            with self.assertRaises(akismet.ConfigurationError):
                await akismet.AsyncClient.validated_client()
        finally:
            os.environ[_common._URL_ENV_VAR] = self.site_url

    async def test_construct_config_missing_key(self):
        """
        Without an API key present, constructing a client raises a
        ConfigurationError.

        """
        try:
            if _common._KEY_ENV_VAR in os.environ:
                del os.environ[_common._KEY_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                await ValidConfig.validated_client()
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key

    async def test_construct_config_missing_url(self):
        """
        Without a registered site URL present, constructing a client raises a
        ConfigurationError.

        """
        try:
            if _common._URL_ENV_VAR in os.environ:
                del os.environ[_common._URL_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                await ValidConfig.validated_client()
        finally:
            os.environ[_common._URL_ENV_VAR] = self.site_url

    async def test_construct_config_missing_all(self):
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
                await ValidConfig.validated_client()
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    async def test_construct_default_client(self):
        """
        Constructing a client without an explicit HTTP client uses the default HTTP
        client.

        """
        client = akismet.AsyncClient()
        http_client = client._http_client
        assert "user-agent" in http_client.headers
        assert http_client.headers["user-agent"] == _common.USER_AGENT


class AsyncAkismetAPITests(base.AsyncAkismetTests):
    """
    Test the API behavior of the asynchronous Akismet API client.

    """

    async def test_unsupported_request_method(self):
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
                    await client._request(
                        bad_method,
                        _common._API_V11,
                        _common._COMMENT_CHECK,
                        {"api_key", client._config.key},
                    )

    async def test_verify_key_valid(self):
        """
        ``verify_key()`` returns True when the config is valid.

        """
        async with ValidConfig() as client:
            assert await client.verify_key()

    async def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        client = InvalidConfig()
        assert not await client.verify_key()

    async def test_verify_key_valid_explicit(self):
        """
        ``verify_key()`` returns True when the config is valid and explicitly passed
        in.

        """
        async with ValidConfig() as client:
            assert await client.verify_key(key=self.api_key, url=self.site_url)

    async def test_verify_key_invalid_explicit(self):
        """
        ``verify_key()`` returns False when the config is invalid and explicitly
        passed in.

        """
        client = InvalidConfig()
        assert not await client.verify_key(key=self.api_key, url=self.site_url)

    async def test_request_with_invalid_key(self):
        """
        The request methods other than ``verify_key()`` raise
        ``akismet.APIKeyError`` if called with an invalid API key/URL.

        """
        client = akismet.AsyncClient(
            http_client=make_fixed_response_async_client(response_text="invalid"),
        )
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.APIKeyError):
                    await getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.APIKeyError):
                    await getattr(client, method)()

    async def test_comment_check_spam(self):
        """
        ``comment_check()`` returns the SPAM value when Akismet declares the content
        to be spam.

        """
        async with AlwaysSpam() as client:
            assert (
                await client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.SPAM
            )

    async def test_comment_check_spam_discard(self):
        """
        ``comment_check()`` returns the DISCARD value when Akismet declares the content
        to be spam and sends the "discard"" header value.

        """
        async with AlwaysBlatantSpam() as client:
            assert (
                await client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.DISCARD
            )

    async def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        async with NeverSpam() as client:
            assert (
                await client.comment_check(comment_content="test", **self.common_kwargs)
                == akismet.CheckResponse.HAM
            )

    async def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        async with ValidConfig() as client:
            assert await client.submit_ham(**self.common_kwargs)

    async def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        async with ValidConfig() as client:
            assert await client.submit_spam(**self.common_kwargs)

    async def test_key_sites_json(self):
        """
        ``key_sites()`` returns key usage information in JSON format by default.

        """
        async with ValidConfig() as client:
            response_json = await client.key_sites()
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

    async def test_key_sites_csv(self):
        """
        ``key_sites()`` returns key usage information in CSV format when requested.

        """
        async with ValidConfig() as client:
            first, *rest = (await client.key_sites(result_format="csv")).splitlines()
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

    async def test_usage_limit(self):
        """
        ``usage_limit()`` returns the API usage statistics in JSON format.

        """
        async with ValidConfig() as client:
            response_json = await client.usage_limit()
        assert set(response_json.keys()) == {
            "limit",
            "usage",
            "percentage",
            "throttled",
        }


class AsyncAkismetErrorTests(base.AsyncAkismetTests):
    """
    Test the error behavior of the asynchronous Akismet API client.

    """

    async def test_error_status(self):
        """
        RequestError is raised when a POST request to Akismet responds with an HTTP
        status code indicating an error.

        """
        codes = [code for code in HTTPStatus if 400 <= code <= 599]
        for code in codes:
            client = akismet.AsyncClient(
                http_client=make_fixed_response_async_client(status_code=code),
            )
            with self.subTest(method="verify_key"):
                with self.assertRaises(akismet.RequestError):
                    await client.verify_key()
            for method in ("comment_check", "submit_ham", "submit_spam"):
                with self.subTest(method=method):
                    with self.assertRaises(akismet.RequestError):
                        await getattr(client, method)(**self.common_kwargs)
            for method in ("key_sites", "usage_limit"):
                with self.subTest(method=method):
                    with self.assertRaises(akismet.RequestError):
                        await getattr(client, method)()

    async def test_error_timeout(self):
        """
        RequestError is raised when the request to Akismet times out.

        """

        client = akismet.AsyncClient(
            http_client=make_exception_async_client(
                httpx.TimeoutException, "Timed out."
            ),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                await client.verify_key()
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)()

    async def test_error_other_httpx(self):
        """
        RequestError is raised when a generic ``httpx`` request error occurs.

        """
        client = akismet.AsyncClient(
            http_client=make_exception_async_client(httpx.RequestError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                await client.verify_key()
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)()

    async def test_error_other(self):
        """
        RequestError is raised when any other (non-``httpx``) exception occurs during
        the request.

        """
        client = akismet.AsyncClient(
            http_client=make_exception_async_client(TypeError),
        )
        with self.subTest(method="verify_key"):
            with self.assertRaises(akismet.RequestError):
                await client.verify_key()
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)(**self.common_kwargs)
        for method in ("key_sites", "usage_limit"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.RequestError):
                    await getattr(client, method)()

    async def test_unknown_argument(self):
        """
        UnknownArgumentError is raised when an argument outside the supported set is
        passed to one of the POST request methods.

        """
        client = akismet.AsyncClient(
            http_client=_test_clients._make_test_async_http_client()
        )
        for method in ("comment_check", "submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.UnknownArgumentError):
                    await getattr(client, method)(bad_argument=1, **self.common_kwargs)

    async def test_protocol_error_comment_check(self):
        """
        ProtocolError is raised when ``comment_check()`` receives an unexpected
        response.

        """
        client = akismet.AsyncClient(
            http_client=make_fixed_response_async_client(response_text="bad"),
        )
        with self.assertRaises(akismet.ProtocolError):
            await client.comment_check(**self.common_kwargs)

    async def test_protocol_error_submit_ham_spam(self):
        """
        ProtocolError is raised when ``submit_ham()`` or ``submit_spam()`` receive an
        unexpected response.

        """
        client = akismet.AsyncClient(
            http_client=make_fixed_response_async_client(response_text="bad"),
        )
        for method in ("submit_ham", "submit_spam"):
            with self.subTest(method=method):
                with self.assertRaises(akismet.ProtocolError):
                    await getattr(client, method)(**self.common_kwargs)

    async def test_protocol_error_verify_key(self):
        """
        ProtocolError is raised when ``verify_key()`` receives an unexpected response.

        """

        client = akismet.AsyncClient(
            http_client=make_fixed_response_async_client(response_text="bad"),
        )
        with self.assertRaises(akismet.ProtocolError):
            await client.verify_key()
