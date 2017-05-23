import os
import unittest

import akismet


class AkismetConfigurationTests(unittest.TestCase):
    def setUp(self):
        os.environ[akismet.Akismet.API_KEY_ENV_VAR] = os.getenv('TEST_AKISMET_API_KEY')
        os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = os.getenv('TEST_AKISMET_BLOG_URL')

    def tearDown(self):
        os.unsetenv(akismet.Akismet.API_KEY_ENV_VAR)
        os.unsetenv(akismet.Akismet.API_KEY_ENV_VAR)

    def test_nothing(self):
        pass
