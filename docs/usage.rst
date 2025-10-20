.. _usage:


Usage guide
===========

To use ``akismet``, you will need to obtain an Akismet API key and register a site for
use with the Akismet web service; you can do this at <https://akismet.com>. Once you
have a key and corresponding registered site URL to use with it, place them in the
environment variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``, and
they will be automatically detected and used.

You can also optionally set the environment variable ``PYTHON_AKISMET_TIMEOUT`` to a
:class:`float` or :class:`int` containing a connection-timeout threshold to use for
making requests to the Akismet web service; if not set, this will default to ``1.0``
(one second).


Using the Akismet clients
-------------------------

Once you have a key and registered site, and have set the environment variables, you can
create an Akismet API client. Two are available, one being synchronous (blocking I/O),
and the other asynchronous (non-blocking I/O).

.. admonition:: **Asynchronous Python**

   Most Python applications are synchronous, and cannot easily run async code (which
   requires an event loop and slightly different syntax to call functions/methods). So
   you'll probably want to use the synchronous Akismet client unless your entire
   application is already async (most commonly, this will be when you have an
   asynchronous web application built with an async framework like FastAPI or Litestar).

   And if you're not sure what all this means, you *definitely* want the synchronous
   Akismet client.


API client creation and basic use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally you will want to create your client in a way which automatically validates
your API key at client instantiation. You can do this in either of two ways:

* Call the ``validated_client()`` constructor method (see :ref:`the FAQ
  <alt-constructor>` for an explanation of why this is done through an alternate
  constructor), or

* Create your client as a context manager

To use the ``validated_client()`` constructor, simply call it. With no arguments, it
will read your Akismet API key and site URL from the environment variables, and will
raise an :exc:`akismet.ConfigurationError` exception if they're not found or not valid.

.. tab:: Sync

   .. code-block:: python

      import akismet

      akismet_client = akismet.SyncClient.validated_client()

.. tab:: Async

   .. code-block:: python

      import akismet

      akismet_client = await akismet.AsyncClient.validated_client()


If don't want to or can't set the environment variables you can use a
:class:`~akismet.Config` instance and use that to manually configure your Akismet API
client:

.. tab:: Sync

   .. code-block:: python

      import akismet

      config = akismet.Config(key=your_api_key, url=your_site_url)
      akismet_client = akismet.SyncClient.validated_client(config=config)

.. tab:: Async

   .. code-block:: python

      import akismet

      config = akismet.Config(key=your_api_key, url=your_site_url)
      akismet_client = await akismet.AsyncClient.validated_client(config=config)

The most important operation of the Akismet client is checking a piece of content to see
if it's spam. This is done with the ``comment_check()`` method. There's one required
argument -- the IP address of the user who submitted the content -- but `a large number
of optional arguments <https://akismet.com/developers/comment-check/>`_ are also
accepted. It's recommended that you include as much information as possible to help
Akismet make accurate determinations, but at the very least you should pass the
following arguments:

* ``comment_content`` -- The actual content that was submitted.

* ``comment_type`` -- The type of content. Common values for this are ``"comment"``,
  ``"forum-post"``, ``"contact-form"``, and ``"signup"``, but you can also pass other
  values depending on the type of user-submitted content you're dealing with.

* ``comment_author`` and/or ``comment_author_email`` -- The identifier (such as a
  username) and/or the email address of the user who submitted the content.

For example, suppose you're using `the Django web framework
<https://www.djangoproject.com>`_ to build an online forum. You might write a Django
view for submitting new forum posts that looks like this (using the API client created
above):

.. tab:: Sync

   .. code-block:: python

      def new_post(request):
          """
          HTTP handler for a new forum post.

          """
          if akismet_client.comment_check(
              user_ip=request.META["REMOTE_ADDR"],
              comment_type="forum_post",
              comment_content=request.POST["post_body"],
              comment_author=request.user.username,
          ):
              # The post was spam, reject it.
          else:
              # The post wasn't spam, allow it.

