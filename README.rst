.. -*-restructuredtext-*-

.. image:: https://github.com/ubernostrum/akismet/workflows/CI/badge.svg
   :alt: CI status image
   :target: https://github.com/ubernostrum/akismet/actions?query=workflow%3ACI

A Python interface to `the Akismet spam-filtering service
<https://akismet.com>`_.

Two API clients are available from this library:

* ``akismet.SyncClient`` is an Akismet API client which performs
  synchronous (blocking) HTTP requests to the Akismet web service.

* ``akismet.AsyncClient`` is an Akismet API client which performs
  asynchronous (``async``/``await``/non-blocking) HTTP requests to the
  Akismet web service.

Aside from one being sync and the other async, the two clients expose
identical APIs, and implement all methods of `the Akismet web API
<https://akismet.com/developers/>`_, including the v1.2 key and API
usage metrics.

To use this library, you will need to obtain an Akismet API key and
register a site for use with the Akismet web service; you can do this
at <https://akismet.com>. Once you have a key and corresponding
registered site URL to use with it, place them in the environment
variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``,
and they will be automatically detected and used.

You can then construct a client instance and call its methods. For
example, to check a submitted forum post for spam:

.. code-block:: python

   import akismet

   akismet_client = akismet.SyncClient.validated_client()

   if akismet_client.comment_check(
       user_ip=submitter_ip,
       comment_content=submitted_content,
       comment_type="forum-post",
       comment_author=submitter_name
   ):
       # This piece of content was classified as spam; handle it appropriately.

Or using the asynchronous client:

.. code-block:: python

   import akismet

   akismet_client = await akismet.AsyncClient.validated_client()

   if await akismet_client.comment_check(
       user_ip=submitter_ip,
       comment_content=submitted_content,
       comment_type="forum-post",
       comment_author=submitter_name
   ):
       # This piece of content was classified as spam; handle it appropriately.

Note that in both cases the client instance is created via the
alternate constructor ``validated_client()``. This is recommended
instead of using the default constructor (i.e., directly calling
``akismet.SyncClient()`` or ``akismet.AsyncClient()``); the
``validated_client()`` constructor will perform automatic discovery of
the environment-variable configuration and validate the configuration
with the Akismet web service before returning the client, while
directly constructing an instance will not (so if you do directly
construct an instance, you must manually provide and validate its
configuration).

See `the documentation <http://akismet.readthedocs.io/>`_ for full
details.

The original version of this library was written by Michael Foord.
