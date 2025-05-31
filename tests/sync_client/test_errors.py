"""
Tests for the sync client's error behaviors.

"""

from http import HTTPStatus

import httpx
import pytest

import akismet

pytestmark = [pytest.mark.errors, pytest.mark.sync_client]

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
def test_error_status(
    akismet_sync_client_fixed_response: akismet.SyncClient,
    akismet_common_kwargs: dict,
    status_code: int,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when a POST request to Akismet responds with an HTTP status
    code indicating an error.

    """
    method = getattr(akismet_sync_client_fixed_response, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(
        akismet.RequestError,
        match=f"Akismet responded with error status: {status_code}",
    ):
        method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=httpx.TimeoutException)
def test_error_timeout(
    akismet_sync_client_exception: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when the request to Akismet times out.

    """
    method = getattr(akismet_sync_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Akismet timed out."):
        method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=httpx.RequestError)
def test_error_other_httpx(
    akismet_sync_client_exception: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when a generic httpx request error occurs.

    """
    method = getattr(akismet_sync_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Error making request to Akismet."):
        method(**args)


@check_all_methods
@pytest.mark.akismet_exception_response(exception_class=TypeError)
def test_error_other(
    akismet_sync_client_exception: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    RequestError is raised when any other (non-httpx) exception occurs during the
    request.

    """
    method = getattr(akismet_sync_client_exception, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.RequestError, match="Error making request to Akismet."):
        method(**args)


@pytest.mark.parametrize("method_name", ["comment_check", "submit_ham", "submit_spam"])
def test_unknown_argument(
    akismet_sync_client: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
):
    """
    UnknownArgumentError is raised when an argument outside the supported set is passed
    to one of the POST request methods.

    """
    with pytest.raises(akismet.UnknownArgumentError, match="bad_argument"):
        getattr(akismet_sync_client, method_name)(
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
def test_protocol_error(
    akismet_sync_client_fixed_response: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    ProtocolError is raised when ``comment_check()`` receives an unexpected
    response.

    """
    method = getattr(akismet_sync_client_fixed_response, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.ProtocolError):
        method(**args)
