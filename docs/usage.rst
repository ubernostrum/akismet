.. _usage:


Usage guide
===========

To use ``akismet``, you will need to obtain an Akismet API key and register a
site for use with the Akismet web service; you can do this at
<https://akismet.com>. Once you have a key and corresponding registered site
URL to use with it, place them in the environment variables
``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``, and they will be
automatically detected and used.

You can also optionally set the environment variable ``PYTHON_AKISMET_TIMEOUT``
to a :class:`float` or :class:`int` containing a connection-timeout threshold
to use for making requests to the Akismet web service; if not set, this will
default to ``1.0`` (one second).


Basic use
---------

Once you have a key and registered site, and have set the environment
variables, you can create an Akismet API client. Two are available, one being
synchronous (blocking I/O), and the other asynchronous (non-blocking I/O).

.. admonition:: **Asynchronous Python**

   Most Python applications are synchronous, and cannot easily run async code
   (which requires an event loop and slightly different syntax to call
   functions/methods). So you'll probably want to use the synchronous Akismet
   client unless your entire application is already async (most commonly, this
   will be when you have an asynchronous web application built with an async
   framework like FastAPI or Litestar).

   And if you're not sure what all this means, you *definitely* want the
   synchronous Akismet client.

To create an Akismet API client, call the ``validated_client()`` constructor
method; this will automatically read your Akismet API key and site URL from the
environment variables, and validate them with Akismet. If they're not valid, or
if they're not found in the environment variables mentioned above, you'll get
an :exc:`akismet.ConfigurationError` exception.

.. tab:: Sync

   .. code-block:: python

      import akismet

      akismet_client = akismet.SyncClient.validated_client()

.. tab:: Async

   .. code-block:: python

      import akismet

      akismet_client = await akismet.AsyncClient.validated_client()

The most important operation of the Akismet client is checking a piece of
content to see if it's spam. This is done with the ``comment_check()``
method. There's one required argument -- the IP address of the user who
submitted the content -- but `a large number of optional arguments
<https://akismet.com/developers/comment-check/>`_ are also accepted. It's
recommended that you include as much information as possible to help Akismet
make accurate determinations, but at the very least you should pass the
following arguments:

* ``comment_content`` -- The actual content that was submitted.

* ``comment_type`` -- The type of content. Common values for this are
  ``"comment"``, ``"forum-post"``, ``"contact-form"``, and ``"signup"``, but
  you can also pass other values depending on the type of user-submitted
  content you're dealing with.

* ``comment_author`` and/or ``comment_email`` -- The identifier (such as a
  username) and/or the email address of the user who submitted the content.

For example, suppose you're using `the Django web framework
<https://www.djangoproject.com>`_ to build an online forum. You might write a
Django view for submitting new forum posts that looks like this (using the API
client created above):


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


Recommended patterns
--------------------

Creating an Akismet API client and verifying its API key/URL is a moderately
expensive process, and you generally don't need to constantly re-create the
client or re-verify its configuration. So you should try to do this only once
per Python process, and then keep the client in memory for the duration of the
process. One way to do this is to write a function which creates the client the
first time it's needed, and then stores it in a module-level variable for
reuse:

.. tab:: Sync

   .. code-block:: python

      import akismet

      _akismet_client = None

      def get_akismet_client():
          """
          Create (if necessary) and return an Akismet API client.

          """
          global _akismet_client
          if _akismet_client is None:
              _akismet_client = akismet.SyncClient.validated_client()
          return _akismet_client

      # Other files in your codebase can import this one and call get_akismet_client()

.. tab:: Async

   .. code-block:: python

      import akismet

      _akismet_client = None

      async def get_akismet_client():
          """
          Create (if necessary) and return an Akismet API client.

          """
          global _akismet_client
          if _akismet_client is None:
              _akismet_client = await akismet.AsyncClient.validated_client()
          return _akismet_client

      # Other files in your codebase can import this one and call get_akismet_client()

A more flexible approach is to adopt something like a `service locator pattern
<https://en.wikipedia.org/wiki/Service_locator_pattern>`_ and use that to
obtain and manage an Akismet API client. For example, `svcs
<https://pypi.org/project/svcs/>`_ is a service-locator implementation for
Python which could be used to register and re-use an Akismet API client (or a
factory function for building a custom one). Whenever possible, this approach
is recommended because it simplifies not just the use of the Akismet API client
but likely many other aspects of your application as well.


Testing your use of ``akismet``
-------------------------------

While you *can* perform limited end-to-end testing of Akismet's spam-checking
if you want to (see :ref:`the testing guide <testing>` for details), in general
it's discouraged to make live requests to external services as part of a normal
application test suite.

