"""
End-to-end tests of the Akismet API clients, which will make real requests to the
Akismet web service.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os

import akismet
from akismet import _common

from .base import AkismetTests, AsyncAkismetTests

BAD_KEY = "INVALID_TEST_KEY"
BAD_URL = "http://example.com"

# The Akismet web API guarantees that these values will trigger certain types of
# responses.
HAM_ROLE = "administrator"
SPAM_AUTHOR = "akismet-guaranteed-spam"


class SyncAkismetEndToEndTests(AkismetTests):
    """
    End-to-end tests of the synchronous Akismet API client.

    """

    common_kwargs = {"user_ip": "127.0.0.1", "is_test": 1}

    def setUp(self):
        """
        Create a default client instance for use in testing.

        """
        self.client = akismet.SyncClient.validated_client()

    def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        akismet.SyncClient.validated_client()

    def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """

        try:
            os.environ[_common._KEY_ENV_VAR] = BAD_KEY
            os.environ[_common._URL_ENV_VAR] = BAD_URL
            with self.assertRaises(akismet.APIKeyError):
                akismet.SyncClient.validated_client()
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_verify_key_valid(self):
        """
        ``verify_key()`` returns True when the config is valid.

        """
        assert self.client.verify_key(self.api_key, self.site_url)

    def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        assert not self.client.verify_key(BAD_KEY, BAD_URL)

    def test_request_with_invalid_key(self):
        """
        The request methods other than ``verify_key()`` raise
        ``akismet.APIKeyError`` if called with an invalid API key/URL.

        """
        client = akismet.SyncClient(
            config=self.config,
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
        assert (
            self.client.comment_check(
                comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
            )
            == akismet.CheckResponse.SPAM
        )

    def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        assert (
            self.client.comment_check(
                comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
            )
            == akismet.CheckResponse.HAM
        )

    def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        assert self.client.submit_ham(
            comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
        )

    def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        assert self.client.submit_spam(
            comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
        )


class AsyncAkismetEndToEndTests(AsyncAkismetTests):
    """
    End-to-end tests of the asynchronous Akismet API client.

    """

    common_kwargs = {"user_ip": "127.0.0.1", "is_test": 1}

    async def asyncSetUp(self):
        """
        Create a default client instance for use in testing.

        """
        self.client = await akismet.AsyncClient.validated_client()

    async def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        await akismet.AsyncClient.validated_client()

    async def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """

        try:
            os.environ[_common._KEY_ENV_VAR] = BAD_KEY
            os.environ[_common._URL_ENV_VAR] = BAD_URL
            with self.assertRaises(akismet.APIKeyError):
                await akismet.AsyncClient.validated_client()
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    async def test_verify_key_valid(self):
        """
        ``verify_key()`` returns True when the config is valid.

        """
        assert await self.client.verify_key(self.api_key, self.site_url)

    async def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        assert not await self.client.verify_key(BAD_KEY, BAD_URL)

    async def test_request_with_invalid_key(self):
        """
        The HTTP POST request methods -- ``comment_check()``, ``submit_ham()``, and
        ``submit_spam()`` -- raise ``APIKeyError`` when called with an invalid API key
        and/or site URL.

        """
        client = akismet.AsyncClient(
            config=self.config,
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
        assert (
            await self.client.comment_check(
                comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
            )
            == akismet.CheckResponse.SPAM
        )

    async def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        assert (
            await self.client.comment_check(
                comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
            )
            == akismet.CheckResponse.HAM
        )

    async def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        assert await self.client.submit_ham(
            comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
        )

    async def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        assert await self.client.submit_spam(
            comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
        )


class LegacyAkismetEndToEndTests(AkismetTests):
    """
    End-to-end tests of the legacy/deprecated Akismet API client.

    """

    common_kwargs = {"user_ip": "127.0.0.1", "user_agent": "Mozilla", "is_test": 1}

    def setUp(self):
        """
        Create a default client instance for use in testing.

        """
        self.client = akismet.Akismet(key=self.api_key, blog_url=self.site_url)

    def test_construct_config_valid(self):
        """
        With a valid configuration, constructing a client succeeds.

        """
        akismet.Akismet(key=self.api_key, blog_url=self.site_url)

    def test_construct_config_invalid_key(self):
        """
        With an invalid API key, constructing a client raises an APIKeyError.

        """
        with self.assertRaises(akismet.APIKeyError):
            akismet.Akismet(key=BAD_KEY, blog_url=BAD_URL)

    def test_verify_key_valid(self):
        """
        ``verify_key()`` returns True when the config is valid.

        """
        assert self.client.verify_key(self.api_key, self.site_url)

    def test_verify_key_invalid(self):
        """
        ``verify_key()`` returns False when the config is invalid.

        """
        assert not self.client.verify_key(BAD_KEY, BAD_URL)

    def test_comment_check_spam(self):
        """
        ``comment_check()`` returns the SPAM value when Akismet declares the content
        to be spam.

        """
        assert self.client.comment_check(
            comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
        )

    def test_comment_check_ham(self):
        """
        ``comment_check()`` returns the HAM value when Akismet declares the content
        to be ham.

        """
        assert not self.client.comment_check(
            comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
        )

    def test_submit_ham(self):
        """
        ``submit_ham()`` returns True when Akismet accepts the submission.

        """
        assert self.client.submit_ham(
            comment_content="test", user_role=HAM_ROLE, **self.common_kwargs
        )

    def test_submit_spam(self):
        """
        ``submit_spam()`` returns True when Akismet accepts the submission.

        """
        assert self.client.submit_spam(
            comment_content="test", comment_author=SPAM_AUTHOR, **self.common_kwargs
        )