.. tab:: Async

   .. code-block:: python

      async def new_post(request):
          """
          HTTP handler for a new forum post.

          """
          if await akismet_client.comment_check(
              user_ip=request.META["REMOTE_ADDR"],
              comment_type="forum_post",
              comment_content=request.POST["post_body"],
              comment_author=request.user.username,
          ):
              # The post was spam, reject it.
          else:
              # The post wasn't spam, allow it.


As a context manager
~~~~~~~~~~~~~~~~~~~~

You can also use either client as a context manager. When doing so, you do *not* need to
use the ``validated_client()`` constructor; the context manager will automatically
validate the configuration for you as soon as the ``with`` block is entered.

.. tab:: Sync

   .. code-block:: python

      import akismet

      with akismet.SyncClient() as akismet_client:
          # Use the client instance here. It will be automatically cleaned up
          # when the "with" block is exited.

.. tab:: Async

   .. code-block:: python

      import akismet

      async with akismet.AsyncClient() as akismet_client:
          # Use the client instance here. It will be automatically cleaned up
          # when the "with" block is exited.

As with the ``validated_client()`` method, you can explicitly pass a
:class:`~akismet.Config` instance to the constructor to manually supply the API key and
site URL.


Detecting "blatant" spam
~~~~~~~~~~~~~~~~~~~~~~~~

The examples above showed spam detection as an either/or check -- either something is
spam, or it's not. But Akismet actually supports *three* possible states: "not spam",
"spam", and "blatant spam". One way you could use this is to add a manual review step:
if something is marked as "not spam" it's allowed to post normally, "spam" goes into a
review queue for you to look at, and "blatant spam" is just rejected without any further
review.

You can implement this by looking at the return value of the ``comment_check()`` method,
which is actually an enum -- :class:`akismet.CheckResponse` -- with three possible
values. So you could adapt the example of ``comment_check()`` above to do this:


.. tab:: Sync

   .. code-block:: python

      from akismet import CheckResponse

      def new_post(request):
          """
          HTTP handler for a new forum post.

          """
          classification = akismet_client.comment_check(
              user_ip=request.META["REMOTE_ADDR"],
              comment_type="forum_post",
              comment_content=request.POST["post_body"],
              comment_author=request.user.username,
          )

          if classification == CheckResponse.DISCARD:
              # The post was "blatant" spam, reject it.
          elif classification == CheckResponse.SPAM:
              # Send it into the manual-review queue.
          elif classification == CheckResponse.HAM:
              # The post wasn't spam, allow it.

.. tab:: Async

   .. code-block:: python

      from akismet import CheckResponse

      async def new_post(request):
          """
          HTTP handler for a new forum post.

          """
          classification = await akismet_client.comment_check(
              user_ip=request.META["REMOTE_ADDR"],
              comment_type="forum_post",
              comment_content=request.POST["post_body"],
              comment_author=request.user.username,
          )

          if classification == CheckResponse.DISCARD:
              # The post was "blatant" spam, reject it.
          elif classification == CheckResponse.SPAM:
              # Send it into the manual-review queue.
          elif classification == CheckResponse.HAM:
              # The post wasn't spam, allow it.

This works because the :class:`~akismet.CheckResponse` enum uses integer values; when
fed directly to an ``if``/``else``, they work as boolean values (``HAM`` is ``0``,
``SPAM`` is ``1``, and ``DISCARD`` is ``2``).


Using a custom HTTP client
~~~~~~~~~~~~~~~~~~~~~~~~~~

For some use cases, you may need custom HTTP client behavior. For example, you might be
running on a server which has to use an HTTP proxy to access any external service. In
that case, you can pass a custom HTTP client to the Akismet API client, as the
constructor argument ``http_client``. The Akismet API clients use `the Python HTTPX
library <https://www.python-httpx.org>`_ (which is automatically installed when you
install ``akismet``) for their HTTP clients, so you can create either an
``httpx.Client`` or an ``httpx.AsyncClient`` with the behavior you want.

You should also make sure to set a value for the ``User-Agent`` header of your custom
HTTP client. If you want the default value the Akismet clients would use, it's available
as :data:`akismet.USER_AGENT`.


