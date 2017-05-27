import os
import sys
import textwrap

import requests


__version__ = '1.0'


class AkismetError(Exception):
    """
    Base exception class for Akismet errors.

    """
    pass


class ProtocolError(AkismetError):
    """
    Indicates an unexpected or non-standard response was received from
    Akismet.

    """
    pass


class ConfigurationError(AkismetError):

    """
    Indicates an Akismet configuration error (config missing or invalid).

    """
    pass


class APIKeyError(ConfigurationError):
    """
    Indicates the supplied Akismet API key/URL are invalid.

    """
    pass


class Akismet:
    """
    A Python wrapper for the Akismet web API.

    Two configuration parameters -- your Akismet API key and
    registered URL -- are required; they can be passed when
    instantiating, or set in the environment variables
    PYTHON_AKISMET_API_KEY and PYTHON_AKISMET_BLOG_URL.

    All the operations of the Akismet API are exposed here:

    * verify_key

    * comment_check

    * submit_spam

    * submit_ham

    For full details of the Akismet API, see the Akismet documentation:

    https://akismet.com/development/api/#detailed-docs

    The verify_key operation will be automatically called for you as
    this class is instantiated; ConfigurationError will be raised if
    the configuration cannot be found or if the supplied key/URL are
    invalid.

    """
    COMMENT_CHECK_URL = 'https://{}.rest.akismet.com/1.1/comment-check'
    SUBMIT_HAM_URL = 'https://{}.rest.akismet.com/1.1/submit-ham'
    SUBMIT_SPAM_URL = 'https://{}.rest.akismet.com/1.1/submit-spam'
    VERIFY_KEY_URL = 'https://rest.akismet.com/1.1/verify-key'

    SUBMIT_SUCCESS_RESPONSE = 'Thanks for making the web a better place.'

    OPTIONAL_KEYS = (
        'referrer', 'permalink', 'comment_type', 'comment_author',
        'comment_author_email', 'comment_author_url', 'comment_content',
        'comment_date_gmt', 'comment_post_modified_gmt', 'blog_lang',
        'blog_charset', 'user_role', 'is_test'
    )

    user_agent_header = {
        'User-Agent': 'Python/{} | akismet.py/{}'.format(
            '{}.{}'.format(*sys.version_info[:2]),
            __version__
        )
    }

    def __init__(self, key=None, blog_url=None):
        maybe_key = (key if key is not None
                     else os.getenv('PYTHON_AKISMET_API_KEY'))
        maybe_url = (blog_url if blog_url is not None
                     else os.getenv('PYTHON_AKISMET_BLOG_URL'))
        if maybe_key in (None, '') or maybe_url in (None, ''):
            raise ConfigurationError(
                textwrap.dedent('''
                Could not find full Akismet configuration.

                Found API key: {}
                Found blog URL: {}
                '''.format(maybe_key, maybe_url)
                )
            )
        if not maybe_url.startswith(('http://', 'https://')):
            raise ConfigurationError(
                textwrap.dedent('''
                Invalid site URL specified: {}

                Akismet requires the full URL including the leading
                'http://' or 'https://'.
                ''').format(maybe_url)
            )
        if not self.verify_key(maybe_key, maybe_url):
            raise APIKeyError(
                'Akismet key ({}, {}) is invalid.'.format(
                    maybe_key, maybe_url
                )
            )
        self.api_key = maybe_key
        self.blog_url = maybe_url

    def _api_request(self, endpoint, user_ip, user_agent, **kwargs):
        """
        Makes a request to the Akismet API.

        This method is used for all API calls except key verification,
        since all endpoints other than key verification must
        interpolate the API key into the URL and supply certain basic
        data.

        """
        data = {'blog': self.blog_url,
                'user_ip': user_ip,
                'user_agent': user_agent}
        for key in self.OPTIONAL_KEYS:
            if key in kwargs:
                data[key] = kwargs[key]
        response = requests.post(
            endpoint.format(self.api_key),
            data=data,
            headers=self.user_agent_header)
        return response.text

    def _submission_request(self, operation, user_ip, user_agent, **kwargs):
        """
        Submits spam or ham to the Akismet API.

        """
        endpoint = {'submit_spam': self.SUBMIT_SPAM_URL,
                    'submit_ham': self.SUBMIT_HAM_URL}[operation]
        response_text = self._api_request(
            endpoint, user_ip, user_agent, **kwargs
        )
        if response_text == self.SUBMIT_SUCCESS_RESPONSE:
            return True
        else:
            self._protocol_error(operation, response_text)

    @classmethod
    def _protocol_error(cls, operation, message):
        """
        Raises an appropriate exception for unexpected API responses.

        """
        raise ProtocolError(
            textwrap.dedent('''
            Received unexpected or non-standard response from Akismet API.

            API operation was: {}
            API response received was: {}
            ''').format(operation, message)
        )

    @classmethod
    def verify_key(cls, key, blog_url):
        """
        Verifies an Akismet API key and URL.

        Returns True if the key and URL are valid, False otherwise.

        """
        response = requests.post(
            cls.VERIFY_KEY_URL,
            data={'key': key, 'blog': blog_url},
            headers=cls.user_agent_header
        )
        if response.text == 'valid':
            return True
        elif response.text == 'invalid':
            return False
        else:
            cls._protocol_error('verify_key', response.text)

    def comment_check(self, user_ip, user_agent, **kwargs):
        """
        Checks a comment to determine whether it is spam.

        The IP address and user-agent string of the remote user are
        required. All other arguments documented by Akismet (other
        than the PHP server information) are also optionally accepted.
        See the Akismet API documentation for a full list:

        https://akismet.com/development/api/#comment-check

        Like the Akismet web API, returns True for a comment that is
        spam, and False for a comment that is not spam.

        """
        response_text = self._api_request(
            self.COMMENT_CHECK_URL, user_ip, user_agent, **kwargs
        )
        if response_text == 'true':
            return True
        elif response_text == 'false':
            return False
        else:
            self._protocol_error('comment_check', response_text)

    def submit_spam(self, user_ip, user_agent, **kwargs):
        """
        Informs Akismet that a comment is spam.

        The IP address and user-agent string of the remote user are
        required. All other arguments documented by Akismet (other
        than the PHP server information) are also optionally accepted.
        See the Akismet API documentation for a full list:

        https://akismet.com/development/api/#submit-spam

        Returns True on success (the only expected response).

        """
        return self._submission_request(
            'submit_spam', user_ip, user_agent, **kwargs
        )

    def submit_ham(self, user_ip, user_agent, **kwargs):
        """
        Informs Akismet that a comment is not spam.

        The IP address and user-agent string of the remote user are
        required. All other arguments documented by Akismet (other
        than the PHP server information) are also optionally accepted.
        See the Akismet API documentation for a full list:

        https://akismet.com/development/api/#submit-ham

        Returns True on success (the only expected response).

        """
        return self._submission_request(
            'submit_ham', user_ip, user_agent, **kwargs
        )
