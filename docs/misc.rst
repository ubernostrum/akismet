.. _misc:

.. currentmodule:: akismet


Other code and data
===================

The following additional items are part of the publicly-exported API
of this module:

.. class:: AkismetArguments

   A :class:`~typing.TypedDict` representing the optional keyword
   arguments accepted by the comment-check, submit-ham, and
   submit-spam Akismet API operations.

   The names and types of these optional arguments are:

   * ``blog_charset``: :class:`str`
   * ``blog_lang``: :class:`str`
   * ``comment_author``: :class:`str`
   * ``comment_author_email``: :class:`str`
   * ``comment_author_url``: :class:`str`
   * ``comment_content``: :class:`str`
   * ``comment_context``: :class:`str`
   * ``comment_date_gmt``: :class:`str`
   * ``comment_post_modified_gmt``: :class:`str`
   * ``comment_type``: :class:`str`
   * ``honeypot_field_name``: :class:`str`
   * ``is_test``: :class:`bool`
   * ``permalink``: :class:`str`
   * ``recheck_reason``: :class:`str`
   * ``referrer``: :class:`str`
   * ``user_agent``: :class:`str`
   * ``user_role``: :class:`str`

   For the meanings of these arguments, see `the Akismet web service
   documentation
   <https://akismet.com/developers/detailed-docs/comment-check/>`_.


.. class:: CheckResponse

   Possible response values from an Akismet content check, including
   the possibility of the "discard" response, modeled as an
   :class:`enum.IntEnum`. See :meth:`SyncClient.comment_check` and
   :meth:`AsyncClient.comment_check` for details.

   Has the following members:

   .. attribute:: HAM

      Indicates Akismet classified a piece of content as ham (i.e.,
      not spam). Has integer value ``0``.

   .. attribute:: SPAM

      Indicates Akismet classified a piece of content as spam. Has
      integer value ``1``.

   .. attribute:: DISCARD

      Indicates Akismet classified a piece of content as "blatant"
      spam, suggesting that it be discarded without further
      review. Has integer value ``2``.


.. autoclass:: Config


.. data:: USER_AGENT

   A :class:`str` containing the default ``User-Agent`` header value
   which will be sent with all requests to the Akismet web
   service. This is automatically derived from the ``akismet`` module
   version and Python version in use.

   You generally will not need to use this value, but if you are
   passing a custom HTTP client to either :class:`SyncClient` or
   :class:`AsyncClient`, it can be useful to set this as the client's
   ``User-Agent`` header, for consistency.
