import datetime
import os
import sys
import unittest

import mock

import akismet


class AkismetTests(unittest.TestCase):
    api_key = os.getenv('TEST_AKISMET_API_KEY')
    blog_url = os.getenv('TEST_AKISMET_BLOG_URL')

    api_key_env_var = 'PYTHON_AKISMET_API_KEY'
    blog_url_env_var = 'PYTHON_AKISMET_BLOG_URL'

    def setUp(self):
        self.api = akismet.Akismet(
            key=self.api_key,
            blog_url=self.blog_url
        )


class AkismetConfigurationTests(AkismetTests):
    """
    Tests configuration of the Akismet class.

    """
    def test_config_from_args(self):
        """
        Configuring via explicit arguments succeeds.

        """
        api = akismet.Akismet(
            key=self.api_key,
            blog_url=self.blog_url
        )
        self.assertEqual(self.api_key, api.api_key)
        self.assertEqual(self.blog_url, api.blog_url)

    def test_bad_config_args(self):
        """
        Configuring with bad arguments fails.

        """
        with self.assertRaises(akismet.APIKeyError):
            akismet.Akismet(
                key='invalid',
                blog_url='http://invalid'
            )

    def test_config_from_env(self):
        """
        Configuring via environment variables succeeds.

        """
        try:
            os.environ[self.api_key_env_var] = self.api_key
            os.environ[self.blog_url_env_var] = self.blog_url

            api = akismet.Akismet(key=None, blog_url=None)
            self.assertEqual(self.api_key, api.api_key)
            self.assertEqual(self.blog_url, api.blog_url)

            api = akismet.Akismet()
            self.assertEqual(self.api_key, api.api_key)
            self.assertEqual(self.blog_url, api.blog_url)
        finally:
            os.environ[self.api_key_env_var] = ''
            os.environ[self.blog_url_env_var] = ''

    def test_bad_config_env(self):
        """
        Configuring with bad environment variables fails.

        """
        try:
            os.environ[self.api_key_env_var] = 'invalid'
            os.environ[self.blog_url_env_var] = 'http://invalid'
            with self.assertRaises(akismet.APIKeyError):
                akismet.Akismet()
        finally:
            os.environ[self.api_key_env_var] = ''
            os.environ[self.blog_url_env_var] = ''

    def test_bad_url(self):
        """
        Configuring with a bad URL fails.

        """
        bad_urls = (
            'example.com',
            'ftp://example.com',
            'www.example.com',
            'http//example.com',
            'https//example.com',
        )
        for url in bad_urls:
            with self.assertRaises(akismet.ConfigurationError):
                akismet.Akismet(key=self.api_key, blog_url=url)

    def test_missing_config(self):
        """
        Instantiating without any configuration fails.

        """
        with self.assertRaises(akismet.ConfigurationError):
            akismet.Akismet(key=None, blog_url=None)
        with self.assertRaises(akismet.ConfigurationError):
            akismet.Akismet()

    def test_user_agent(self):
        """
        The Akismet class creates the correct user-agent string.

        """
        api = akismet.Akismet(key=self.api_key, blog_url=self.blog_url)
        expected_agent = "Python/{} | akismet.py/{}".format(
            '{}.{}'.format(*sys.version_info[:2]),
            akismet.__version__
        )
        self.assertEqual(
            expected_agent,
            api.user_agent_header['User-Agent']
        )


class AkismetAPITests(AkismetTests):
    """
    Tests implementation of the Akismet API.

    """
    base_kwargs = {
        'user_ip': '127.0.0.1',
        'user_agent': 'Mozilla',
        # Always send this when testing; Akismet recognizes it as a
        # test query and does not train/learn from it.
        'is_test': 1,
    }

    def test_verify_key_valid(self):
        """
        The verify_key operation succeeds with a valid key and URL.

        """
        self.assertTrue(
            akismet.Akismet.verify_key(self.api_key, self.blog_url)
        )

    def test_verify_key_invalid(self):
        """
        The verify_key operation fails with an invalid key and URL.

        """
        self.assertFalse(
            akismet.Akismet.verify_key('invalid', 'http://invalid')
        )

    def test_comment_check_spam(self):
        """
        The comment_check method correctly identifies spam.

        """
        check_kwargs = self.base_kwargs.copy()
        check_kwargs.update(
            # Akismet guarantees this will be classified spam.
            comment_author='viagra-test-123',
        )
        self.assertTrue(self.api.comment_check(**check_kwargs))

    def test_comment_check_not_spam(self):
        """
        The comment_check method correctly identifies non-spam.

        """
        check_kwargs = self.base_kwargs.copy()
        check_kwargs.update(
            # Akismet guarantees this will not be classified spam.
            user_role='administrator',
        )
        self.assertFalse(self.api.comment_check(**check_kwargs))

    def test_submit_spam(self):
        """
        The submit_spam method succeeds.

        """
        spam_kwargs = self.base_kwargs.copy()
        spam_kwargs.update(
            comment_type='comment',
            comment_author='viagra-test-123',
            comment_content='viagra-test-123',
        )
        self.assertTrue(self.api.submit_spam(**spam_kwargs))

    def test_submit_ham(self):
        """
        The submit_ham method succeeds.

        """
        ham_kwargs = self.base_kwargs.copy()
        ham_kwargs.update(
            comment_type='comment',
            comment_author='Legitimate Author',
            comment_content='This is a legitimate comment.',
            user_role='administrator',
        )
        self.assertTrue(self.api.submit_ham(**ham_kwargs))

    def test_unexpected_verify_key_response(self):
        """
        Unexpected verify_key API responses are correctly handled.

        """
        post_mock = mock.MagicMock()
        with mock.patch('requests.post', post_mock):
            with self.assertRaises(akismet.ProtocolError):
                akismet.Akismet.verify_key(self.api_key, self.blog_url)

    def test_unexpected_comment_check_response(self):
        """
        Unexpected comment_check API responses are correctly handled.

        """
        post_mock = mock.MagicMock()
        with mock.patch('requests.post', post_mock):
            with self.assertRaises(akismet.ProtocolError):
                check_kwargs = self.base_kwargs.copy()
                check_kwargs.update(
                    comment_author='viagra-test-123',
                )
                self.api.comment_check(**check_kwargs)

    def test_unexpected_submit_spam_response(self):
        """
        Unexpected submit_spam API responses are correctly handled.

        """
        post_mock = mock.MagicMock()
        with mock.patch('requests.post', post_mock):
            with self.assertRaises(akismet.ProtocolError):
                spam_kwargs = self.base_kwargs.copy()
                spam_kwargs.update(
                    comment_type='comment',
                    comment_author='viagra-test-123',
                    comment_content='viagra-test-123',
                )
                self.api.submit_spam(**spam_kwargs)

    def test_unexpected_submit_ham_response(self):
        """
        Unexpected submit_ham API responses are correctly handled.

        """
        post_mock = mock.MagicMock()
        with mock.patch('requests.post', post_mock):
            with self.assertRaises(akismet.ProtocolError):
                ham_kwargs = self.base_kwargs.copy()
                ham_kwargs.update(
                    comment_type='comment',
                    comment_author='Legitimate Author',
                    comment_content='This is a legitimate comment.',
                    user_role='administrator',
                )
                self.api.submit_ham(**ham_kwargs)


