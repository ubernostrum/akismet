import os
import os.path
import sys
import textwrap

import requests


__version__ = '1.0'


class AkismetError(Exception):
    """
    Base exception class for Akismet errors.

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


class Akismet(object):
    """
    A Python implementation of the Akismet web API.

    Two configuration parameters -- your Akismet API key and
    registered URL -- are required; they can be passed when
    instantiating, or set in the environment variables
    PYTHON_AKISMET_API_KEY and PYTHON_AKISMET_BLOG_URL.

    All the operations of the Akismet API are exposed here:

    * verify_key

    * comment_check

    * submit_spam

    * submit_ham

    The verify_key operation will be automatically called for you as
    this class is instantiated; ConfigurationError will be raised if
    the configuration cannot be found or if the supplied key/URL are
    invalid.

    """
    COMMENT_CHECK_URL = 'https://{}.rest.akismet.com/1.1/comment-check'
    SUBMIT_HAM_URL = 'https://{}.rest.akismet.com/1.1/submit-ham'
    SUBMIT_SPAM_URL = 'https://{}.rest.akismet.com/1.1/submit-spam'
    VERIFY_KEY_URL = 'https://rest.akismet.com/1.1/verify-key'

    INVALID_CONFIG = 'Akismet configuration ({}, {}) is invalid.'
    MISSING_CONFIG = textwrap.dedent('''Could not find full Akismet configuration.
    
    Found API key: {}
    Found blog URL: {}
    ''')
    PROTOCOL_ERROR = textwrap.dedent('''
    Received unexpected or non-standard response from Akismet API.
    
    API operation was: {}
    API response received was: {}
    ''')
    
    USER_AGENT = 'Python/{} | akismet.py/{}'

    API_KEY_ENV_VAR = 'PYTHON_AKISMET_API_KEY'
    BLOG_URL_ENV_VAR = 'PYTHON_AKISMET_BLOG_URL'
    USER_AGENT_ENV_VAR = 'PYTHON_AKISMET_USER_AGENT'

    OPTIONAL_KEYS = (
        'referrer', 'permalink', 'comment_type', 'comment_author',
        'comment_author_email', 'comment_author_url', 'comment_content',
        'comment_date_gmt', 'comment_post_modified_gmt', 'blog_lang',
        'blog_charset', 'user_role', 'is_test'
    )

    def _set_key_and_url(self, key=None, blog_url=None):
        maybe_key = key if key is not None else os.getenv(self.API_KEY_ENV_VAR)
        maybe_url = blog_url if blog_url is not None else os.getenv(self.BLOG_URL_ENV_VAR)
        if maybe_key is None or maybe_url is None:
            raise ConfigurationError(self.MISSING_CONFIG.format(maybe_key, maybe_url))
        try:
            self.verify_key(maybe_key, maybe_url)
            self.api_key = maybe_key
            self.blog_url = maybe_url
        except APIKeyError:
            raise ConfigurationError(self.INVALID_CONFIG.format(maybe_key, maybe_url))

    def _protocol_error(self, operation, message):
        raise AkismetError(self.PROTOCOL_ERROR.format(operation, message))

    def __init__(self, key=None, blog_url=None):
        self.user_agent = self.USER_AGENT.format(
            '{}.{}.{}'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2]),
            __version__
        )
        self._set_key_and_url(key, blog_url)

    def _get_headers(self):
        return {'User-Agent': self.user_agent}

    def verify_key(self, key, blog_url):
        """
        Verify an Akismet API key and URL.

        If the key and URL are valid, this function returns None;
        otherwise, it raises APIKeyError.

        """
        resp = requests.post(self.VERIFY_KEY_URL,
                             data={'key': key, 'blog': blog_url},
                             headers=self._get_headers()
        )
        if resp.text == 'valid':
            return
        elif resp.text == 'invalid':
            raise APIKeyError(self.INVALID_CONFIG.format(key, blog_url))
        else:
            self._protocol_error('verify_key', resp.text)

    def comment_check(self, user_ip, user_agent, **kwargs):
        """
        Check a comment to determine whether it is spam.

        The IP address and user-agent string of the remote user are
        required. All other arguments documented by Akismet (other
        than the PHP server information) are also optionally accepted;
        see the Akismet API documentation for a full list:

        https://akismet.com/development/api/#comment-check

        Like the Akismet web API, returns True for a comment that is
        spam, and False for a comment that is not spam.

        """
        data = {'blog': self.blog_url, 'user_ip': user_ip, 'user_agent': user_agent}
        for key in self.OPTIONAL_KEYS:
            if key in kwargs:
                data[key] = kwargs[key]
        resp = requests.post(self.COMMENT_CHECK_URL.format(self.api_key),
                             data=data,
                             headers=self._get_headers())
        if resp.text == 'true':
            return True
        elif resp.text == 'false':
            return False
        else:
            self._protocol_error('comment_check', resp.text)
