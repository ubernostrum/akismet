.. faq:

Frequently asked questions
==========================

The following notes answer common questions, and may be useful to you when using
``akismet``.


What versions of Python are supported?
--------------------------------------

The |release| release of ``akismet`` supports the following versions of Python:

* Python 3.10

* Python 3.11

* Python 3.12

* Python 3.13

* Python 3.14

Older versions of Python are not supported and will cause errors.


Do I have to send all the optional arguments?
---------------------------------------------

The Akismet web service supports a large number of optional arguments to provide
additional information for classification and training. You can submit as many of them
as you wish with the ``comment_check``, ``submit_ham``, and ``submit_spam``
operations. The Akismet documentation recommends sending as much information as
possible, though only the ``user_ip`` argument to those methods is actually required.


Is this only for blog comments?
-------------------------------

The Akismet web service can handle many types of user-submitted content, including
comments, contact-form submissions, user signups and more. See `Akismet's documentation
of the comment check operation <https://akismet.com/developers/comment-check/>`_ for
details.


.. _alt-constructor:

Why doesn't the default constructor validate the config?
--------------------------------------------------------

Both of the Akismet API clients provide an alternate constructor --
:meth:`akismet.SyncClient.validated_client` and
:meth:`akismet.AsyncClient.validated_client` -- and you're encouraged to use these
nearly any time you want an instance of an Akismet API client (the exception is using a
client as a context manager -- see below), because the ``validated_client()``
constructor will validate your Akismet configuration (via the verify-key API operation)
automatically. If you don't do this, you'll need to call ``verify_key()`` manually (and
ideally only once for each client instance).

The technical reason for this is that the ``validated_client()`` constructor allows both
the sync and async clients to provide the same interface. :class:`~akismet.SyncClient`
could perform the validation in its ``__init__()`` method, but
:class:`~akismet.AsyncClient` cannot, because its
:meth:`~akismet.AsyncClient.verify_key` method is asynchronous; calling it in
``__init__()`` would require making the ``__init__()`` method asynchronous too, and an
async ``__init__()`` is not currently supported by Python.

This limitation does not apply to classmethods used as alternate constructors, so to
perform automatic validation of your Akismet configuration,
:class:`~akismet.AsyncClient` defines the alternate constructor
:meth:`~akismet.AsyncClient.validated_client`. And to ensure both client classes have
the same interface, :class:`~akismet.SyncClient` also provides a
:meth:`~akismet.SyncClient.validated_client` constructor.

Using either client class as a context manager does not have this technical limitation
(the entry method of an async context manager is async, so the verify-key operation can
be called there), so using one of the Akismet client classes as a context manager does
not require using the alternate constructor.


How do I check my key?
----------------------

The simplest way is to either:

* Use :meth:`akismet.SyncClient.validated_client` /
  :meth:`akismet.AsyncClient.validated_client`, or

* Create a client as a context manager (e.g., ``with akismet.SyncClient() as
  akismet_client`` or ``async with akismet.AsyncClient() as akismet_client``)

Either of these approaches automatically verifies the key and URL for you, and will
raise :exc:`~akismet.APIKeyError` if the key is invalid.

If you're not able to do this, you can also manually instantiate a client and then call
its ``verify_key()`` method, passing the key and URL you want to check as the
arguments. For example:

.. tab:: Sync

   .. code-block:: python

      import akismet

      client = akismet.SyncClient()
      if not client.verify_key(key_to_test, url_to_test):
          # The key/URL were invalid.

.. tab:: Async

   .. code-block:: python

      import akismet

      client = akismet.AyncClient()
      if not await client.verify_key(key_to_test, url_to_test):
          # The key/URL were invalid.


How can I test that it's working?
---------------------------------

``akismet`` provides test-client implementations you can use in your own application's
tests; it also provides its own thorough test suite you can run to verify its behavior,
and you can perform some live end-to-end testing through the standard Akismet API
clients. See :ref:`the testing guide <testing>` for details.


What user-agent string is sent by ``akismet``?
----------------------------------------------

The Akismet web service documentation recommends sending a string identifying the
application or platform with version, and Akismet plugin/implementation name with
version. In accordance with this, ``akismet`` sends an HTTP ``User-Agent`` based on the
versions of Python and ``akismet`` in use. For example, ``akismet`` 24.4.0 on Python
3.10.4 will send ``akismet.py/24.4.0 | Python 3.10.4``.


Does ``akismet`` support the "pro-tip" header?
----------------------------------------------

For content determined to be "blatant" spam (and thus which does not need to be placed
into a queue for review by a human), the Akismet web service will add the header
``X-akismet-pro-tip: discard`` to its comment-check response.

The comment-check operations of both the sync and async clients provide a mechanism to
read this, expressed through the :class:`~akismet.CheckResponse` enum.


How am I allowed to use this module?
------------------------------------

``akismet`` is distributed under a `three-clause BSD license
<http://opensource.org/licenses/BSD-3-Clause>`_. This is an open-source license which
grants you broad freedom to use, redistribute, modify and distribute modified versions
of ``akismet``. For details, see the file ``LICENSE`` in the source distribution of
``akismet``.


I found a bug or want to make an improvement!
---------------------------------------------

The canonical development repository for ``akismet`` is online at
<https://github.com/ubernostrum/akismet>. Issues and pull requests can both be filed
there.
