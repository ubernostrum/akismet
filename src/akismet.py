import os
import sys
import textwrap

import requests


__version__ = u'1.0.1'


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
    COMMENT_CHECK_URL = u'https://{}.rest.akismet.com/1.1/comment-check'
    SUBMIT_HAM_URL = u'https://{}.rest.akismet.com/1.1/submit-ham'
    SUBMIT_SPAM_URL = u'https://{}.rest.akismet.com/1.1/submit-spam'
    VERIFY_KEY_URL = u'https://rest.akismet.com/1.1/verify-key'

    SUBMIT_SUCCESS_RESPONSE = u'Thanks for making the web a better place.'

    OPTIONAL_KEYS = (
        u'referrer', u'permalink', u'comment_type', u'comment_author',
        u'comment_author_email', u'comment_author_url', u'comment_content',
        u'comment_date_gmt', u'comment_post_modified_gmt', u'blog_lang',
        u'blog_charset', u'user_role', u'is_test'
    )

    user_agent_header = {
        u'User-Agent': 'Python/{} | akismet.py/{}'.format(
            u'{}.{}'.format(*sys.version_info[:2]),
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
                textwrap.dedent(u'''
                Could not find full Akismet configuration.

                Found API key: {}
                Found blog URL: {}
                '''.format(maybe_key, maybe_url)
                )
            )
        if not self.verify_key(maybe_key, maybe_url):
            raise APIKeyError(
                u'Akismet key ({}, {}) is invalid.'.format(
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
        data = {u'blog': self.blog_url,
                u'user_ip': user_ip,
                u'user_agent': user_agent}
        for key in self.OPTIONAL_KEYS:
            if key in kwargs:
                data[key] = kwargs[key]
        response = requests.post(
            endpoint.format(self.api_key),
            data=data,
            headers=self.user_agent_header)
        return response

    def _submission_request(self, operation, user_ip, user_agent, **kwargs):
        """
        Submits spam or ham to the Akismet API.

        """
        endpoint = {u'submit_spam': self.SUBMIT_SPAM_URL,
                    u'submit_ham': self.SUBMIT_HAM_URL}[operation]
        response = self._api_request(
            endpoint, user_ip, user_agent, **kwargs
        )
        if response.text == self.SUBMIT_SUCCESS_RESPONSE:
            return True
        else:
            self._protocol_error(operation, response)

    @classmethod
    def _protocol_error(cls, operation, response):
        """
        Raises an appropriate exception for unexpected API responses.

        """
        raise ProtocolError(
            textwrap.dedent(u'''
            Received unexpected or non-standard response from Akismet API.

            API operation was: {}
            API response received was: {}
            Debug header value was: {}
            ''').format(
                operation,
                response.text,
                response.headers.get('X-akismet-debug-help')
            )
        )

    @classmethod
    def verify_key(cls, key, blog_url):
        """
        Verifies an Akismet API key and URL.

        Returns True if the key and URL are valid, False otherwise.

        """
        if not blog_url.startswith((u'http://', u'https://')):
            raise ConfigurationError(
                textwrap.dedent(u'''
                Invalid site URL specified: {}

                Akismet requires the full URL including the leading
                'http://' or 'https://'.
                ''').format(blog_url)
            )
        response = requests.post(
            cls.VERIFY_KEY_URL,
            data={u'key': key, u'blog': blog_url},
            headers=cls.user_agent_header
        )
        if response.text == u'valid':
            return True
        elif response.text == u'invalid':
            return False
        else:
            cls._protocol_error(u'verify_key', response)

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
        response = self._api_request(
            self.COMMENT_CHECK_URL, user_ip, user_agent, **kwargs
        )
        if response.text == u'true':
            return True
        elif response.text == u'false':
            return False
        else:
            self._protocol_error(u'comment_check', response)

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
            u'submit_spam', user_ip, user_agent, **kwargs
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
            u'submit_ham', user_ip, user_agent, **kwargs
        )
