"""
Tests for the async client's API.

"""

import csv
from typing import Any, cast

import pytest

import akismet
from akismet import _common

pytestmark = [pytest.mark.anyio, pytest.mark.api, pytest.mark.sync_client]


@pytest.mark.parametrize(
    "method", ["CONNECT", "DELETE", "HEAD", "OPTIONS", "PATCH", "PUT", "TRACE"]
)
def test_unsupported_request_method(
    akismet_config: akismet.Config,
    akismet_sync_client: akismet.SyncClient,
    method: str,
):
    """
    Attempting to make a request with an unsupported method raises AkismetError.

    """
    with pytest.raises(akismet.AkismetError):
        akismet_sync_client._request(
            method,  # type: ignore
            _common._API_V11,
            _common._COMMENT_CHECK,
            {"api_key": akismet_config.key},
        )


def test_verify_key_valid(akismet_sync_client: akismet.SyncClient):
    """
    verify_key() returns True when the config is valid.

    """
    assert akismet_sync_client.verify_key()


@pytest.mark.akismet_client(verify_key_response=False)
def test_verify_key_invalid(akismet_sync_client: akismet.SyncClient):
    """
    verify_key() returns False when the config is invalid.

    """
    assert not akismet_sync_client.verify_key()


def test_verify_key_valid_explicit(
    akismet_sync_client: akismet.SyncClient, akismet_config: akismet.Config
):
    """
    verify_key() returns True when the config is valid and explicitly passed in.

    """
    assert akismet_sync_client.verify_key(
        key=akismet_config.key, url=akismet_config.url
    )


@pytest.mark.akismet_client(verify_key_response=False)
def test_verify_key_invalid_explicit(
    akismet_sync_client: akismet.SyncClient, akismet_config: akismet.Config
):
    """
    verify_key() returns False when the config is invalid and explicitly
    passed in.

    """
    assert not akismet_sync_client.verify_key(
        key=akismet_config.key, url=akismet_config.url
    )


@pytest.mark.akismet_fixed_response(response_text="invalid")
@pytest.mark.parametrize(
    ["method_name", "pass_args"],
    [
        ("comment_check", True),
        ("submit_ham", True),
        ("submit_spam", True),
        ("key_sites", False),
        ("usage_limit", False),
    ],
    ids=["comment_check", "submit_ham", "submit_spam", "key_sites", "usage_limit"],
)
def test_request_with_invalid_key(
    akismet_sync_client_fixed_response: akismet.SyncClient,
    akismet_common_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    The request methods other than verify_key() raise akismet.APIKeyError if called with
    an invalid API key/URL.

    """
    method = getattr(akismet_sync_client_fixed_response, method_name)
    args = akismet_common_kwargs if pass_args else {}
    with pytest.raises(akismet.APIKeyError):
        method(**args)


@pytest.mark.parametrize(
    "expected",
    [
        pytest.param(
            akismet.CheckResponse.HAM,
            marks=pytest.mark.akismet_client(
                comment_check_response=akismet.CheckResponse.HAM
            ),
            id="ham",
        ),
        pytest.param(
            akismet.CheckResponse.SPAM,
            marks=pytest.mark.akismet_client(
                comment_check_response=akismet.CheckResponse.SPAM
            ),
            id="spam",
        ),
        pytest.param(
            akismet.CheckResponse.DISCARD,
            marks=pytest.mark.akismet_client(
                comment_check_response=akismet.CheckResponse.DISCARD
            ),
            id="discard",
        ),
    ],
)
def test_comment_check(
    akismet_sync_client: akismet.SyncClient,
    akismet_common_kwargs: dict,
    expected: akismet.CheckResponse,
):
    """
    comment_check() returns the expected value based on the Akismet API's response.

    """
    assert akismet_sync_client.comment_check(**akismet_common_kwargs) == expected


def test_submit_ham(
    akismet_sync_client: akismet.SyncClient, akismet_common_kwargs: dict
):
    """
    submit_ham() returns True when Akismet accepts the submission.

    """
    assert akismet_sync_client.submit_ham(**akismet_common_kwargs)


def test_submit_spam(
    akismet_sync_client: akismet.SyncClient, akismet_common_kwargs: dict
):
    """
    submit_spam() returns True when Akismet accepts the submission.

    """
    assert akismet_sync_client.submit_spam(**akismet_common_kwargs)


def test_key_sites_json(akismet_sync_client: akismet.SyncClient):
    """
    key_sites() returns key usage information in JSON format by default.

    """
    response_json = cast(dict[str, Any], akismet_sync_client.key_sites())
    for key in ["2022-09", "limit", "offset", "total"]:
        assert key in response_json
    sites = response_json["2022-09"]
    for site in sites:
        for key in [
            "site",
            "api_calls",
            "spam",
            "ham",
            "missed_spam",
            "false_positives",
            "is_revoked",
        ]:
            assert key in site


def test_key_sites_csv(akismet_sync_client: akismet.SyncClient):
    """
    key_sites() returns key usage information in CSV format when requested.

    """
    first, *rest = (
        cast(str, akismet_sync_client.key_sites(result_format="csv"))
    ).splitlines()
    assert first.startswith("Active sites for")
    reader = csv.DictReader(rest)
    row = next(reader)
    assert set(row.keys()) == {
        "Site",
        "Total API Calls",
        "Spam",
        "Ham",
        "Missed Spam",
        "False Positives",
        "Is Revoked",
    }


def test_usage_limit(akismet_sync_client: akismet.SyncClient):
    """
    usage_limit() returns the API usage statistics in JSON format.

    """
    response_json = akismet_sync_client.usage_limit()
    assert set(response_json.keys()) == {
        "limit",
        "usage",
        "percentage",
        "throttled",
    }
