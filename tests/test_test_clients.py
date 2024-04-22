"""
Tests for the Akismet test clients.

"""

from akismet import APIKeyError, CheckResponse, TestAsyncClient, TestSyncClient

from .base import AkismetTests, AsyncAkismetTests


class SyncTestClientTests(AkismetTests):
    """
    Tests for the synchronous Akismet test client.

    """

    def test_comment_check_default_not_spam(self):
        """
        The default configuration of the test client marks all content as non-spam.

        """
        client = TestSyncClient(config=self.config)
        assert (
            client.comment_check(comment_content="Test", **self.common_kwargs)
            == CheckResponse.HAM
        )

    def test_comment_check_configuration(self):
        """
        Setting comment_check_response explicitly will cause the test client to mark
        content accordingly.

        """
        for response_value in CheckResponse:
            with self.subTest(comment_check_response=response_value):

                class _Client(TestSyncClient):
                    """
                    Test client with explicit comment_check_response.

                    """

                    comment_check_response = response_value

                client = _Client(config=self.config)
                assert (
                    client.comment_check(comment_content="Test", **self.common_kwargs)
                    == response_value
                )

    def test_verify_key_default(self):
        """
        The default configuration of the test client succeeds at key verification.

        """
        client = TestSyncClient(config=self.config)
        assert client.verify_key()

    def test_verify_key_explicit_success(self):
        """
        Setting verify_key_response explicitly to True will cause the test client to
        succeed at key verification.

        """

        class _Client(TestSyncClient):
            """
            Test client with explicit verify_key_response.

            """

            verify_key_response = True

        # Explicit configuration succeeds.
        client = _Client(config=self.config)
        assert client.verify_key()

        # Implicit configuration succeeds.
        _Client.validated_client()

    def test_verify_key_explicit_failure(self):
        """
        Setting verify_key_response explicitly to False will cause the test client
        to fail at key verification.

        """

        class _Client(TestSyncClient):
            """
            Test client with explicit verify_key_response.

            """

            verify_key_response = False

        # Explicit configuration fails.
        client = _Client(config=self.config)
        assert not client.verify_key()

        # Implicit configuration fails.
        with self.assertRaises(APIKeyError):
            _Client.validated_client()


class AsyncTestClientTests(AsyncAkismetTests):
    """
    Tests for the asynchronous Akismet test client.

    """

    async def test_comment_check_default_not_spam(self):
        """
        The default configuration of the test client marks all content as non-spam.

        """
        client = TestAsyncClient(config=self.config)
        assert (
            await client.comment_check(comment_content="Test", **self.common_kwargs)
            == CheckResponse.HAM
        )

    async def test_comment_check_configuration(self):
        """
        Setting comment_check_response explicitly will cause the test client to mark
        content accordingly.

        """
        for response_value in CheckResponse:
            with self.subTest(comment_check_response=response_value):

                class _Client(TestAsyncClient):
                    """
                    Test client with explicit comment_check_response.

                    """

                    comment_check_response = response_value

                client = _Client(config=self.config)
                assert (
                    await client.comment_check(
                        comment_content="Test", **self.common_kwargs
                    )
                    == response_value
                )

    async def test_verify_key_default(self):
        """
        The default configuration of the test client succeeds at key verification.

        """
        client = TestAsyncClient(config=self.config)
        assert await client.verify_key()

    async def test_verify_key_explicit_success(self):
        """
        Setting verify_key_response explicitly to True will cause the test client to
        succeed at key verification.

        """

        class _Client(TestAsyncClient):
            """
            Test client with explicit verify_key_response.

            """

            verify_key_response = True

        # Explicit configuration succeeds.
        client = _Client(config=self.config)
        assert await client.verify_key()

        # Implicit configuration succeeds.
        await _Client.validated_client()

    async def test_verify_key_explicit_failure(self):
        """
        Setting verify_key_response explicitly to False will cause the test client
        to fail at key verification.

        """

        class _Client(TestAsyncClient):
            """
            Test client with explicit verify_key_response.

            """

            verify_key_response = False

        # Explicit configuration fails.
        client = _Client(config=self.config)
        assert not await client.verify_key()

        # Implicit configuration fails.
        with self.assertRaises(APIKeyError):
            await _Client.validated_client()
