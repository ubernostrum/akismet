"""
Base test class and utilities.

"""

# SPDX-License-Identifier: BSD-3-Clause

import os
import typing
import unittest
from http import HTTPStatus

import httpx

import akismet
from akismet import _common, _test_clients


def make_fixed_response_transport(
    response_text: str = "true",
    status_code: HTTPStatus = HTTPStatus.OK,
    response_json: typing.Optional[dict] = None,
) -> httpx.MockTransport:
    """
    Return an ``httpx`` transport that produces a fixed response, for use
    in testing.

    The transport will return a response consisting of:

    * ``status_code`` (default 200)
    * ``response_json`` as the JSON content, if supplied
    * Otherwise ``response_text`` (default ``"true"``) as the response text

    """

    def _handler(
        request: httpx.Request,  # pylint: disable=unused-argument
    ) -> httpx.Response:
        """
        Mock transport handler which returns a controlled response.

        """
        response_kwargs = {"status_code": status_code, "content": response_text}
        if response_json is not None:
            del response_kwargs["content"]
            response_kwargs["json"] = response_json
        return httpx.Response(**response_kwargs)

    return httpx.MockTransport(_handler)


class CommonData:  # pylint: disable=too-few-public-methods
    """
    Common data for all Akismet tests.

    """

    api_key = os.getenv("PYTHON_AKISMET_API_KEY")
    site_url = os.getenv("PYTHON_AKISMET_BLOG_URL")
    verify_key_url = f"{_common._API_URL}/{_common._API_V11}/{_common._VERIFY_KEY}"

    config = akismet.Config(key=_test_clients._TEST_KEY, url=_test_clients._TEST_URL)
    common_kwargs = {"user_ip": "127.0.0.1"}


class AkismetTests(CommonData, unittest.TestCase):
    """
    Base class for synchronous Akismet tests.

    """


class AsyncAkismetTests(CommonData, unittest.IsolatedAsyncioTestCase):
    """
    Base class for asynchronous Akismet tests.

    """