.. tab:: Sync

   .. code-block:: python

      import akismet
      import httpx

      from your_app.config import settings

      akismet_client = akismet.SyncClient.validated_client(
          http_client=httpx.Client(
              proxy=settings.PROXY_URL,
              headers={"User-Agent": akismet.USER_AGENT}
          )
      )

.. tab:: Async

   .. code-block:: python

      import akismet
      import httpx

      from your_app.config import settings

      akismet_client = await akismet.AsyncClient.validated_client(
          http_client=httpx.AsyncClient(
              proxy=settings.PROXY_URL,
              headers={"User-Agent": akismet.USER_AGENT}
          )
      )

Finally, note that if all you want is to set a custom timeout value for connections to
the Akismet web service, you do not need a custom HTTP client; you can set the
environment variable ``PYTHON_AKISMET_TIMEOUT`` as described above.


.. _usage-testing:

Testing your use of ``akismet``
-------------------------------

While you *can* perform limited end-to-end testing of Akismet's spam-checking if you
want to (see :ref:`the testing guide <testing>` for details), in general it's
discouraged to make live requests to external services as part of a normal application
test suite.

It's also generally discouraged to build extensive :mod:`unittest.mock` representations
of code that isn't under your control; this often leads to over-complicated test setups
and a high maintenance burden as you attempt to keep your mocks in sync with what a
third-party library is doing.

So ``akismet`` provides two test clients intended to be used in your application's
tests: :class:`~akismet.TestAsyncClient` as a test version of
:class:`~akismet.AsyncClient`, and :class:`~akismet.TestSyncClient` as a test version of
:class:`~akismet.SyncClient`.

Both of these test classes implement the full API of their real counterparts, but they
do *not* make actual requests to the Akismet web service. You can configure them by
subclassing and setting attributes to simulate content being marked as spam/not-spam and
also to simulate an invalid API key. For example, you might write a simple spam-flagging
function which toggles an attribute on a submitted comment:

.. code-block:: python

   def flag_spam_comment(akismet_client, request, comment):
       """
       If the submitted content is marked as spam by Akismet, set it to
       have filtered=True.

       """
       if akismet_client.comment_check(
           user_ip=request.META["REMOTE_ADDR"],
           comment_type="comment",
           comment_content=comment.body,
           comment_author=request.user.username,
       ):
           comment.filtered = True
       return comment

And then test it like so:

.. tab:: unittest

   .. code-block:: python

      import unittest

      import akismet

      from your_app.moderation import flag_spam_comment
      from your_app.test_factories import make_test_request, make_test_comment


      class AlwaysSpam(akismet.TestSyncClient):
          """
          An Akismet client whose comment_check() always returns SPAM.

          """
          comment_check_response = akismet.CheckResponse.SPAM


      class NeverSpam(akismet.TestSyncClient):
          """
          An Akismet client whose comment_check() always returns HAM.

          """
          comment_check_response = akismet.CheckResponse.HAM


      class SpamFlagTests(unittest.TestCase):
         """
         Test the spam-flagging function.

         """
         def test_flag_set_on_spam(self):
             """
             When the comment is identified as spam, the "filtered" attribute
             is set to True.

             """
             with AlwaysSpam() as akismet_client:
                 comment = flag_spam_comment(
                     akismet_client,
                     make_test_request(),
                     make_test_comment()
                 )
             assert comment.filtered

         def test_flag_not_set_on_non_spam(self):
             """
             When the comment is identified as non-spam, the "filtered" attribute
             is set to False.

             """
             with NeverSpam() as akismet_client:
                 comment = flag_spam_comment(
                     akismet_client,
                     make_test_request(),
                     make_test_comment()
                 )
             assert not comment.filtered

