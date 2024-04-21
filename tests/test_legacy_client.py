"""
Tests for the deprectaed legacy Akismet API client.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os

import akismet
from akismet import _common, _test_clients

from . import base
from .test_sync_client import make_fixed_response_sync_client


class LegacyAkismetConfigurationTests(base.AkismetTests):
    """
    Tests configuration of the legacy Akismet API class.

    """

    base_kwargs = {
        "user_ip": "127.0.0.1",
        "user_agent": "Mozilla",
    }

    def test_config_from_args(self):
        """
        Configuring via explicit arguments succeeds.

        """
        api = akismet.Akismet(
            key=self.api_key,
            blog_url=self.site_url,
            http_client=_test_clients._make_test_sync_http_client(),
        )
        self.assertEqual(self.api_key, api.api_key)
        self.assertEqual(self.site_url, api.blog_url)

    def test_bad_config_args(self):
        """
        Configuring with bad arguments fails.

        """
        with self.assertRaises(akismet.APIKeyError):
            akismet.Akismet(
                key="invalid",
                blog_url="http://invalid",
                http_client=_test_clients._make_test_sync_http_client(
                    verify_key_response=False
                ),
            )

    def test_config_from_env(self):
        """
        Configuring via environment variables succeeds.

        """
        api = akismet.Akismet(
            key=None,
            blog_url=None,
            http_client=_test_clients._make_test_sync_http_client(),
        )
        self.assertEqual(self.api_key, api.api_key)
        self.assertEqual(self.site_url, api.blog_url)

        api = akismet.Akismet(http_client=_test_clients._make_test_sync_http_client())
        self.assertEqual(self.api_key, api.api_key)
        self.assertEqual(self.site_url, api.blog_url)

    def test_bad_config_env(self):
        """
        Configuring with bad environment variables fails.

        """
        try:
            os.environ[_common._KEY_ENV_VAR] = "invalid"
            os.environ[_common._URL_ENV_VAR] = "http://invalid"
            with self.assertRaises(akismet.APIKeyError):
                akismet.Akismet(
                    http_client=_test_clients._make_test_sync_http_client(
                        verify_key_response=False
                    )
                )
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_bad_config_missing_key(self):
        """
        Configuring with missing key fails.

        """
        try:
            del os.environ[_common._KEY_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                akismet.Akismet(
                    http_client=_test_clients._make_test_sync_http_client(
                        verify_key_response=False
                    )
                )
        finally:
            os.environ[_common._KEY_ENV_VAR] = self.api_key
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_bad_config_missing_url(self):
        """
        Configuring with missing URL fails.

        """
        try:
            del os.environ[_common._URL_ENV_VAR]
            with self.assertRaises(akismet.ConfigurationError):
                akismet.Akismet(
                    http_client=_test_clients._make_test_sync_http_client(
                        verify_key_response=False
                    )
                )
        finally:
            os.environ[_common._URL_ENV_VAR] = self.site_url

    def test_bad_url(self):
        """
        Configuring with a bad URL fails.

        """
        bad_urls = (
            "example.com",
            "ftp://example.com",
            "www.example.com",
            "http//example.com",
            "https//example.com",
        )
        for url in bad_urls:
            with self.assertRaises(akismet.ConfigurationError):
                akismet.Akismet(
                    key=self.api_key,
                    blog_url=url,
                    http_client=_test_clients._make_test_sync_http_client(
                        verify_key_response=False
                    ),
                )

    def test_missing_config(self):
        """
        Instantiating without any configuration fails.

        """
        with self.assertRaises(akismet.ConfigurationError):
            akismet.Akismet(
                key=None,
                blog_url=None,
                http_client=_test_clients._make_test_sync_http_client(
                    verify_key_response=False
                ),
            )
        with self.assertRaises(akismet.ConfigurationError):
            akismet.Akismet(
                http_client=_test_clients._make_test_sync_http_client(
                    verify_key_response=False
                )
            )

    def test_user_agent(self):
        """
        The Akismet class creates the correct user-agent string.

        """
        api = akismet.Akismet(
            key=self.api_key,
            blog_url=self.site_url,
            http_client=_test_clients._make_test_sync_http_client(),
        )
        self.assertEqual(api.user_agent_header["User-Agent"], _common.USER_AGENT)


class LegacyAkismetAPITests(base.AkismetTests):
    """
    Tests implementation of the legacy Akismet API.

    """

    base_kwargs = {
        "user_ip": "127.0.0.1",
        "user_agent": "Mozilla",
    }

    def test_verify_key_valid(self):
        """
        The verify_key operation succeeds with a valid key and URL.

        """
        self.assertTrue(
            akismet.Akismet.verify_key(
                self.api_key,
                self.site_url,
                http_client=_test_clients._make_test_sync_http_client(),
            )
        )

    def test_verify_key_invalid(self):
        """
        The verify_key operation fails with an invalid key and URL.

        """
        self.assertFalse(
            akismet.Akismet.verify_key(
                "invalid",
                "http://invalid",
                http_client=_test_clients._make_test_sync_http_client(
                    verify_key_response=False
                ),
            )
        )

    def test_comment_check_spam(self):
        """
        The comment_check method correctly identifies spam.

        """
        check_kwargs = {
            # Akismet guarantees this will be classified spam.
            "comment_author": "viagra-test-123",
            **self.base_kwargs,
        }
        api = akismet.Akismet(http_client=_test_clients._make_test_sync_http_client())
        self.assertTrue(api.comment_check(**check_kwargs))

    def test_comment_check_not_spam(self):
        """
        The comment_check method correctly identifies non-spam.

        """
        check_kwargs = {
            # Akismet guarantees this will not be classified spam.
            "user_role": "administrator",
            **self.base_kwargs,
        }
        api = akismet.Akismet(
            http_client=_test_clients._make_test_sync_http_client(
                comment_check_response=_common.CheckResponse.HAM
            )
        )
        self.assertFalse(api.comment_check(**check_kwargs))

    def test_submit_spam(self):
        """
        The submit_spam method succeeds.

        """
        spam_kwargs = {
            "comment_type": "comment",
            "comment_author": "viagra-test-123",
            "comment_content": "viagra-test-123",
            **self.base_kwargs,
        }
        api = akismet.Akismet(http_client=_test_clients._make_test_sync_http_client())
        self.assertTrue(api.submit_spam(**spam_kwargs))

    def test_submit_ham(self):
        """
        The submit_ham method succeeds.

        """
        ham_kwargs = {
            "comment_type": "comment",
            "comment_author": "Legitimate Author",
            "comment_content": "This is a legitimate comment.",
            "user_role": "administrator",
            **self.base_kwargs,
        }
        api = akismet.Akismet(http_client=_test_clients._make_test_sync_http_client())
        self.assertTrue(api.submit_ham(**ham_kwargs))

    def test_unexpected_verify_key_response(self):
        """
        Unexpected verify_key API responses are correctly handled.

        """

        api = akismet.Akismet(
            http_client=_test_clients._make_test_sync_http_client(),
        )
        with self.assertRaises(akismet.ProtocolError):
            api.verify_key(
                self.api_key,
                self.site_url,
                http_client=make_fixed_response_sync_client(response_text="bad"),
            )

    def test_unexpected_comment_check_response(self):
        """
        Unexpected comment_check API responses are correctly handled.

        """
        api = akismet.Akismet(
            http_client=make_fixed_response_sync_client(response_text="valid"),
        )
        with self.assertRaises(akismet.ProtocolError):
            check_kwargs = {"comment_author": "viagra-test-123", **self.base_kwargs}
            api.comment_check(**check_kwargs)

    def test_unexpected_submit_spam_response(self):
        """
        Unexpected submit_spam API responses are correctly handled.

        """
        api = akismet.Akismet(
            http_client=make_fixed_response_sync_client(response_text="valid"),
        )
        with self.assertRaises(akismet.ProtocolError):
            spam_kwargs = {
                "comment_type": "comment",
                "comment_author": "viagra-test-123",
                "comment_content": "viagra-test-123",
                **self.base_kwargs,
            }
            api.submit_spam(**spam_kwargs)

    def test_unexpected_submit_ham_response(self):
        """
        Unexpected submit_ham API responses are correctly handled.

        """
        api = akismet.Akismet(
            http_client=make_fixed_response_sync_client(response_text="valid"),
        )
        with self.assertRaises(akismet.ProtocolError):
            ham_kwargs = {
                "comment_type": "comment",
                "comment_author": "Legitimate Author",
                "comment_content": "This is a legitimate comment.",
                "user_role": "administrator",
                **self.base_kwargs,
            }
            api.submit_ham(**ham_kwargs)

    def test_unknown_kwargs(self):
        """
        Unknown Akismet arguments are correctly rejected.

        """
        bad_kwargs = {"bad_arg": "bad_val", **self.base_kwargs}
        api = akismet.Akismet(
            http_client=_test_clients._make_test_sync_http_client(),
        )
        with self.assertRaises(akismet.UnknownArgumentError):
            api.comment_check(**bad_kwargs)
