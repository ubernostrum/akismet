"""
Test configuration.

"""

import typing
from http import HTTPStatus
from unittest import mock

import httpx
import pytest

import akismet
from akismet import _test_clients

# pylint: disable=redefined-outer-name


@pytest.fixture
def anyio_backend() -> str:
    """
    Return the async backend to use for async tests.

    """
    return "asyncio"


@pytest.fixture
def akismet_common_kwargs() -> dict:
    """
    Return the common set of base arguments neded for most Akismet API calls.

    """
    return {"user_ip": "127.0.0.1"}


@pytest.fixture
def akismet_end_to_end_kwargs(akismet_common_kwargs: dict) -> dict:
    """
    Return the set of base arguments needed for end-to-end test calls.

    """
    return {"is_test": 1, **akismet_common_kwargs}


@pytest.fixture
def akismet_fixed_response_transport() -> (
    typing.Callable[[str, HTTPStatus, typing.Optional[dict]], httpx.MockTransport]
):
    """
    Factory function to generate an httpx transport with a fixed response.

    """

    def _fixed_response_transport(
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
            return httpx.Response(**response_kwargs)  # type: ignore

        return httpx.MockTransport(_handler)

    return _fixed_response_transport


@pytest.fixture
def akismet_sync_client_fixed_response(
    request: pytest.FixtureRequest,
    akismet_fixed_response_transport: typing.Callable[
        [str, HTTPStatus, typing.Optional[dict]], httpx.MockTransport
    ],
) -> akismet.SyncClient:
    """
    Return a (sync) Akismet test client with an HTTP client which produces a fixed
    response.

    """
    marker = request.node.get_closest_marker("akismet_fixed_response")
    return akismet.SyncClient(
        http_client=httpx.Client(
            transport=akismet_fixed_response_transport(**marker.kwargs)  # type: ignore
        )
    )


@pytest.fixture
def akismet_async_client_fixed_response(
    request: pytest.FixtureRequest,
    akismet_fixed_response_transport: typing.Callable[
        [str, HTTPStatus, typing.Optional[dict]], httpx.MockTransport
    ],
) -> akismet.AsyncClient:
    """
    Return an (async) Akismet test client with an HTTP client which produces a fixed
    response.

    """
    marker = request.node.get_closest_marker("akismet_fixed_response")
    return akismet.AsyncClient(
        http_client=httpx.AsyncClient(
            transport=akismet_fixed_response_transport(**marker.kwargs)  # type: ignore
        )
    )


@pytest.fixture
def akismet_sync_http_client_exception(request: pytest.FixtureRequest) -> httpx.Client:
    """
    Return a (sync) HTTP client which always raises an exception.

    """
    marker = request.node.get_closest_marker("akismet_exception_response")
    exception_class = marker.kwargs.get("exception_class", Exception)
    error_message = marker.kwargs.get("error_message", "Error!")

    return mock.Mock(
        spec_set=httpx.Client,
        get=mock.Mock(side_effect=exception_class(error_message)),
        post=mock.Mock(side_effect=exception_class(error_message)),
    )


@pytest.fixture
def akismet_async_http_client_exception(
    request: pytest.FixtureRequest,
) -> httpx.AsyncClient:
    """
    Return an (async) HTTP client which always raises an exception.

    """
    marker = request.node.get_closest_marker("akismet_exception_response")
    exception_class = marker.kwargs.get("exception_class", Exception)
    error_message = marker.kwargs.get("error_message", "Error!")

    return mock.AsyncMock(
        spec_set=httpx.AsyncClient,
        get=mock.Mock(side_effect=exception_class(error_message)),
        post=mock.Mock(side_effect=exception_class(error_message)),
    )


@pytest.fixture
def akismet_sync_client_exception(
    akismet_sync_http_client_exception,
) -> akismet.SyncClient:
    """
    Return a (sync) Akismet test client whose HTTP client always raises an exception.

    """
    return akismet.SyncClient(http_client=akismet_sync_http_client_exception)


@pytest.fixture
def akismet_async_client_exception(
    akismet_async_http_client_exception,
) -> akismet.AsyncClient:
    """
    Return an (async) Akismet test client whose HTTP client always raises an exception.

    """
    return akismet.AsyncClient(http_client=akismet_async_http_client_exception)


@pytest.fixture
def akismet_config() -> akismet.Config:
    """
    Return an Akismet config object.

    """
    return akismet.Config(key=_test_clients._TEST_KEY, url=_test_clients._TEST_URL)


@pytest.fixture
def akismet_bad_config() -> akismet.Config:
    """
    Return an Akismet config object with invalid values.

    """
    return akismet.Config(key="INVALID_TEST_KEY", url="http://example.com")
