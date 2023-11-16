"""
Asynchronous Akismet API client implementation.

"""
# SPDX-License-Identifier: BSD-3-Clause

import textwrap
import typing

import httpx

from . import _common, _exceptions

if typing.TYPE_CHECKING:  # pragma: no cover
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
    corresponding registered site URL to use with it, place them in the environment
    variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``, and they will
    be automatically detected and used.

    .. admonition:: **Always use the** ``client()`` **constructor!**

       This class should generally *not* be directly instantiated via the default
       constructor (``AyncClient()``) -- instead, call :meth:`client` to ensure the
       Akismet configuration is appropriately auto-discovered and validated for you.

       If you *must* instantiate this class directly, it then becomes your
       responsibility to manually provide and perform validation of the Akismet
       configuration.

       See :ref:`the FAQ <alt-constructor>` for an explanation of the technical reasons
       for this.

    """

    _http_client: httpx.AsyncClient
    _config: _common.Config

    # Constructors.
    # ----------------------------------------------------------------------------

    def __init__(
        self,
        config: _common.Config,
        http_client: typing.Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._http_client = http_client or _common._get_async_http_client()
        self._config = config

    @classmethod
    async def client(
        cls, http_client: typing.Optional[httpx.AsyncClient] = None
    ) -> "AsyncClient":
        """
        Constructor of :class:`AsyncClient`.

        This is always preferred over the default ``AsyncClient()`` constructor, because
        this constructor will discover and validate the Akismet configuration (API key
        and URL) prior to returning the client instance. The Akismet API key will be
        read from the environment variable ``PYTHON_AKISMET_API_KEY``, and the
        registered site URL from the environment variable ``PYTHON_AKISMET_BLOG_URL``.

        :param http_client: An optional HTTP client instance to use. If not supplied,
           will default to an ``httpx.AsyncClient`` instance. Generally you should only
           pass this in if you need significantly customized HTTP-client behavior, and
           if you do pass this argument you are responsible for setting an appropriate
           ``User-Agent`` (see :data:`~akismet.USER_AGENT`), timeout, and other
           configuration values. If all you want is to change the default timeout (1
           second), store the desired timeout as a floating-point or integer value in
           the environment variable ``PYTHON_AKISMET_TIMEOUT``.
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
        method: str,
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

        The IP address of the user posting the content is required. All `other arguments
        documented by Akismet <https://akismet.com/developers/comment-check/>`_ are also
        optionally accepted, except for the PHP server information array.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``, ``comment_type``, and ``comment_author`` and/or
        ``comment_author_email``.

        The return value is an :class:`int` from the :class:`~akismet.CheckResponse`
        enum, which can be used as a truthy value (``0``/:data:`False` if the content is
        not classified as spam, ``1``/:data:`True` if it is classified as spam). But
        making use of the full set of enum values allows detecting the presence of `the
        "discard" value <https://akismet.com/blog/theres-a-ninja-in-your-akismet/>`_ in
        the ``X-akismet-pro-tip`` header to indicate "blatant" spam.

        :param user_ip: The IP address of the user who submitted the content.
        :param str comment_content: (optional) The content the user submitted.
        :param str comment_type: (optional) The type of content, with common values
           being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.
        :param str comment_author: (optional) The name (such as username) of the
           content's submitter.
        :param str comment_author_email: (optional) The email address of the content's
           submitter.
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

        The IP address of the user posting the content is required. All `other optional
        arguments documented by Akismet <https://akismet.com/developers/submit-ham/>`_
        are also optionally accepted, except for the PHP server information array.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``, ``comment_type``, and ``comment_author`` and/or
        ``comment_author_email``.

        Will return :data:`True` on success (the only expected response).

        :param user_ip: The IP address of the user who submitted the content.
        :param str comment_content: (optional) The content the user submitted.
        :param str comment_type: (optional) The type of content, with common values
           being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.
        :param str comment_author: (optional) The name (such as username) of the
           content's submitter.
        :param str comment_author_email: (optional) The email address of the content's
           submitter.
        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        return await self._submit(_common._SUBMIT_HAM, user_ip, **kwargs)

    async def submit_spam(self, user_ip: str, **kwargs: str) -> bool:
        """
        Inform Akismet that a piece of user-submitted comment is spam.

        The IP address of the user posting the content is required. All `other arguments
        optionally documented by Akismet <https://akismet.com/developers/submit-spam/>`_
        are also optionally accepted, except for the PHP server information array.

        It is recommended that you supply at least the following optional arguments:
        ``comment_content``, ``comment_type``, and ``comment_author`` and/or
        ``comment_author_email``.

        Will return :data:`True` on success (the only expected response).

        :param user_ip: The IP address of the user who submitted the content.
        :param str comment_content: (optional) The content the user submitted.
        :param str comment_type: (optional) The type of content, with common values
           being ``"comment"``, ``"forum-post"``, ``"contact-form"``, and
           ``"signup"``. See the Akismet service documentation for a full list of
           common/recommended types.
        :param str comment_author: (optional) The name (such as username) of the
           content's submitter.
        :param str comment_author_email: (optional) The email address of the content's
           submitter.
        :raises akismet.ProtocolError: When an unexpected/invalid response type is
           received from the Akismet API.

        """
        return await self._submit(_common._SUBMIT_SPAM, user_ip, **kwargs)

    async def key_sites(  # pylint: disable=too-many-arguments
        self,
        month: typing.Optional[str] = None,
        url_filter: typing.Optional[str] = None,
        result_format: typing.Optional[str] = None,
        order: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
    ) -> typing.Union[dict, str]:
        """
        Return Akismet API usage statistics keyed by site.

        All arguments are optional, and the Akismet API will set them to default values
        if not supplied.

        :param month: The month, in ``"YYYY-MM"`` format, to retrieve statistics for. If
           not supplied, defaults to the current month.
        :param url_filter: A full or partial site URL to filter results by. If not
           supplied, results for all sites under the current API key will be returned.
        :param result_format: The format in which to return results. Supported options
           are ``"json"`` and ``"csv"`` Defaults to ``"json"`` if not supplied.
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
        :meth:`client` constructor will ensure this method is called during client
        construction, after which the now-verified key/URL can be trusted.

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
