"""
A Python interface to `the Akismet spam-filtering service <https://akismet.com>`_.

Two Akismet API clients are available from this library:

* :class:`akismet.SyncClient` is an Akismet API client which performs synchronous
  (blocking) HTTP requests to the Akismet web service.

* :class:`akismet.AsyncClient` is an Akismet API client which performs asynchronous
  (``async``/``await``/non-blocking) HTTP requests to the Akismet web service.

Aside from one being sync and the other async, the two clients expose identical APIs,
and implement all methods of `the Akismet web API <https://akismet.com/developers/>`_.

To use this library, you will need to obtain an Akismet API key and register a site for
use with the Akismet web service; you can do this at <https://akismet.com>. Once you
have a key and corresponding registered site URL to use with it, place them in the
environment variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``, and
they will be automatically detected and used.

You can then construct a client instance and call its methods. It's recommended that you
always use a client construction method which will automatically validate your API key
with the Akismet web service. You can do this by creating your client as a context
manager, in which case the key is automatically validated on entering the ``with``
block:

.. code-block:: python

   import akismet

   with akismet.SyncClient() as akismet_client:
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

   async with akismet.AsyncClient() as akismet_client:
       if await akismet_client.comment_check(
           user_ip=submitter_ip,
           comment_content=submitted_content,
           comment_type="forum-post",
           comment_author=submitter_name
       ):
           # This piece of content was classified as spam; handle it appropriately.

Or you can use the ``validated_client()`` constructor method, which will validate your
key when constructing the client instance:

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

"""

# SPDX-License-Identifier: BSD-3-Clause

from ._async_client import AsyncClient
from ._common import USER_AGENT, AkismetArguments, CheckResponse, Config
from ._exceptions import (
    AkismetError,
    APIKeyError,
    ConfigurationError,
    ProtocolError,
    RequestError,
    UnknownArgumentError,
)
from ._sync_client import SyncClient
from ._test_clients import TestAsyncClient, TestSyncClient

__all__ = [
    "APIKeyError",
    "AkismetArguments",
    "AkismetError",
    "AsyncClient",
    "CheckResponse",
    "Config",
    "ConfigurationError",
    "ProtocolError",
    "RequestError",
    "SyncClient",
    "TestAsyncClient",
    "TestSyncClient",
    "UnknownArgumentError",
    "USER_AGENT",
]
