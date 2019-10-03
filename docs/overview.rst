.. module:: akismet

.. _overview:

Usage overview
==============

Once you have `akismet` :ref:`installed <install>`, you can begin
using it as soon as you register an API key and a site to use it on.


.. _api-key:

Obtaining an API key
--------------------

Use of `akismet` requires an Akismet API key, and requires
associating that API key with the site you'll use `akismet`
on. Visit `akismet.com <https://akismet.com/>`_ to purchase an API key
and associate it with a site.


.. _optional-arguments:

Optional arguments to API methods
---------------------------------

For API methods other than :meth:`~Akismet.verify_key`, only the end
user's IP address and user-agent string are required to be passed as
arguments (a third argument, `blog`, will be automatically inserted
for you). However, these methods all accept a large set of optional
keyword arguments, corresponding to additional data accepted by the
Akismet web service. This set of arguments is identical across all the
API methods.

Akismet recommends sending as many of these arguments as possible, as
additional data helps with identification of spam and training the
service.

For a full list of the supported arguments, see `the Akismet web
service documentation
<https://akismet.com/development/api/#comment-check>`_.

The most commonly useful arguments are:

* `comment_author` -- a :class:`str` containing the name or username
  of the person posting the comment.

* `comment_content` -- a :class:`str` containing the contents of the
  comment.

* `comment_type` -- a :class:`str` indicating the type of comment. For
  typical site comments, set this to `"comment"`. For a contact form,
  use `"contact-form"`. For a user-account signup, use `"signup"`.

If you call a method of :class:`Akismet` and pass one or more
arguments not recognized by the Akismet web service, an
:exc:`UnknownArgumentError` will be raised.


Using `akismet`
-----------------

.. class:: Akismet

   This is the wrapper class for the Akismet API. Instantiating it
   requires two parameters: your Akismet API key and the URL that key
   is associated with. You can pass these as the keyword arguments
   `key` and `blog_url` when instantiating `Akismet`, like so:

   .. code-block:: python

      import akismet

      akismet_api = akismet.Akismet(
          key='your API key',
          blog_url='http://yoursite.com'
      )

   You can also configure via environment variables: to do so, place
   the API key in the environment variable `PYTHON_AKISMET_API_KEY`,
   and the URL in the environment variable
   `PYTHON_AKISMET_BLOG_URL`.

   Instantiating :class:`Akismet` will automatically verify your API key and
   URL with the Akismet web service. If you do not supply an API key
   and/or URL, :exc:`ConfigurationError` will be raised. If your API
   key and URL are not valid, :exc:`APIKeyError` will be raised.

   Methods for using the API are:


   .. classmethod:: verify_key(key, blog_url)

      Verifies an Akismet API key and URL. Although this is done
      automatically during instantiation, you can also use this method
      to check a different key and URL manually.

      Returns :data:`True` if the key/URL are valid, :data:`False` if
      they are invalid.

      :param key: The API key to verify.
      :type key: str
      :param blog_url: The URL the key is associated with.
      :type blog_url: str
      :rtype: bool
      :raises ConfigurationError: if `blog_url` is not a full URL
         including the `http://` or `https://` protocol.


   .. method:: comment_check(user_ip, user_agent, **kwargs)

      Checks a comment to determine whether it is spam.

      This method accepts the full range of :ref:`optional arguments
      to the Akismet API service <optional-arguments>` in addition to
      its two required arguments.

      Returns :data:`True` if the comment is classified as spam,
      :data:`False` if it is not.

      :param user_ip: The IP address of the user posting the comment.
      :type user_ip: str
      :param user_agent: The HTTP `User-Agent` header of the user
         posting the comment.
      :type user_agent: str
      :rtype: bool
      :raises UnknownArgumentError: if one or more unrecognized
         arguments are passed in `kwargs`.


   .. method:: submit_spam(user_ip, user_agent, **kwargs)

      Informs Akismet that a comment (which it had classified as not
      spam) is in fact spam.

      This method accepts the full range of :ref:`optional arguments
      to the Akismet API service <optional-arguments>` in addition to
      its two required arguments.

      Returns :data:`True` on a successful submission.

      :param user_ip: The IP address of the user posting the comment.
      :type user_ip: str
      :param user_agent: The HTTP `User-Agent` header of the user
         posting the comment.
      :type user_agent: str
      :rtype: bool
      :raises UnknownArgumentError: if one or more unrecognized
         arguments are passed in `kwargs`.
      :raises ProtocolError: if submission fails due to Akismet API
         error.


   .. method:: submit_ham(user_ip, user_agent, **kwargs)

      Informs Akismet that a comment (which it had classified as spam)
      is in fact not spam.

      This method accepts the full range of :ref:`optional arguments
      to the Akismet API service <optional-arguments>` in addition to
      its two required arguments.

      Returns :data:`True` on a successful submission.

      :param user_ip: The IP address of the user posting the comment.
      :type user_ip: str
      :param user_agent: The HTTP `User-Agent` header of the user
         posting the comment.
      :type user_agent: str
      :rtype: bool
      :raises UnknownArgumentError: if one or more unrecognized
         arguments are passed in `kwargs`.
      :raises ProtocolError: if submission fails due to Akismet API
         error.


Exceptions
----------

To represent different possible error conditions, `akismet` provides
several exception classes:

.. exception:: AkismetError

   Base class for all exceptions directly raised by `akismet`. Other
   exceptions may still occur (for example, due to network
   unavailability or timeout), and will not be caught by `akismet`
   or replaced with this exception.


.. exception:: UnknownArgumentError

   Subclass of :exc:`AkismetError` indicating an unexpected argument
   was provided as part of a request. The message raised with this
   exception will include the names of all the unknown arguments.


.. exception:: ProtocolError

   Subclass of :exc:`AkismetError` indicating an unexpected or
   non-standard response was received from the Akismet web
   service. The message raised with this exception will include the
   API method invoked, and the contents of the unexpected response.


.. exception:: ConfigurationError

   Subclass of :exc:`AkismetError` indicating that the supplied
   configuration is missing or invalid. The message raised with this
   exception will provide details of the problem.


.. exception:: APIKeyError

   Subclass of :exc:`ConfigurationError` to indicate the specific case
   of an invalid API key.
