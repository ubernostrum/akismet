"""
End-to-end (live requests to the Akismet web service) tests for the async client.

"""

import pytest

import akismet
from akismet import _common

pytestmark = [pytest.mark.anyio, pytest.mark.async_client, pytest.mark.end_to_end]


async def test_construct_config_valid():
    """
    With a valid configuration, constructing a client succeeds.

    """
    await akismet.AsyncClient.validated_client()


async def test_construct_config_invalid_key(
    monkeypatch: pytest.MonkeyPatch, akismet_bad_config: akismet.Config
):
    """
    With an invalid API key, constructing a client raises an APIKeyError.

    """
    monkeypatch.setenv(_common._KEY_ENV_VAR, akismet_bad_config.key)
    monkeypatch.setenv(_common._URL_ENV_VAR, akismet_bad_config.url)
    with pytest.raises(akismet.APIKeyError):
        await akismet.AsyncClient.validated_client()


async def test_verify_key_valid():
    """
    verify_key() returns True when the config is valid.

    """
    client = akismet.AsyncClient()
    assert await client.verify_key()


async def test_verify_key_invalid(akismet_bad_config: akismet.Config):
    """
    verify_key() returns False when the config is invalid.

    """
    client = akismet.AsyncClient()
    assert not await client.verify_key(akismet_bad_config.key, akismet_bad_config.url)


@pytest.mark.parametrize(
    ["method_name", "pass_args"],
    [
        ("comment_check", True),
        ("submit_ham", True),
        ("submit_spam", True),
        ("key_sites", False),
        ("usage_limit", False),
    ],
    ids=["comment_check", "submit_nam", "submit_spam", "key_sites", "usage_limit"],
)
async def test_request_with_invalid_key(
    akismet_bad_config: akismet.Config,
    akismet_end_to_end_kwargs: dict,
    method_name: str,
    pass_args: bool,
):
    """
    The request methods other than verify_key() raise akismet.APIKeyError if called with
    an invalid API key/URL.

    """
    client = akismet.AsyncClient(config=akismet_bad_config)
    method = getattr(client, method_name)
    args = akismet_end_to_end_kwargs if pass_args else {}
    with pytest.raises(akismet.APIKeyError):
        await method(**args)


async def test_comment_check_spam(
    akismet_end_to_end_kwargs: dict, akismet_spam_author: str
):
    """
    comment_check() returns the SPAM value when Akismet declares the content to be spam.

    """
    client = akismet.AsyncClient()
    assert (
        await client.comment_check(
            comment_content="test",
            comment_author=akismet_spam_author,
            **akismet_end_to_end_kwargs,
        )
        == akismet.CheckResponse.SPAM
    )


async def test_comment_check_ham(
    akismet_end_to_end_kwargs: dict, akismet_ham_role: str
):
    """
    comment_check() returns the HAM value when Akismet declares the content to be ham.

    """
    client = akismet.AsyncClient()
    assert (
        await client.comment_check(
            comment_content="test",
            user_role=akismet_ham_role,
            **akismet_end_to_end_kwargs,
        )
        == akismet.CheckResponse.HAM
    )


async def test_submit_ham(akismet_end_to_end_kwargs: dict, akismet_ham_role: str):
    """
    submit_ham() returns True when Akismet accepts the submission.

    """
    client = akismet.AsyncClient()
    assert await client.submit_ham(
        comment_content="test", user_role=akismet_ham_role, **akismet_end_to_end_kwargs
    )


async def test_submit_spam(akismet_end_to_end_kwargs: dict, akismet_spam_author: str):
    """
    submit_spam() returns True when Akismet accepts the submission.

    """
    client = akismet.AsyncClient()
    assert await client.submit_spam(
        comment_content="test",
        comment_author=akismet_spam_author,
        **akismet_end_to_end_kwargs,
    )
