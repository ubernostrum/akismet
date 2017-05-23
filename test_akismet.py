import os
import unittest

import akismet


API_KEY_FROM_ENV = os.getenv('TEST_AKISMET_API_KEY')
URL_FROM_ENV = os.getenv('TEST_AKISMET_BLOG_URL')


class AkismetConfigurationTests(unittest.TestCase):
    def setUp(self):
        os.environ[akismet.Akismet.API_KEY_ENV_VAR] = API_KEY_FROM_ENV
        os.environ[akismet.Akismet.BLOG_URL_ENV_VAR] = URL_FROM_ENV

    def tearDown(self):
        os.unsetenv(akismet.Akisment.API_KEY_ENV_VAR)
        os.unsetenv(akismet.Akismet.API_KEY_ENV_VAR)

    def test_nothing(self):
        pass
