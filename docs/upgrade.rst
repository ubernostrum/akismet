.. upgrading:

Upgrading from previous versions
================================

Changes within the 1.x release series
-------------------------------------

Version 1.2
-----------

* The supported Python versions are now 3.7, 3.8, 3.9, and
  3.10. Support for earlier Python 3 versions is dropped.

Version 1.1
~~~~~~~~~~~

* `akismet` tracks versions of Python supported upstream by the Python
  core team. Since `akismet` 1.1 was released after the Python core
  team dropped support for Python 2, `akismet` 1.1 and later do not
  support Python 2. The new minimum Python version supported by
  `akismet` is 3.5.

* Support was added for the :ref:`optional argument
  <optional-arguments>` `recheck_reason`, used when a comment or other
  content is being submitted a second or later time, and indicating
  the reason (such as `"edit"` when resubmitting a comment after the
  user edited it).


Changes from older releases to the 1.x release series
-----------------------------------------------------

Prior to the 1.0 release, the last release of `akismet` was in
2009. If you were still using that release (0.2.0), there are some
changes you'll need to be aware of when upgrading to 1.0 or later.


Configuration via file no longer supported
------------------------------------------

In 0.2.0, `akismet` supported configuration via a file named
`apikey.txt`. Support for this has been removed in favor of either
explicitly configuring via arguments as the :class:`~akismet.Akismet`
class is instantiated, or configuring via environment variables. If
you were relying on an `apikey.txt` file for configuration, you will
need to switch to explicit arguments or environment variables.


Custom user agent no longer supported
--------------------------------------

In 0.2.0, `akismet` allowed you to specify the string which would be
sent in the `User-Agent` HTTP header. The Akismet web service
documentation now recommends a standard format for the `User-Agent`
header, and as a result this is no longer directly configurable. The
`User-Agent` string of `akismet` will now be based on the Python
version and the version of `akismet`, in accordance with the Akismet
service's recommendation. For example, `akismet` 1.0 on Python
3.5 will send the string `Python/3.5 | akismet.py/1.0`.

If you do need to send a custom `User-Agent`, you can subclass
:class:`~akismet.Akismet` and change the attribute
`user_agent_header` to a dictionary specifying the header you
want. For example:

.. code-block:: python

   import akismet

   class MyAkismet(akismet.Akismet):
       user_agent_header = {'User-Agent': 'My Akismet application'}


`requests` is now a dependency
--------------------------------

Prior versions of `akismet` were implemented solely using modules in
the Python standard library. As the Python standard library's support
for easily performing HTTP requests is poor, `akismet` as of 1.0 has a
dependency on `the requests library
<http://docs.python-requests.org/en/master/>`_, which will be
automatically installed for you when you install a packaged copy of
`akismet`.


API changes
-----------

Finally, the public API of `akismet` has been modified to match the
current interface of the Akismet web service. This has resulted in the
removal of one public method of :class:`~akismet.Akismet` --
`setAPIKey` -- and changes to the argument signatures of other
methods.

For details of the updated interface, consult :ref:`the usage overview
document <overview>`.
