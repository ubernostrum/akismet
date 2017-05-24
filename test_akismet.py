import os
import unittest

import akismet


class AkismetConfigurationTests(unittest.TestCase):
    """
    Test configuration of the Akismet class.

    """
    api_key = os.getenv('TEST_AKISMET_API_KEY')
    blog_url = os.getenv('TEST_AKISMET_BLOG_URL')

    def test_config_from_args(self):
        """Configuring via explicit arguments succeeds."""
        api = akismet.Akismet(
            key=self.api_key,
            blog_url=self.blog_url
        )

    def test_bad_config_args(self):
        """Configuring with bad arguments fails."""
        with self.assertRaises(akismet.ConfigurationError):
            api = akismet.Akismet(
                key='invalid',
                blog_url='invalid'
            )

    def test_config_from_env(self):
        """Configuring via environment variables succeeds."""
        try:
            os.environ[akismet.Akismet.API_KEY_ENV_VAR] = self.api_key
            os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = self.blog_url
            api = akismet.Akismet(key=None, blog_url=None)
            api = akismet.Akismet()
        finally:
            os.environ[akismet.Akismet.API_KEY_ENV_VAR] = ''
            os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = ''

    def test_bad_config_env(self):
        """Configuring with bad environment variables fails."""
        try:
            os.environ[akismet.Akismet.API_KEY_ENV_VAR] = 'invalid'
            os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = 'invalid'
            with self.assertRaises(akismet.ConfigurationError):
                api = akismet.Akismet()
        finally:
            os.environ[akismet.Akismet.API_KEY_ENV_VAR] = ''
            os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = ''

    def test_missing_config(self):
        """Instantiating without any configuration fails."""
        with self.assertRaises(akismet.ConfigurationError):
            api = akismet.Akismet(key=None, blog_url=None)
        with self.assertRaises(akismet.ConfigurationError):
            api = akismet.Akismet()
