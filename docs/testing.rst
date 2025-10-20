.. _testing:

Testing guide
=============


Testing your use of ``akismet``
-------------------------------

The recommended way to test your use of ``akismet`` is with one of the included
:ref:`test clients <test-clients>`. They implement the full API of the corresponding
real clients, but do not make live HTTP requests to the Akismet web service. They also
are configurable to allow testing important behaviors which your own code using
``akismet`` will need to handle:

* Marking content as spam or as not spam

* Rejecting an API key/URL as invalid

The test clients are configured by subclassing and setting attributes on the subclass:

* Setting the attribute ``comment_check_response`` to a :class:`~akismet.CheckResponse`
  enum value will cause the comment-check operation to always return that value,
  allowing you to test spam, non-spam and "blatant spam" responses.

* Setting the attribute ``verify_key_response`` to a :class:`bool` will cause the
  verify-key operation to always return that value, allowing you to test for the case of
  both valid and invalid keys. Setting to :data:`False` will also cause the
  ``validated_client()`` alternate constructor to raise :exc:`~akismet.APIKeyError`,
  allowing you to test your handling of that situation.

See :ref:`the test client documentation <test-clients>` for details.


.. _pytest-plugin:

Using the pytest plugin
~~~~~~~~~~~~~~~~~~~~~~~

If you're using `pytest <https://docs.pytest.org/>`_, ``akismet`` includes a pytest
plugin which provides the test clients as fixtures:

* ``akismet_async_client``: An instance of the async test client.

* ``akismet_sync_client``: An instance of the sync test client.

* ``akismet_async_class``: The class object for the async test client.

* ``akismet_sync_class``: The class object for the sync test client.

By default, these will succeed at key verification and will mark all content as spam. To
configure the behavior, you can apply the pytest mark ``akismet_client``, with arguments
``comment_check_response`` (which should be a value from the
:class:`~akismet.CheckResponse` enum), and/or ``verify_key_response`` (which should be a
:class:`bool`). For example:

.. tab:: Sync

   .. code-block:: python

      import akismet
      import pytest

      @pytest.mark.akismet_client(comment_check_response=akismet.CheckResponse.DISCARD)
      def test_akismet_discard_response(akismet_sync_client: akismet.SyncClient):
          # Inside this test, akismet_sync_client's comment_check() will always
          # return CheckResponse.DISCARD.

      @pytest.mark.akismet_client(verify_key_response=False)
      def test_akismet_fails_key_verification(akismet_sync_class: type[akismet.SyncClient]):
          # The key verification will always fail on this class.
          with pytest.raises(akismet.APIKeyError):
              akismet_sync_class.validated_client()

.. tab:: Async

   .. code-block:: python

      import akismet
      import pytest

      @pytest.mark.akismet_client(comment_check_response=akismet.CheckResponse.DISCARD)
      async def test_akismet_discard_response(akismet_async_client: akismet.ASyncClient):
          # Inside this test, akismet_async_client's comment_check() will always
          # return CheckResponse.DISCARD.

      @pytest.mark.akismet_client(verify_key_response=False)
      async def test_akismet_fails_key_verification(akismet_async_class: type[akismet.ASyncClient]):
          # Key verification will always fail on this class and on all instances
          # of it.
          with pytest.raises(akismet.APIKeyError):
              await akismet_async_class.validated_client()

As a general guideline, request the client class fixtures when you want to test key
verification handling in your own code, or when you're using some testing pattern which
will construct instances on demand from the class, and otherwise always request a client
instance fixture.

Testing with ``unittest``
~~~~~~~~~~~~~~~~~~~~~~~~~

