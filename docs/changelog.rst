.. _changelog:

Changelog
=========

This is a list of changes made in released versions of this library, tracking since its
1.0 release.


Version numbering
-----------------

This library currently tracks its version numbers using the ``YY.MM.MICRO`` form of
`Calendar Versioning <https://calver.org>`_ ("CalVer"), in which the first two
components of the version number are the (two-digit) year and (non-zero-padded) month of
the release date, while the third component is an incrementing value for releases
occurring in that month. For example, the first release issued in January 2025 would
have a version number of 25.1.0; a subsequent release in the same month would be 25.1.1;
a release the following month (February) would be 25.2.0.

The CalVer system was adopted for this library in 2024, and the first release to use a
CalVer version number was 24.5.0.


API stability and deprecations
------------------------------

The API stability/deprecation policy for this library is as follows:

* The supported stable public API of this library is the set of symbols which are
  exported by its ``__all__`` declaration and which are documented in this
  documentation. For classes exported there, the supported stable public API is the set
  of methods and attributes of those classes whose names do not begin with one or more
  underscore (``_``) characters and which are documented in this documentation.

* When a public API is to be removed, or undergo a backwards-incompatible change, it
  will emit a deprecation warning which serves as notice of the intended removal or
  change, and which will give a date -- which will always be at least in the next
  calendar year after the first release which emits the deprecation warning -- past
  which the removal or change may occur without further warning.

* Security fixes, and fixes for high-severity bugs (such as those which might cause
  unrecoverable crash or data loss), are not required to emit deprecation warnings, and
  may -- if needed -- impose backwards-incompatible change in any release. If this
  occurs, this changelog document will contain a note explaining why the usual
  deprecation process could not be followed for that case.

* This policy is in effect as of the adoption of CalVer versioning, with version 24.5.0
  of this library.


Releases under CalVer
---------------------

Version 25.10.0
~~~~~~~~~~~~~~~

Released October 2025

* Supported Python versions are now Python 3.10, 3.11, 3.12, 3.13, and 3.14.

* Added :ref:`a pytest plugin <pytest-plugin>` to make use of the test clients easier.

* Removed the legacy ``akismet.Akismet`` client class. Use of either the synchronous
  :class:`~akismet.SyncClient` or asynchronous :class:`~akismet.AsyncClient` is now
  mandatory. The legacy ``Akismet`` client class had been deprecated and raising
  warnings since version 1.3.

* Added the :class:`~akismet.AkismetArguments` typed dictionary to represent the set of
  optional keyword arguments accepted by the comment-check, submit-ham, and submit-spam
  API operations.


Version 24.11.0
~~~~~~~~~~~~~~~

Released November 2024

* Supported Python versions are now Python 3.9, 3.10, 3.11, 3.12, and 3.13.


Version 24.5.1
~~~~~~~~~~~~~~

Released May 2024

* Corrected a missing release date in the changelog.


Version 24.5.0
~~~~~~~~~~~~~~

Released May 2024

* Adopted `CalVer versioning <https://calver.org>`_.

* Introduced the test client classes: :class:`~akismet.TestSyncClient` and
  :class:`~akismet.TestAsyncClient`.

* The ``validated_client()`` constructor of both client classes now optionally accepts
  an explicit :class:`~akismet.Config` instance.

* The default constructor's ``config`` argument is now optional on both client classes;
  as with ``validated_client()``, it will attempt to find the config in environment
  variables if it is not explicitly passed in. This means the only difference now
  between the default constructor and the ``validated_client()`` constructor is the
  validation of the key/URL in ``validated_client()``.

* The ``key`` and ``url`` arguments to the ``verify_key()`` method of both client
  classes are now optional; if not supplied, ``verify_key()`` uses the key and URL from
  the client's current config.

* :class:`~akismet.SyncClient` can now be used as a context manager, and
  :class:`~akismet.AsyncClient` can now be used as an async (``async with``) context
  manager. In both cases, it is not necessary to use the ``validated_client()``
  constructor; the config validation is performed when entering the context manager.


Releases not under CalVer
-------------------------

Version 1.3
~~~~~~~~~~~

Released February 2024

* The supported Python versions are now 3.8, 3.9, 3.10, 3.11, and 3.12. Support for
  earlier Python versions is dropped.

* Introduced the :class:`~akismet.SyncClient` and :class:`~akismet.AsyncClient` API
  client classes.

* The :class:`~akismet.SyncClient` and :class:`~akismet.AsyncClient` API client classes
  support the ``X-akismet-pro-tip`` header, and expose the "discard" header response by
  using the :class:`~akismet.CheckResponse` enum as the return value of their
  comment-check operation.

* The :class:`~akismet.SyncClient` and :class:`~akismet.AsyncClient` API client classes
  support the `activity <https://akismet.com/developers/key-sites-activity/>`_ and
  `usage limit <https://akismet.com/developers/usage-limit/>`_ methods of the Akismet
  v1.2 web API.

* **Deprecation:** The ``Akismet`` API client class is now deprecated, and will be
  removed in 2025. Instantiating this class will issue a :exc:`DeprecationWarning`. To
  discourage new uses of this class, its API documentation has been removed; refer to
  its docstrings, or to documentation for an earlier version of this module, if you
  continue to need documentation for it. All users of the deprecated ``Akismet`` class
  are encouraged to migrate as quickly as possible to one of the two new client classes,
  which more fully implement the Akismet web API. The deprecated ``Akismet`` class will
  receive no further features, and will only receive bugfixes if a security issue is
  discovered.

* All of the API clients, including the deprecated ``Akismet`` class which formerly used
  ``requests``, now use ``httpx`` internally as their default HTTP client. This provides
  uniformity of interface, async support, and better defaults (such as a default request
  timeout value). The default timeout is now one second, but is configurable by setting
  the environment variable ``PYTHON_AKISMET_TIMEOUT`` to a :class:`float` or
  :class:`int` value containing the desired timeout threshold in seconds.

Version 1.2
~~~~~~~~~~~

Released May 2022

* The supported Python versions are now 3.7, 3.8, 3.9, and 3.10. Support for earlier
  Python 3 versions is dropped.

Version 1.1
~~~~~~~~~~~

Released February 2020

* ``akismet`` tracks versions of Python supported upstream by the Python core
  team. Since ``akismet`` 1.1 was released after the Python core team dropped support
  for Python 2, ``akismet`` 1.1 and later do not support Python 2. The new minimum
  Python version supported by ``akismet`` is 3.5.

* Support was added for the optional ``recheck_reason``, used when a comment or other
  content is being submitted a second or later time, and indicating the reason (such as
  `"edit"` when resubmitting a comment after the user edited it).

Version 1.0.1
~~~~~~~~~~~~~

Released May 2017

* Corrected several typographical errors in the 1.0 release documentation.

Version 1.0
~~~~~~~~~~~

Released May 2017

* Significant rewrite of the pre-1.0 codebase. Prior to this, the last release was
  version 0.2.0 in June 2009.

* **Feature removal:** Configuring the Akismet client by placing a specially-named file
  containing the API key is no longer supported. The only supported configuration
  methods are explicit constructor arguments or environment variables.

* **Feature removal:** Specifying a custom ``User-Agent`` header value is no longer
  supported as a constructor argument. To set a custom ``User-Agent`` header, subclass
  the Akismet client and set the attribute ``user_agent_header`` to a dictionary
  containing the header(s) to send.

* **Method removal:** The ``setAPIKey()`` method of the Akismet client class is removed.

* The ``requests`` library is now a dependency.