.. tab:: pytest

   .. code-block:: python

      import akismet
      import pytest

      from your_app.moderation import flag_spam_comment


      # The following test functions assume you have also defined pytest
      # fixtures to create the request and comment objects.
      #
      #
      # A pytest plugin provided with akismet defines fixtures for
      # sync and async clients, with behavior configured by the
      # akismet_client mark.

      @pytest.mark.akismet_client(comment_check_response=akismet.CheckResponse.SPAM)
      def test_flag_set_on_spam(akismet_sync_client, test_request, test_comment):
          """
          When the comment is identified as spam, the "filtered" attribute
          is set to True.

          """
          comment = flag_spam_comment(
              akismet_sync_client,
              test_request,
              test_comment
          )
          assert comment.filtered


      @pytest.mark.akismet_client(comment_check_response=akismet.CheckResponse.HAM)
      def test_flag_not_set_on_non_spam(akismet_sync_client, test_request, test_comment):
          """
          When the comment is identified as non-spam, the "filtered" attribute
          is set to False.

          """
          comment = flag_spam_comment(
              akismet_sync_client,
              test_request,
              test_comment
          )
          assert not comment.filtered


Recommended patterns
--------------------

In general, you should try to avoid manually creating/re-creating Akismet API clients
over and over. Instantiating the client and verifying its configuration is a moderately
expensive process (verifying the configuration requires making an HTTP request), so
ideally it's something you'll do only once per Python process, then keep the client
instance in memory for the duration of that process.

Then there are two main ways to access your Akismet client:

1. Provide some way of accessing the single in-memory Akismet client instance from other
   parts of your codebase, either via an import or some function which returns the
   client, or

2. Pass the client instance as an argument to functions which need it.

One approach is to use `the service locator pattern
<https://en.wikipedia.org/wiki/Service_locator_pattern>`_ and register an Akismet
client, or a factory for producing one, with the service locator; then any code which
needs it can ask the service locator for it. For example, `svcs
<https://svcs.hynek.me/en/stable/>`_ is a service-locator implementation in Python which
allows you to easily register both values and factory functions with it, as well as
providing an easy way to modify/override. The following example shows how you might
register both your Akismet configuration and a factory for Akismet clients with
``svcs``:

.. tab:: Sync

   .. code-block:: python

      import typing

      import akismet
      import svcs


      def provide_akismet_client(
          svcs_container: svcs.Container
      ) -> typing.Generator[akismet.SyncClient, None, None]:
          """
          Create and yield an Akismet client.

          """
          config = svcs_container.get(akismet.Config)
          with akismet.SyncClient(config=config) as akismet_client:
              yield akismet_client


      # The svcs registry is indexed by type -- each value or factory is
      # registered according to the type of object it will return.
      registry = svcs.Registry()
      registry.register_value(
          akismet.Config,
          akismet.Config(key=your_akismet_key, url=your_akismet_url)
      )
      registry.register_factory(akismet.SyncClient, provide_akismet_client)

.. tab:: Async

   .. code-block:: python

      import typing

      import akismet
      import svcs


      async def provide_akismet_client(
          svcs_container: svcs.Container
      ) -> typing.AsyncGenerator[akismet.AsyncClient, None]:
          """
          Create and yield an Akismet client.

          """
          config = svcs_container.get(akismet.Config)
          async with akismet.AsyncClient(config=config) as akismet_client:
              yield akismet_client


      # The svcs registry is indexed by type -- each value or factory is
      # registered according to the type of object it will return.
      registry = svcs.Registry()
      registry.register_value(
          akismet.Config,
          akismet.Config(key=your_akismet_key, url=your_akismet_url)
      )
      registry.register_factory(akismet.AsyncClient, provide_akismet_client)

Another approach is to use `dependency injection
<https://en.wikipedia.org/wiki/Dependency_injection>`_ to ensure an Akismet client is
provided, usually as an argument, to any function which needs it. The sample pytest code
in the testing example above already showed a version of this -- pytest's "fixtures" are
an implementation of the dependency injection technique. Many other tools and frameworks
support dependency injection as well, including several popular web frameworks like
`FastAPI <https://fastapi.tiangolo.com/tutorial/dependencies/>`_ and `Litestar
<https://docs.litestar.dev/latest/usage/dependency-injection.html>`_.

These can also be combined. For example, you could use dependency injection to provide a
``svcs`` container to any function which asks for it, or use ``svcs`` as a registry to
define things which a dependency-injection framework will read and inject. ``svcs``
already provides an integration for FastAPI's dependency-injection system, and `a plugin
for Litestar is also available <https://pypi.org/project/litestar-svcs/>`_.