If you use the Python standard library's ``unittest`` module, or another test setup
derived from it (such as Django's testing tools), you can create and use test client
classes directly in your tests.

For example:

.. tab:: Sync

   .. code-block:: python

      import akismet


      class AlwaysSpam(akismet.TestSyncClient):
         """
         This client's comment_check() always returns SPAM.

         """
         comment_check_response = akismet.CheckResponse.SPAM


      class AlwaysBlatantSpam(akismet.TestSyncClient):
         """
         This client's comment_check() always returns DISCARD.

         """
         comment_check_response = akismet.CheckResponse.DISCARD


      class NeverSpam(akismet.TestSyncClient):
         """
         This client's comment_check() always returns HAM.

         """
         comment_check_response = akismet.CheckResponse.HAM


      class AlwaysValid(akismet.TestSyncClient):
         """
         This client's verify_key() always returns True.

         """
         verify_key_response = True


      class NeverValid(akismet.TestSyncClient):
         """
         This client's verify_key() always returns False.

         """
         verify_key_response = False


.. tab:: Async

   .. code-block:: python

      import akismet


      class AlwaysSpam(akismet.TestAsyncClient):
         """
         This client's comment_check() always returns SPAM.

         """
         comment_check_response = akismet.CheckResponse.SPAM


      class AlwaysBlatantSpam(akismet.TestAsyncClient):
         """
         This client's comment_check() always returns DISCARD.

         """
         comment_check_response = akismet.CheckResponse.DISCARD


      class NeverSpam(akismet.TestAsyncClient):
         """
         This client's comment_check() always returns HAM.

         """
         comment_check_response = akismet.CheckResponse.HAM


      class AlwaysValid(akismet.TestAsyncClient):
         """
         This client's verify_key() always returns True.

         """
         verify_key_response = True


      class NeverValid(akismet.TestAsyncClient):
         """
         This client's verify_key() always returns False.

         """
         verify_key_response = False


Testing against the live Akismet service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you also want to perform live end-to-end testing of your use of Akismet, you can do
so with a real Akismet API client, by passing the optional keyword argument
``is_test=1`` to the comment-check, submit-ham, and submit-spam operations; this tells
Akismet that you are only issuing requests for testing purposes, and will not result in
any submissions being incorporated into Akismet's training corpus. Additionally, the
Akismet web service supports certain special values for use in triggering specific
responses:

* Passing ``comment_author="akismet-guaranteed-spam"`` to the comment-check operation
  will always cause Akismet to mark the content as spam.

* Passing ``user_role="administrator"`` to the comment-check operation will always cause
  Akismet to mark the content as not spam.

In the provided pytest plugin, these values are available as the pytest fixtures
``akismet_spam_author`` and ``akismet_spam_role``.

However, it is generally discouraged to make live requests to an external service as
part of a normal test suite. For most cases you should be making use of the included
test clients.


Running this library's tests
----------------------------

A standard install of ``akismet`` does not install the test suite; you will need to
perform :ref:`a source checkout as described in the installation guide
<source-install>`.

``akismet``'s testing tasks are run using `nox <https://nox.thea.codes/>`_, so you will
also need to install it, after which you can run ``nox``, which should be done from the
root of your git checkout of ``akismet``:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install --upgrade nox
      python -m nox

.. tab:: Windows

   .. code-block:: shell

      py -m pip install --upgrade nox
      py -m nox

Note that to run the full test matrix you will need to have each supported version of
Python available. To run only the subset of test tasks for a specific Python version,
pass the ``--python`` flag with a version number. For example, to run tasks for Python
3.10 only, you could run:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --python "3.10"

.. tab:: Windows

   .. code-block:: shell

      py -m nox --python "3.10"

By default, ``nox`` will only run the tasks whose associated Python versions are
available on your system. For example, if you have only Python 3.10 and 3.13 installed,
test runs for Python 3.11, 3.12, and 3.14 would be skipped.

To see a list of all available test tasks, run:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --list

.. tab:: Windows

   .. code-block:: shell

      py -m nox --list

All test tasks defined for ``akismet`` are also categorized with tags, which ``nox``
understands and can use. For example, to run just the standard unit-test suite and no
other tasks:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox -t tests

.. tab:: Windows

   .. code-block:: shell

      py -m nox -t tests

Other useful tags are: ``docs`` (documentation build and checks); ``formatters``
(code-formatting checks); ``linters`` (code linters); ``security`` (security checks);
and ``packaging`` (tests for the packaging configuration and build).

The test suite makes significant use of custom HTTP clients, relying on the ``httpx``
package's `mock HTTP transport
<https://www.python-httpx.org/advanced/#mock-transports>`_ to generate test responses
without needing to contact the live Akismet web service, so setting the environment
variables for your Akismet API key and site URL is not necessary to run the normal test
suite.

However, there is a separate test file--found at ``tests/end_to_end.py``--which is not
run as part of the usual test suite invoked by ``nox`` and which makes live requests to
Akismet. Running the tests in that file *does* require setting the
``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL`` environment variables to
valid values, after which you can run the end-to-end tests by invoking ``nox`` and
asking it to run tasks with the keyword ``release`` (normally this test file is only run
as a final check prior to issuing a new release, hence the keyword name):

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --keyword release

.. tab:: Windows

   .. code-block:: shell

      py -m nox --keyword release

If you also want to manually perform your own tests, you can instantiate an Akismet
client class and call its methods to communicate with the live Akismet web service. As
mentioned above, it is recommended that you pass the optional keyword argument
``is_test=1`` to the comment-check, submit-ham, and submit-spam operations; this tells
the Akismet web service that you are only issuing requests for testing purposes, and
will not result in any submissions being incorporated into Akismet's training corpus.
