"""
Asynchronous Akismet API client implementation.

"""

# SPDX-License-Identifier: BSD-3-Clause

import textwrap
from typing import TYPE_CHECKING, Optional, Union

import httpx

from . import _common, _exceptions

if TYPE_CHECKING:  # pragma: no cover
    import akismet


class AsyncClient:
    """
    Asynchronous Akismet API client.

    All methods of the Akismet 1.1 and 1.2 web APIs are implemented here:

    * :meth:`comment_check`
    * :meth:`key_sites`
    * :meth:`submit_ham`
    * :meth:`submit_spam`
    * :meth:`usage_limit`
    * :meth:`verify_key`

    Use of this client requires an Akismet API key; see <https://akismet.com> for
    instructions on how to obtain one. Once you have an Akismet API key and
    corresponding registered site URL to use with it, you can create an API client in
    either of two ways.

    **Recommended for most uses:** Place your Akismet API key and site URL in the
    environment variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``,
    and then use the :meth:`validated_client` constructor:

    .. code-block:: python

       import akismet
       akismet_client = await akismet.AsyncClient.validated_client()

    This will automatically read the API key and site URL from the environment
    variables, instantiate a client, and use its :meth:`verify_key` method to ensure the
    key and URL are valid before returning the client instance to you. See :ref:`the FAQ
    <alt-constructor>` for the technical reasons why the default constructor does not
    have this behavior.

    **Advanced/unusual use cases:** Instantiate the client directly. You must construct
    a :class:`~akismet.Config` instance with your API key and site URL, and they will
    *not* be automatically validated for you.

    .. code-block:: python

       import akismet
       config = akismet.Config(key=your_api_key, url=your_site_url)
       akismet_client = akismet.AsyncClient(config=config)

    .. warning:: **Consequences of invalid configurationn**

       If you construct an Akismet API client manually and provide an invalid key or
       URL, all operations of the Akismet web service, other than key verification, will
       reply with an invalid-key message. This will cause all client methods other than
       :meth:`verify_key` to raise :exc:`akismet.APIKeyError`. To avoid this situation,
       it is strongly recommended that you call :meth:`verify_key` to validate your
       configuration prior to calling any other methods.

    If you want to modify the HTTP request behavior -- for example, to support a
    required HTTP proxy -- you can construct a custom ``httpx.AsyncClient`` and pass it
    as the keyword argument ``http_client`` to either :meth:`validated_client` or the
    default constructor. See :data:`akismet.USER_AGENT` for the default user-agent
    string used by the Akismet API clients, and <https://www.python-httpx.org> for the
    full documentation of the HTTPX module.

    .. code-block:: python

       import akismet
       import httpx

       from your_app.config import settings

       akismet_client = await akismet.AsyncClient.validated_client(
           http_client=httpx.AsyncClient(
               proxy=settings.PROXY_URL,
               headers={"User-Agent": akismet.USER_AGENT}
           )
       )

    Note that if you only want to set a custom request timeout threshold (the default is
    1 second), you can specify it by setting the environment variable
    ``PYTHON_AKISMET_TIMEOUT`` to a value that can be parsed into a :class:`float` or
    :class:`int`.

    :param config: An Akismet :class:`~akismet.Config`, consisting of an API key and
       site URL.

    :param http_client: An optional ``httpx`` async HTTP client instance to
       use. Generally you should only pass this in if you need significantly customized
       HTTP-client behavior, and if you do pass this argument you are responsible for
       setting an appropriate ``User-Agent`` (see :data:`~akismet.USER_AGENT`), timeout,
       and other configuration values. If all you want is to change the default timeout
       (1 second), store the desired timeout as a floating-point or integer value in the
       environment variable ``PYTHON_AKISMET_TIMEOUT``.

    """

    _http_client: httpx.AsyncClient
    _config: _common.Config

    # Constructors.
    # ----------------------------------------------------------------------------

    def __init__(
        self,
        config: _common.Config,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Default constructor.

        You will almost always want to use :meth:`validated_client` instead.

        """
        self._http_client = http_client or _common._get_async_http_client()
        self._config = config

    @classmethod
    async def validated_client(
        cls, http_client: Optional[httpx.AsyncClient] = None
    ) -> "AsyncClient":
        """
        Constructor of :class:`AsyncClient`.

        This is usually preferred over the default ``AsyncClient()`` constructor,
        because this constructor will discover and validate the Akismet configuration
        (API key and URL) prior to returning the client instance. The Akismet API key
        will be read from the environment variable ``PYTHON_AKISMET_API_KEY``, and the
        registered site URL from the environment variable ``PYTHON_AKISMET_BLOG_URL``.

        :param http_client: An optional ``httpx`` async HTTP client instance to
           use. Generally you should only pass this in if you need significantly
           customized HTTP-client behavior, and if you do pass this argument you are
           responsible for setting an appropriate ``User-Agent`` (see
           :data:`~akismet.USER_AGENT`), timeout, and other configuration values. If all
           you want is to change the default timeout (1 second), store the desired
           timeout as a floating-point or integer value in the environment variable
           ``PYTHON_AKISMET_TIMEOUT``.

        :raises akismet.APIKeyError: When the discovered Akismet configuration is
           invalid according to :meth:`verify_key`.

        :raises akismet.ConfigurationError: When the Akismet configuration is partially
           or completely missing, or when the supplied site URL is in the wrong format
           (does not begin with ``http://`` or ``https://``).

        """
        # While the synchronous version of the client could perform the config discovery
        # and validation in __init__(), here we cannot because this client's
        # verify_key() method is async, and its underlying HTTP client is async. So
        # calling into them would require making __init__ into an async method, and
        # Python does not currently allow __init__() to be usefully async. But a
        # classmethod *can* be async, so we define and encourage the use of an
        # alternative constructor in order to achieve API consistency.
        config = _common._try_discover_config()
        instance = cls(config=config, http_client=http_client)
        if not await instance.verify_key(config.key, config.url):
            raise _exceptions.APIKeyError(
                textwrap.dedent(
                    f"""
                    Akismet API key and/or blog URL were invalid.

                    Found API key: {config.key}
                    Found blog URL: {config.url}
                    """
                )
            )
        return instance

    # Internal/helper methods.
    # ----------------------------------------------------------------------------

    async def _request(
        self,
        method: _common._REQUEST_METHODS,
        version: str,
        endpoint: str,
        data: dict,
    ) -> httpx.Response:
        """
        Make a request to the Akismet API and return the response.

        :param method: The HTTP request method to use.

        :param version: The Akismet API version to use.

        :param endpoint: The Akismet API endpoint to post to.

        :param data: The data to send in the request.

        :raises akismet.RequestError: When an error occurs connecting to Akismet, or
           when Akiset returns a non-success status code.

        """
        method = method.upper()
        if method not in ("GET", "POST"):
            raise _exceptions.AkismetError(
                f"Unrecognized request method attempted: {method}."
            )
        handler = getattr(self._http_client, method.lower())
        request_kwarg = "data" if method == "POST" else "params"
        try:
            response = await handler(
                f"{_common._API_URL}/{version}/{endpoint}", **{request_kwarg: data}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise _exceptions.RequestError(
                f"Akismet responded with error status: {exc.response.status_code}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise _exceptions.RequestError("Akismet timed out.") from exc
        except httpx.RequestError as exc:
            raise _exceptions.RequestError("Error making request to Akismet.") from exc
        except Exception as exc:
            raise _exceptions.RequestError("Error making request to Akismet.") from exc
        # Since it's possible to construct a client without performing up-front API key
        # validation, we have to watch out here for the possibility that we're making
        # requests with an invalid key, and raise the appropriate exception.
        if endpoint != _common._VERIFY_KEY and response.text == "invalid":
            raise _exceptions.APIKeyError(
                "Akismet API key and/or site URL are invalid."
            )
        return response

    async def _get_request(
        self, version: str, endpoint: str, params: dict
    ) -> httpx.Response:
        """
        Make a GET request to the Akismet API and return the response.

        This method is used by most HTTP GET API calls.

        :param version: The Akismet API version to use.

        :param endpoint: The Akismet API endpoint to post to.

        :param params: The querystring parameters to include in the request.

        :raises akismet.APIKeyError: When the configured API key and/or site URL are
           invalid.

        """
        return await self._request("GET", version, endpoint, params)

    async def _post_request(
        self, version: str, endpoint: str, user_ip: str, **kwargs: str
    ) -> httpx.Response:
        """
        Make a POST request to the Akismet API and return the response.

        This method is used by most HTTP POST API calls except key verification.

        :param version: The Akismet API version to use.

        :param endpoint: The Akismet API endpoint to post to.

        :param user_ip: The IP address of the user who submitted the content.

        :raises akismet.APIKeyError: When the configured API key and/or site URL are
           invalid.

        :raises akismet.UnknownArgumentError: When one or more unexpected optional
           argument names are supplied. See `the Akismet documentation
           <https://akismet.com/developers/comment-check/>`_ for details of supported
           optional argument names.

        """
        unknown_args = [k for k in kwargs if k not in _common._OPTIONAL_KEYS]
        if unknown_args:
            raise _exceptions.UnknownArgumentError(
                f"Received unknown argument(s) for Akismet operation {endpoint}"
                f"{', '.join(unknown_args)}"
            )
        data = {
            "api_key": self._config.key,
            "blog": self._config.url,
            "user_ip": user_ip,
            **kwargs,
        }
        return await self._request("POST", version, endpoint, data)

    async def _submit(self, endpoint: str, user_ip: str, **kwargs: str) -> bool:
        """
        Submit ham or spam to the Akismet API.

        :param endpoint: The endpoint (either ``""submit-ham""`` or ``""submit-spam""``)
           to send the content to.

        :param user_ip: The IP address of the user who submitted the content.

        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        response = await self._post_request(
            _common._API_V11, endpoint, user_ip=user_ip, **kwargs
        )
        if response.text == _common._SUBMISSION_RESPONSE:
            return True
        _common._protocol_error(endpoint, response)

    # Public methods corresponding to the methods of the Akismet API.
    # ----------------------------------------------------------------------------

    async def comment_check(
        self, user_ip: str, **kwargs: str
    ) -> "akismet.CheckResponse":
        """
        Check a piece of user-submitted content to determine whether it is spam.

        The IP address of the user posting the content is required. All `other
        comment-check arguments documented by Akismet
        <https://akismet.com/developers/comment-check/>`_ are also optionally accepted.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``; ``comment_type``; and ``comment_author`` and/or
        ``comment_author_email``.

        The return value is an :class:`int` from the :class:`~akismet.CheckResponse`
        enum, which can be used as a truthy value (``0``/:data:`False` if the content is
        not classified as spam, ``1``/:data:`True` if it is classified as spam). But
        making use of the full set of enum values allows detecting the presence of `the
        "discard" value <https://akismet.com/blog/theres-a-ninja-in-your-akismet/>`_ in
        the ``X-akismet-pro-tip`` header to indicate "blatant" spam.

        :param user_ip: The IP address of the user who submitted the content.

        :param str comment_content: (optional, recommended) The content the user
           submitted.

        :param str comment_type: (optional, recommended) The type of content, with
           common values being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.

        :param str comment_author: (optional, recommended) The name (such as username)
           of the content's submitter.

        :param str comment_author_email: (optional, recommended) The email address of
           the content's submitter.

        :param int is_test: (optional) Set to ``1`` if you are making requests for
          testing purposes; this tells Akismet not to incorporate the request into its
          training corpus or allow it to affect future responses.

        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        response = await self._post_request(
            _common._API_V11, _common._COMMENT_CHECK, user_ip=user_ip, **kwargs
        )
        if response.text == "true":
            if response.headers.get("X-akismet-pro-tip", "") == "discard":
                return _common.CheckResponse.DISCARD
            return _common.CheckResponse.SPAM
        if response.text == "false":
            return _common.CheckResponse.HAM
        _common._protocol_error(_common._COMMENT_CHECK, response)

    async def submit_ham(self, user_ip: str, **kwargs: str) -> bool:
        """
        Inform Akismet that a piece of user-submitted comment is not spam.

        The IP address of the user posting the content is required. All `other
        submit-ham arguments documented by Akismet
        <https://akismet.com/developers/submit-ham/>`_ are also optionally accepted.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``; ``comment_type``; and ``comment_author`` and/or
        ``comment_author_email``.

        Will return :data:`True` on success (the only expected response).

        :param user_ip: The IP address of the user who submitted the content.

        :param str comment_content: (optional, recommended) The content the user
           submitted.

        :param str comment_type: (optional, recommended) The type of content, with
           common values being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.

        :param str comment_author: (optional, recommended) The name (such as username)
           of the content's submitter.

        :param str comment_author_email: (optional, recommended) The email address of
           the content's submitter.

        :param int is_test: (optional) Set to ``1`` if you are making requests for
          testing purposes; this tells Akismet not to incorporate the request into its
          training corpus or allow it to affect future responses.

        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        return await self._submit(_common._SUBMIT_HAM, user_ip, **kwargs)

    async def submit_spam(self, user_ip: str, **kwargs: str) -> bool:
        """
        Inform Akismet that a piece of user-submitted comment is spam.

        The IP address of the user posting the content is required. All `other
        submit-spam arguments documented by Akismet
        <https://akismet.com/developers/submit-spam/>`_ are also optionally accepted.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``; ``comment_type``; and ``comment_author`` and/or
        ``comment_author_email``.

        Will return :data:`True` on success (the only expected response).

        :param user_ip: The IP address of the user who submitted the content.

        :param str comment_content: (optional, recommended) The content the user
           submitted.

        :param str comment_type: (optional, recommended) The type of content, with
           common values being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.

        :param str comment_author: (optional, recommended) The name (such as username)
           of the content's submitter.

        :param str comment_author_email: (optional, recommended) The email address of
           the content's submitter.

        :param int is_test: (optional) Set to ``1`` if you are making requests for
          testing purposes; this tells Akismet not to incorporate the request into its
          training corpus or allow it to affect future responses.

        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        return await self._submit(_common._SUBMIT_SPAM, user_ip, **kwargs)

    async def key_sites(  # pylint: disable=too-many-arguments
        self,
        month: Optional[str] = None,
        url_filter: Optional[str] = None,
        result_format: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Union[dict, str]:
        """
        Return Akismet API usage statistics keyed by site.

        All arguments are optional, and the Akismet API will set them to default values
        if not supplied.

        See `the Akismet key-sites documentation
        <https://akismet.com/developers/key-sites-activity/>`_ for examples of the
        response data from this method.

        :param month: The month, in ``"YYYY-MM"`` format, to retrieve statistics for. If
           not supplied, defaults to the current month.

        :param url_filter: A full or partial site URL to filter results by. If not
           supplied, results for all sites under the current API key will be returned.

        :param result_format: The format in which to return results. Supported options
           are ``"json"`` and ``"csv"``. Defaults to ``"json"`` if not supplied.

        :param order: For CSV-formatted results, the column by which the results should
           be sorted.

        :param limit: The maximum number of results to return. If not supplied, defaults
           to 500.

        :param offset: The offset from which to begin result reporting. If not supplied,
           defaults to 0.

        """
        params = {}
        for argument, value in (
            ("month", month),
            ("filter", url_filter),
            ("format", result_format),
            ("order", order),
            ("limit", limit),
            ("offset", offset),
        ):
            if value is not None:
                params[argument] = value
        response = await self._get_request(_common._API_V12, _common._KEY_SITES, params)
        if result_format == "csv":
            return response.text
        return response.json()

    async def usage_limit(self) -> dict:
        """
        Return Akismet API usage statistics for the current month.

        See `the Akismet usage-limit documentation
        <https://akismet.com/developers/usage-limit/>`_ for examples of the response
        data from this method.

        """
        response = await self._get_request(
            _common._API_V12, _common._USAGE_LIMIT, params={"api_key": self._config.key}
        )
        return response.json()

    async def verify_key(self, key: str, url: str) -> bool:
        """
        Verify an Akismet API key and URL.

        Return :data:`True` if the key and URL are valid, :data:`False` otherwise.

        In general, you should not need to explicitly call this method. The
        :meth:`validated_client` constructor will ensure this method is called during
        client construction, after which the now-verified key/URL can be trusted.

        :param key: The API key to check.

        :param url: The URL to check.

        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        response = await self._request(
            "POST", _common._API_V11, _common._VERIFY_KEY, {"key": key, "blog": url}
        )
        if response.text == "valid":
            return True
        if response.text == "invalid":
            return False
        _common._protocol_error(_common._VERIFY_KEY, response)
