.. faq:

Frequently asked questions
==========================

The following notes answer common questions, and may be useful to you when
using ``akismet``.


What versions of Python are supported?
--------------------------------------

The |release| release of ``akismet`` supports the following versions of Python:


* Python 3.8

* Python 3.9

* Python 3.10

* Python 3.11

* Python 3.12

Older versions of Python are not supported and will cause errors.


Do I have to send all the optional arguments?
---------------------------------------------

The Akismet web service supports a large number of optional arguments to
provide additional information for classification and training. You can submit
as many of them as you wish with the ``comment_check``, ``submit_ham``, and
``submit_spam`` operations. The Akismet documentation recommends sending as
much information as possible, though only the ``user_ip`` argument to those
methods is actually required.


Is this only for blog comments?
-------------------------------

The Akismet web service can handle many types of user-submitted content,
including comments, contact-form submissions, user signups and more. See
`Akismet's documentation of the comment check operation
<https://akismet.com/developers/comment-check/>`_ for details.


.. _alt-constructor:

Why shouldn't I create the client directly?
-------------------------------------------

Both of the API clients provide a ``classmethod`` which serves as an alternate
constructor: :meth:`akismet.SyncClient.validated_client` and
:meth:`akismet.AsyncClient.validated_client`, and you're encouraged to use
these alternate constructors when you need an instance of one of the clients.

The short explanation for this is that the ``validated_client()`` constructor
will automatically read your Akismet API key and site URL from environment
variables (``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``) and
validate them via the ``verify_key`` operation before returning the API client
instance to you, and this is highly useful behavior.

If you don't use the ``validated_client()`` constructor, you'll need to
construct your own :class:`~akismet.Config` to pass in to the default
constructor, and you'll want to ensure you call the verify-key operation to
validate that configuration.

The longer explanation is that the ``validated_client()`` constructor allows
both the sync and async clients to provide the same
interface. :class:`~akismet.SyncClient` could easily just read the
configuration and do the validation in its own ``__init__()`` method. But
:class:`~akismet.AsyncClient` cannot do this, because its
:meth:`~akismet.AsyncClient.verify_key` method is asynchronous; calling it in
``__init__()`` would require making the ``__init__()`` method asynchronous too,
and an async ``__init__()`` is not currently supported by Python.

This limitation does not apply to classmethods used as alternate constructors,
so to provide a useful constructor that does automatic discovery and validation
of your Akismet configuration, :class:`~akismet.AsyncClient` defines the
alternate constructor :meth:`~akismet.AsyncClient.validated_client`. And to
ensure both client classes have the same interface,
:class:`~akismet.SyncClient` also provides a
:meth:`~akismet.SyncClient.validated_client` constructor.


How do I check my key?
----------------------

The simplest way is to set your key and site URL in the standard environment
variables (``PYTHON_AKISMET_API_KEY`` / ``PYTHON_AKISMET_BLOG_URL``), and then
call either :meth:`akismet.SyncClient.validated_client` or
:meth:`akismet.AsyncClient.validated_client`; the ``validated_client()``
constructor automatically verifies the key and URL for you, and will raise
:exc:`~akismet.APIKeyError` if the key is invalid.

If you're not able to do this, you can also manually instantiate a client and
then call its ``verify_key()`` method, passing the key and URL you want to
check as the arguments. For example:

.. tab:: Sync

   .. code-block:: python

      import akismet

      config = akismet.Config(key=key_to_test, url=url_to_test)
      client = akismet.SyncClient(config=config)
      if not client.verify_key(key_to_test, url_to_test):
          # The key/URL were invalid.

.. tab:: Async

   .. code-block:: python

      import akismet

      config = akismet.Config(key=key_to_test, url=url_to_test)
      client = akismet.AyncClient(config=config)
      if not await client.verify_key(key_to_test, url_to_test):
          # The key/URL were invalid.


How can I test that it's working?
---------------------------------

The documentation :ref:`includes a section <testing>` on how to run
``akismet``'s unit test suite.

If you want to manually perform your own tests, you can also instantiate an
Akismet client class and call its methods. When doing so, it is recommended
that you pass the optional keyword argument ``is_test=1`` to the comment-check,
submit-ham, and submit-spam operations; this tells the Akismet web service that
you are only issuing requests for testing purposes, and will not result in any
submissions being incorporated into Akismet's training corpus.


What user-agent string is sent by ``akismet``?
----------------------------------------------

The Akismet web service documentation recommends sending a string identifying
the application or platform with version, and Akismet plugin/implementation
name with version. In accordance with this, ``akismet`` sends an HTTP
``User-Agent`` based on the versions of Python and ``akismet`` in use. For
example, ``akismet`` 1.3 on Python 3.10.4 will send ``akismet.py/1.3 | Python
3.10.4``.


Does ``akismet`` support the "pro-tip" header?
----------------------------------------------

For content determined to be "blatant" spam (and thus which does not need to be
placed into a queue for review by a human), the Akismet web service will add
the header ``X-akismet-pro-tip: discard`` to its comment-check response.

The comment-check operations of both the sync and async clients provide a
mechanism to read this, expressed through the :class:`~akismet.CheckResponse`
enum.


How am I allowed to use this module?
------------------------------------

``akismet`` is distributed under a `three-clause BSD license
<http://opensource.org/licenses/BSD-3-Clause>`_. This is an open-source license
which grants you broad freedom to use, redistribute, modify and distribute
modified versions of ``akismet``. For details, see the file ``LICENSE`` in the
source distribution of ``akismet``.


I found a bug or want to make an improvement!
---------------------------------------------

The canonical development repository for ``akismet`` is online at
<https://github.com/ubernostrum/akismet>. Issues and pull requests can both be
filed there.
