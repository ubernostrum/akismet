"""
Tests for the async client's constructor behavior.

"""

import pytest

import akismet
from akismet import _common

pytestmark = [pytest.mark.anyio, pytest.mark.async_client, pytest.mark.constructors]


async def test_construct_config_explicit(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    Passing explicit config to the async default constructor uses that config.

    """
    config = akismet.Config(key="invalid-test-key", url=akismet_config.url)
    async with akismet_async_class(config=config) as client:
        assert client._config == config


async def test_construct_config_alternate_constructor_explicit(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    Passing explicit config to the alternate constructor uses that config.

    """
    config = akismet.Config(key="other-invalid-test-key", url=akismet_config.url)
    client = await akismet_async_class.validated_client(config=config)
    assert client._config == config


async def test_construct_config_from_env(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    Instantiating via the async default constructor, without passing explicit config,
    reads the config from the environment.

    """
    async with akismet_async_class() as client:
        assert client._config == akismet_config


async def test_construct_alternate_constructor_config_from_env(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    Instantiating via the alternate constructor, without passing explicit config, reads
    the config from the environment.

    """
    client = await akismet_async_class.validated_client()
    assert client._config == akismet_config


async def test_construct_config_valid(akismet_async_class: type[akismet.AsyncClient]):
    """
    With a valid configuration, constructing a client succeeds.

    """
    await akismet_async_class.validated_client()


@pytest.mark.akismet_client(verify_key_response=False)
async def test_construct_config_invalid_key(
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    With an invalid API key, constructing a client raises an APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        await akismet_async_class.validated_client()


async def test_construct_config_valid_context_manager(
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    With a valid configuration, constructing a client as a context manager succeeds.

    """
    async with akismet_async_class():
        pass


@pytest.mark.akismet_client(verify_key_response=False)
async def test_construct_config_invalid_key_context_manager(
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    With an invalid API key, constructing a client as a context manager raises an
    APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        async with akismet_async_class():
            pass


async def test_construct_config_valid_explicit(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    With an explicit valid configuration, constructing a client succeeds.

    """
    await akismet_async_class.validated_client(config=akismet_config)


@pytest.mark.akismet_client(verify_key_response=False)
async def test_construct_config_invalid_key_explicit(
    akismet_config: akismet.Config, akismet_async_class: type[akismet.AsyncClient]
):
    """
    With an explicit invalid API key, constructing a client raises an APIKeyError.

    """
    with pytest.raises(akismet.APIKeyError):
        await akismet_async_class.validated_client(config=akismet_config)


async def test_construct_config_bad_url(
    monkeypatch: pytest.MonkeyPatch, akismet_async_class: type[akismet.AsyncClient]
):
    """
    With an invalid URL, constructing a client raises a ConfigurationError.

    """
    monkeypatch.setenv(_common._URL_ENV_VAR, "ftp://example.com")
    with pytest.raises(akismet.ConfigurationError):
        await akismet_async_class.validated_client()


async def test_construct_config_missing_key(
    monkeypatch: pytest.MonkeyPatch,
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    Without an API key present, constructing a client raises a ConfigurationError.

    """
    monkeypatch.delenv(_common._KEY_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        await akismet_async_class.validated_client()


async def test_construct_config_missing_url(
    monkeypatch: pytest.MonkeyPatch,
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    Without a registered site URL present, constructing a client raises a
    ConfigurationError.

    """
    monkeypatch.delenv(_common._URL_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        await akismet_async_class.validated_client()


async def test_construct_config_missing_all(
    monkeypatch: pytest.MonkeyPatch,
    akismet_async_class: type[akismet.AsyncClient],
):
    """
    Without any config present, constructing a client raises a ConfigurationError.

    """
    monkeypatch.delenv(_common._KEY_ENV_VAR)
    monkeypatch.delenv(_common._URL_ENV_VAR)
    with pytest.raises(akismet.ConfigurationError):
        await akismet_async_class.validated_client()


async def test_construct_default_client():
    """
    Constructing a client without an explicit HTTP client uses the async default HTTP
    client.

    """
    client = akismet.AsyncClient()
    http_client = client._http_client
    assert "user-agent" in http_client.headers
    assert http_client.headers["user-agent"] == _common.USER_AGENT