class AkismetRequestTests(AkismetTests):
    """
    Tests the requests constructed by the Akismet class.

    """
    def _get_mock(self, text):
        """
        Create a mock for requests.post() returning expected text.

        """
        post_mock = mock.MagicMock()
        post_mock.return_value.text = text
        return post_mock

    def _mock_request(self, method, endpoint, text, method_kwargs):
        """
        Issue a mocked request and verify requests.post() was called
        with the correct arguments.

        """
        method_kwargs.update(
            user_ip='127.0.0.1',
            user_agent='Mozilla',
            is_test=1,
        )
        expected_kwargs = method_kwargs.copy()
        expected_kwargs.update(blog=self.blog_url)
        post_mock = self._get_mock(text)
        with mock.patch('requests.post', post_mock):
            getattr(self.api, method)(
                **method_kwargs
            )
            post_mock.assert_called_with(
                endpoint.format(self.api_key),
                data=expected_kwargs,
                headers=akismet.Akismet.user_agent_header
            )

    def test_verify_key(self):
        """
        The request issued by verify_key() is correct.

        """
        post_mock = self._get_mock('valid')
        with mock.patch('requests.post', post_mock):
            akismet.Akismet.verify_key(
                self.api_key,
                self.blog_url
            )
            post_mock.assert_called_with(
                akismet.Akismet.VERIFY_KEY_URL,
                data={'key': self.api_key,
                      'blog': self.blog_url},
                headers=akismet.Akismet.user_agent_header
            )

    def test_comment_check(self):
        """
        The request issued by comment_check() is correct.

        """
        self._mock_request(
            'comment_check',
            akismet.Akismet.COMMENT_CHECK_URL,
            'true',
            {'comment_author': 'viagra-test-123'}
        )

    def test_submit_spam(self):
        """
        The request issued by submit_spam() is correct.

        """
        self._mock_request(
            'submit_spam',
            akismet.Akismet.SUBMIT_SPAM_URL,
            akismet.Akismet.SUBMIT_SUCCESS_RESPONSE,
            {'comment_content': 'Bad comment',
             'comment_author': 'viagra-test-123'}
        )

    def test_submit_ham(self):
        """
        The request issued by submit_ham() is correct.

        """
        self._mock_request(
            'submit_ham',
            akismet.Akismet.SUBMIT_HAM_URL,
            akismet.Akismet.SUBMIT_SUCCESS_RESPONSE,
            {'comment_content': 'Good comment',
             'comment_author': 'Legitimate commenter'}
        )

    def test_full_kwargs(self):
        """
        All optional Akismet arguments are correctly passed through.

        """
        modified_timestamp = datetime.datetime.now()
        posted_timestamp = modified_timestamp - datetime.timedelta(seconds=30)
        full_kwargs = {
            'referrer': 'http://www.example.com/',
            'permalink': 'http://www.example.com/#comment123',
            'comment_type': 'comment',
            'comment_author': 'Legitimate Author',
            'comment_author_email': 'email@example.com',
            'comment_author_url': 'http://www.example.com/',
            'comment_content': 'This is a fine comment.',
            'comment_date_gmt': posted_timestamp.isoformat(),
            'comment_post_modified_gmt': modified_timestamp.isoformat(),
            'blog_lang': 'en_us',
            'blog_charset': 'utf-8',
            'user_role': 'administrator',
        }
        self._mock_request(
            'comment_check',
            akismet.Akismet.COMMENT_CHECK_URL,
            'false',
            full_kwargs
        )
