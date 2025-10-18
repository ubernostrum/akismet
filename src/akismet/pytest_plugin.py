"""
Pytest plugin supplying markers and fixtures to assist in testing code which uses the
Akismet clients.

"""

import pytest

from . import AsyncClient, CheckResponse, SyncClient, TestAsyncClient, TestSyncClient

# pylint: disable=redefined-outer-name


def _get_mark_arguments(request: pytest.FixtureRequest) -> tuple[CheckResponse, bool]:
    """
    Collect and return the arguments for construction of an Akismet test client, from
    pytest mark configuration if set or from defaults if not.

    """
    comment_check_response = CheckResponse.SPAM
    verify_key_response = True
    if marker := request.node.get_closest_marker("akismet_client"):
        comment_check_response = marker.kwargs.get(
            "comment_check_response", comment_check_response
        )
        verify_key_response = marker.kwargs.get(
            "verify_key_response", verify_key_response
        )
    return comment_check_response, verify_key_response


@pytest.fixture
def akismet_sync_class(request: pytest.FixtureRequest) -> type[TestSyncClient]:
    """
    A synchronous Akismet test client class.

    Use this fixture if you need the actual class itself (for example, to register with
    dependency injection tool which will instantiate it for you). If you just want an a
    client instance to use directly, use the akismet_sync_client fixture instead.

    By default, this will return a class whose verify_key() method always returns True,
    and whose comment_check() method always returns akismet.CheckResponse.SPAM. To
    change this, use the pytest mark akismet_client on your test, and pass either or
    both of the following keyword arguments:

    * comment_check_response: an akismet.CheckResponse which will be used as the return
      value of the comment_check() method.

    * verify_key_response: a bool which will be used as the return value of the
      verify_key() method.

    """
    _comment_check_response, _verify_key_response = _get_mark_arguments(request)

    class _SyncClient(TestSyncClient):
        """
        Test Akismet client.

        """

        comment_check_response = _comment_check_response
        verify_key_response = _verify_key_response

    return _SyncClient


@pytest.fixture
def akismet_async_class(request: pytest.FixtureRequest) -> type[TestAsyncClient]:
    """
    An asynchronous Akismet test client class.

    Use this fixture if you need the actual class itself (for example, to register with
    dependency injection tool which will instantiate it for you). If you just want an a
    client instance to use directly, use the akismet_async_client fixture instead.

    By default, this will return a class whose verify_key() method always returns True,
    and whose comment_check() method always returns akismet.CheckResponse.SPAM. To
    change this, use the pytest mark akismet_client on your test, and pass either or
    both of the following keyword arguments:

    * comment_check_response: an akismet.CheckResponse which will be used as the return
      value of the comment_check() method.

    * verify_key_response: a bool which will be used as the return value of the
      verify_key() method.

    """
    _comment_check_response, _verify_key_response = _get_mark_arguments(request)

    class _AsyncClient(TestAsyncClient):
        """
        Test Akismet client.

        """

        comment_check_response = _comment_check_response
        verify_key_response = _verify_key_response

    return _AsyncClient


@pytest.fixture
def akismet_sync_client(akismet_sync_class: type[SyncClient]) -> SyncClient:
    """
    A synchronous Akismet test client instance.

    Use this fixture if you just need a client instance to usedirectly. If you instead
    need the client class (for example, to register with a dependency injection system
    which will instantiate it for you), use the akismet_sync_class fixture instead.

    By default, this will return a client whose verify_key() method always returns True,
    and whose comment_check() method always returns akismet.CheckResponse.SPAM. To change
    this, use the pytest mark akismet_client on your test, and pass either or both of the
    following keyword arguments:

    * comment_check_response: an akismet.CheckResponse which will be used as the return
      value of the comment_check() method.

    * verify_key_response: a bool which will be used as the return value of the
      verify_key() method.

    """
    return akismet_sync_class()


@pytest.fixture
def akismet_async_client(akismet_async_class: type[AsyncClient]) -> AsyncClient:
    """
    An asynchronous Akismet test client instance.

    Use this fixture if you just need a client instance to usedirectly. If you instead
    need the client class (for example, to register with a dependency injection system
    which will instantiate it for you), use the akismet_async_class fixture instead.

    By default, this will return a client whose verify_key() method always returns True,
    and whose comment_check() method always returns akismet.CheckResponse.SPAM. To change
    this, use the pytest mark akismet_client on your test, and pass either or both of the
    following keyword arguments:

    * comment_check_response: an akismet.CheckResponse which will be used as the return
      value of the comment_check() method.

    * verify_key_response: a bool which will be used as the return value of the
      verify_key() method.
    """
    return akismet_async_class()


@pytest.fixture
def akismet_ham_role() -> str:  # pragma: no cover
    """
    Return a user_role value which Akismet always considers to be non-spam.

    """
    return "administrator"


@pytest.fixture
def akismet_spam_author() -> str:  # pragma: no cover
    """
    Return a comment_author value which Akismet always considers to be spam.

    """
    return "akismet-guaranteed-spam"


def pytest_configure(config: pytest.Config):
    """
    Register custom markers.

    """
    config.addinivalue_line(
        "markers",
        "akismet_client: Configure the Akismet test client fixtures.",
    )
