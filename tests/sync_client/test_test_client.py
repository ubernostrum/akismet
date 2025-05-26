"""
Tests for the sync test client.

"""

import pytest

import akismet

pytestmark = [pytest.mark.sync_client, pytest.mark.test_client]


def test_comment_check_default_not_spam(
    akismet_config: akismet.Config, akismet_common_kwargs: dict
):
    """
    The default configuration of the test client marks all content as non-spam.

    """
    client = akismet.TestSyncClient(config=akismet_config)
    assert (
        client.comment_check(comment_content="Test", **akismet_common_kwargs)
        == akismet.CheckResponse.HAM
    )


@pytest.mark.parametrize("response_value", list(akismet.CheckResponse))
def test_comment_check_configuration(
    akismet_config: akismet.Config,
    akismet_common_kwargs: dict,
    response_value: akismet.CheckResponse,
):
    """
    Setting comment_check_response explicitly will cause the test client to mark content
    accordingly.

    """

    class _Client(akismet.TestSyncClient):
        """
        Test client with explicit comment_check_response.

        """

        comment_check_response = response_value

    client = _Client(config=akismet_config)
    assert (
        client.comment_check(comment_content="Test", **akismet_common_kwargs)
        == response_value
    )


def test_verify_key_default(akismet_config: akismet.Config):
    """
    The default configuration of the test client succeeds at key verification.

    """
    client = akismet.TestSyncClient(config=akismet_config)
    assert client.verify_key()


def test_verify_key_explicit_success(akismet_config: akismet.Config):
    """
    Setting verify_key_response explicitly to True will cause the test client to succeed
    at key verification.

    """

    class _Client(akismet.TestSyncClient):
        """
        Test client with explicit verify_key_response.

        """

        verify_key_response = True

    # Explicit configuration succeeds.
    client = _Client(config=akismet_config)
    assert client.verify_key()

    # Implicit configuration succeeds.
    _Client.validated_client()


def test_verify_key_explicit_failure(akismet_config: akismet.Config):
    """
    Setting verify_key_response explicitly to False will cause the test client to fail
    at key verification.

    """

    class _Client(akismet.TestSyncClient):
        """
        Test client with explicit verify_key_response.

        """

        verify_key_response = False

    # Explicit configuration fails.
    client = _Client(config=akismet_config)
    assert not client.verify_key()

    # Implicit configuration fails.
    with pytest.raises(akismet.APIKeyError):
        _Client.validated_client()
