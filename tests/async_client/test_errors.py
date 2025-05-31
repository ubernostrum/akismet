"""
Tests for the async client's error behaviors.

"""

from http import HTTPStatus

import httpx
import pytest

import akismet

pytestmark = [pytest.mark.anyio, pytest.mark.async_client, pytest.mark.constructors]

check_all_methods = pytest.mark.parametrize(
    ["method_name", "pass_args"],
    [
        ("comment_check", True),
        ("key_sites", False),
        ("submit_ham", True),
        ("submit_spam", True),
        ("usage_limit", False),
        ("verify_key", False),
    ],
    ids=[
        "comment_check",
        "key_sites",
        "submit_ham",
        "submit_spam",
        "usage_limit",
        "verify_key",
    ],
)


@check_all_methods
@pytest.mark.parametrize(
    "status_code",
    [
        pytest.param(
            code.value, marks=pytest.mark.akismet_fixed_response(status_code=code)
        )
        for code in HTTPStatus
        if 400 <= code < 600
    ],
    ids=[code.value for code in HTTPStatus if 400 <= code < 600],
)
async def test_error_status(
    akismet_async_client_fixed_response: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    status_code: int,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when a POST request to Akismet responds with an HTTP status
    code indicating an error.

    """
    method = getattr(akismet_async_client_fixed_response, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(
        akismet.RequestError,
        match=f"Akismet responded with error status: {status_code}",
    ):
        await method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=httpx.TimeoutException)
async def test_error_timeout(
    akismet_async_client_exception: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when the request to Akismet times out.

    """
    method = getattr(akismet_async_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Akismet timed out."):
        await method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=httpx.RequestError)
async def test_error_other_httpx(
    akismet_async_client_exception: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when a generic httpx request error occurs.

    """
    method = getattr(akismet_async_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Error making request to Akismet."):
        await method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=TypeError)
async def test_error_other(
    akismet_async_client_exception: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when any other (non-httpx) exception occurs during the
    request.

    """
    method = getattr(akismet_async_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Error making request to Akismet."):
        await method(**args)


@pytest.mark.parametrize("method_name", ["comment_check", "submit_ham", "submit_spam"])
async def test_unknown_argument(
    akismet_async_client: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
):
    """
    UnknownArgumentError is raised when an argument outside the supported set is passed
    to one of the POST request methods.

    """
    with pytest.raises(akismet.UnknownArgumentError, match="bad_argument"):
        await getattr(akismet_async_client, method_name)(
            bad_argument=1, **akismet_common_kwargs
        )


@pytest.mark.parametrize(
    ["method_name", "pass_args"],
    [
        ("comment_check", True),
        ("submit_ham", True),
        ("submit_spam", True),
        ("verify_key", False),
    ],
    ids=["comment_check", "submit_ham", "submit_spam", "verify_key"],
)
@pytest.mark.akismet_fixed_response(response_text="bad")
async def test_protocol_error(
    akismet_async_client_fixed_response: akismet.AsyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    ProtocolError is raised when ``comment_check()`` receives an unexpected
    response.

    """
    method = getattr(akismet_async_client_fixed_response, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.ProtocolError):
        await method(**args)
