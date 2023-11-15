.. _misc:

.. module:: akismet
  :noindex:


Other code and data
===================

The following additional items are part of the publicly-exported API of this
module:

.. class:: CheckResponse

   Possible response values from an Akismet content check, including the
   possibility of the "discard" response, modeled as an
   :class:`enum.IntEnum`. See :meth:`SyncClient.comment_check` and
   :meth:`AsyncClient.comment_check` for details.

   Has the following members:

   .. attribute:: HAM

      Indicates Akismet classified a piece of content as ham (i.e., not
      spam). Has integer value ``0``.

   .. attribute:: SPAM

      Indicates Akismet classified a piece of content as spam. Has integer
      value ``1``.

   .. attribute:: DISCARD

      Indicates Akismet classified a piece of content as "blatant" spam,
      suggesting that it be discarded without further review. Has integer value
      ``2``.


.. autoclass:: Config


.. data:: USER_AGENT

   A :class:`str` containing the default ``User-Agent`` header value which will
   be sent with all requests to the Akismet web service. This is automatically
   derived from the ``akismet`` module version and Python version in use.

   You generally will not need to use this value, but if you are passing a
   custom HTTP client to either :class:`SyncClient` or :class:`AsyncClient`, it
   can be useful to set this as the client's ``User-Agent`` header, for
   consistency.
