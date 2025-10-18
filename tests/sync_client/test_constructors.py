"""
Tests for the sync client's constructor behavior.

"""

import pytest

import akismet
from akismet import _common

pytestmark = [pytest.mark.constructors, pytest.mark.sync_client]


def test_construct_config_explicit(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Passing explicit config to the default constructor uses that config.

    """
    config = akismet.Config(key="invalid-test-key", url=akismet_config.url)
    with akismet_sync_class(config=config) as client:
        assert client._config == config


def test_construct_config_alternate_constructor_explicit(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Passing explicit config to the alternate constructor uses that config.

    """
    config = akismet.Config(key="other-invalid-test-key", url=akismet_config.url)
    client = akismet_sync_class.validated_client(config=config)
    assert client._config == config


def test_construct_config_from_env(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Instantiating via the default constructor, without passing explicit config,
    reads the config from the environment.

    """
    with akismet_sync_class() as client:
        assert client._config == akismet_config


def test_construct_alternate_constructor_config_from_env(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Instantiating via the alternate constructor, without passing explicit config, reads
    the config from the environment.

    """
    client = akismet_sync_class.validated_client()
    assert client._config == akismet_config


def test_construct_config_valid(akismet_sync_class: type[akismet.SyncClient]):
    """
    With a valid configuration, constructing a client succeeds.

    """
    akismet_sync_class.validated_client()


@pytest.mark.akismet_client(verify_key_response=False)
def test_construct_config_invalid_key(akismet_sync_class: type[akismet.SyncClient]):
    """
    With an invalid API key, constructing a client raises an APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        akismet_sync_class.validated_client()


def test_construct_config_valid_context_manager(
    akismet_sync_class: type[akismet.SyncClient],
):
    """
    With a valid configuration, constructing a client as a context manager succeeds.

    """
    with akismet_sync_class():
        pass


@pytest.mark.akismet_client(verify_key_response=False)
def test_construct_config_invalid_key_context_manager(
    akismet_sync_class: type[akismet.SyncClient],
):
    """
    With an invalid API key, constructing a client as a context manager raises an
    APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        with akismet_sync_class():
            pass


def test_construct_config_valid_explicit(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    With an explicit valid configuration, constructing a client succeeds.

    """
    akismet_sync_class.validated_client(config=akismet_config)


@pytest.mark.akismet_client(verify_key_response=False)
def test_construct_config_invalid_key_explicit(
    akismet_config: akismet.Config, akismet_sync_class: type[akismet.SyncClient]
):
    """
    With an explicit invalid API key, constructing a client raises an APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        akismet_sync_class.validated_client(config=akismet_config)


def test_construct_config_bad_url(
    monkeypatch: pytest.MonkeyPatch, akismet_sync_class: type[akismet.SyncClient]
):
    """
    With an invalid URL, constructing a client raises a ConfigurationError.

    """
    monkeypatch.setenv(_common._URL_ENV_VAR, "ftp://example.com")
    with pytest.raises(akismet.ConfigurationError):
        akismet_sync_class.validated_client()


def test_construct_config_missing_key(
    monkeypatch: pytest.MonkeyPatch, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Without an API key present, constructing a client raises a ConfigurationError.

    """
    monkeypatch.delenv(_common._KEY_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        akismet_sync_class.validated_client()


def test_construct_config_missing_url(
    monkeypatch: pytest.MonkeyPatch, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Without a registered site URL present, constructing a client raises a
    ConfigurationError.

    """
    monkeypatch.delenv(_common._URL_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        akismet_sync_class.validated_client()


def test_construct_config_missing_all(
    monkeypatch: pytest.MonkeyPatch, akismet_sync_class: type[akismet.SyncClient]
):
    """
    Without any config present, constructing a client raises a ConfigurationError.

    """
    monkeypatch.delenv(_common._KEY_ENV_VAR)
    monkeypatch.delenv(_common._URL_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        akismet_sync_class.validated_client()


def test_construct_default_client():
    """
    Constructing a client without an explicit HTTP client uses the default HTTP client.

    """
    client = akismet.SyncClient()
    http_client = client._http_client
    assert "user-agent" in http_client.headers
    assert http_client.headers["user-agent"] == _common.USER_AGENT
