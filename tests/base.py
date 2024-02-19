"""
Base test class and utilities.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os
import typing
import unittest
from http import HTTPStatus
from unittest import mock

import httpx

import akismet
from akismet import _common


class AkismetTests(unittest.TestCase):
    """
    Base class for Akismet tests, defining utilities used for testing both the sync
    and async clients.

    """

    api_key = os.getenv("PYTHON_AKISMET_API_KEY")
    site_url = os.getenv("PYTHON_AKISMET_BLOG_URL")
    verify_key_url = f"{_common._API_URL}/{_common._API_V11}/{_common._VERIFY_KEY}"

    config = akismet.Config(key="fake-test-key", url="http://example.com")
    common_kwargs = {"user_ip": "127.0.0.1"}

    def custom_response_transport(  # pylint: disable=too-many-arguments
        self,
        response_text: str = "true",
        status_code: HTTPStatus = HTTPStatus.OK,
        response_json: typing.Optional[dict] = None,
        headers: typing.Optional[dict] = None,
        config_valid: bool = True,
    ) -> httpx.MockTransport:
        """
        Return an ``httpx`` transport that produces a particular response, for use
        in testing.

        The transport will return a response consisting of:

        * ``status_code`` (default 200)
        * ``response_json`` as the JSON content, if supplied
        * Otherwise ``response_text`` (default ``"true"``) as the response text
        * And the given ``headers``.

        The only exception to this is the ``verify_key`` operation, which is controlled
        by ``config_valid`` -- ``verify_key`` will succeed if ``config_valid`` is
        ``True`` (the default) and fail if it is ``False``

        """

        def _handler(request: httpx.Request) -> httpx.Response:
            """
            Mock transport handler which returns a controlled response.

            """
            response_kwargs = {"status_code": status_code, "content": response_text}
            if headers is not None:
                response_kwargs["headers"] = headers
            if response_json is not None:
                del response_kwargs["content"]
                response_kwargs["json"] = response_json
            if request.url == self.verify_key_url:
                response_kwargs["content"] = "valid" if config_valid else "invalid"
            return httpx.Response(**response_kwargs)

        return httpx.MockTransport(_handler)

    def custom_response_sync_client(  # pylint: disable=too-many-arguments
        self,
        response_text: str = "true",
        status_code: HTTPStatus = HTTPStatus.OK,
        response_json: typing.Optional[dict] = None,
        headers: typing.Optional[dict] = None,
        config_valid: bool = True,
    ) -> httpx.Client:
        """
        Return a synchronous HTTP client that produces a fixed repsonse, for use in
        testing.

        """
        return httpx.Client(
            transport=self.custom_response_transport(
                response_text, status_code, response_json, headers, config_valid
            )
        )

    def custom_response_async_client(  # pylint: disable=too-many-arguments
        self,
        response_text: str = "true",
        status_code: HTTPStatus = HTTPStatus.OK,
        response_json: typing.Optional[dict] = None,
        headers: typing.Optional[dict] = None,
        config_valid: bool = True,
    ) -> httpx.AsyncClient:
        """
        Return an asynchronous HTTP client that produces a fixed repsonse, for use in
        testing.

        """
        return httpx.AsyncClient(
            transport=self.custom_response_transport(
                response_text, status_code, response_json, headers, config_valid
            )
        )

    def exception_sync_client(
        self, exception_class: Exception, message: str = "Error!"
    ) -> httpx.Client:
        """
        Return a synchronous HTTP client that raises the given exception/message.

        """
        return mock.Mock(
            spec_set=httpx.Client,
            get=mock.Mock(side_effect=exception_class(message)),
            post=mock.Mock(side_effect=exception_class(message)),
        )

    def exception_async_client(
        self, exception_class: Exception, message: str = "Error!"
    ) -> httpx.AsyncClient:
        """
        Return an asynchronous HTTP client that raises the given exception/message.

        """
        return mock.AsyncMock(
            spec_set=httpx.AsyncClient,
            get=mock.AsyncMock(side_effect=exception_class(message)),
            post=mock.AsyncMock(side_effect=exception_class(message)),
        )


class AsyncAkismetTests(AkismetTests, unittest.IsolatedAsyncioTestCase):
    """
    Base class for asynchronous Akismet tests.

    """