It's also generally discouraged to build extensive :mod:`unittest.mock`
representations of code that isn't under your control; this often leads to
over-complicated test setups and a high maintenance burden as you attempt to
keep your mocks in sync with what a third-party library is doing.

So ``akismet`` provides two test clients intended to be used in your
application's tests: :class:`~akismet.TestAsyncClient` as a test version of
:class:`~akismet.AsyncClient`, and :class:`~akismet.TestSyncClient` as a test
version of :class:`~akismet.SyncClient`.

Both of these test classes implement the full API of their real counterparts,
but they do *not* make actual requests to the Akismet web service. You can
configure them by subclassing and setting attributes to simulate content being
marked as spam/not-spam and also to simulate an invalid API key. For example,
you might write a simple spam-flagging function which toggles an attribute on a
submitted comment:

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

   test_config = akismet.Config(key="fake-test-key", url="http://example.com")

   class SpamFlagTests(unittest.TestCase):
       """
       Test the spam-flagging function.

       """
       def test_flag_set_on_spam(self):
           """
           When the comment is identified as spam, the "filtered" attribute
           is set to True.

           """
           akismet_client = AlwaysSpam(config=test_config)
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
           akismet_client = NeverSpam(config=test_config)
           comment = flag_spam_comment(
               akismet_client,
               make_test_request(),
               make_test_comment()
           )
           assert not comment.filtered


Advanced usage
--------------

The full Akismet API has many more methods -- see the API reference for
:class:`~akismet.SyncClient` or :class:`~akismet.AsyncClient` for full details
-- but a few of the more useful things to know are:


Detecting "blatant" spam
~~~~~~~~~~~~~~~~~~~~~~~~

The example above showed spam detection as an either/or check -- either
something is spam, or it's not. But Akismet actually supports *three* possible
states: "not spam", "spam", and "blatant spam". One way you could use this is
to add a manual review step: if something is marked as "not spam" it's allowed
to post normally, "spam" goes into a review queue for you to look at, and
"blatant spam" is just rejected without any further review.

You can implement this by looking at the return value of the
``comment_check()`` method, which is actually an enum --
:class:`akismet.CheckResponse` -- with three possible values. So you could
adapt the example of ``comment_check()`` above to do this:


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

This works because the :class:`~akismet.CheckResponse` enum uses integer
values; when fed directly to an ``if``/``else``, they work as boolean values
(``HAM`` is ``0``, ``SPAM`` is ``1``, and ``DISCARD`` is ``2``).


Using a custom HTTP client
~~~~~~~~~~~~~~~~~~~~~~~~~~

For some use cases, you may need custom HTTP client behavior. For example, you
might be running on a server which has to use an HTTP proxy to access any
external service. In that case, you can pass a custom HTTP client to the
Akismet API client, as the constructor argument ``http_client``. The Akismet
API clients use `the Python HTTPX library <https://www.python-httpx.org>`_
(which is automatically installed when you install ``akismet``) for their HTTP
clients, so you can create either an ``httpx.Client`` or an
``httpx.AsyncClient`` with the behavior you want.

You should also make sure to set a value for the ``User-Agent`` header of your
custom HTTP client. If you want the default value the Akismet clients would
use, it's available as :data:`akismet.USER_AGENT`.


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

Finally, note that if all you want is to set a custom timeout value for
connections to the Akismet web service, you *can* do this with a custom HTTP
client, or you can simply set the environment variable
``PYTHON_AKISMET_TIMEOUT`` as described above.


Alternative configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't want to configure your Akismet client via the standard environment
variables, or aren't able to set the environment variables, you can avoid the
``validated_client()`` method and instantiate your Akismet client
directly. This is done via the :class:`akismet.Config` utility tuple. You
should also make sure to validate the configuration before trying to use the
client.

.. tab:: Sync

   .. code-block:: python

      import akismet

      config = akismet.Config(key=your_api_key, url=your_site_url)

      akismet_client = akismet.SyncClient(config=config)

      if not akismet_client.verify_key(config.key, config.url):
          # The configuration was invalid!

.. tab:: Async

   .. code-block:: python

      import akismet

      config = akismet.Config(key=your_api_key, url=your_site_url)

      # When constructing a client this way, you do *not* need to "await" it!
      akismet_client = akismet.AsyncClient(config=config)

      # But you *do* need to "await" the verify_key() method.
      if not await akismet_client.verify_key(config.key, config.url):
          # The configuration was invalid!

If you also need a custom HTTP client when configuring this way, you can also
pass it in, again as the keyword argument ``http_client``.
