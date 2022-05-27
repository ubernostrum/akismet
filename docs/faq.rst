.. faq:

Frequently asked questions
==========================

The following notes answer common questions, and may be useful to you
when using `akismet`.


What versions of Python are supported?
--------------------------------------

The |release| release of `akismet` supports the following versions of
Python:

* Python 3.7

* Python 3.8

* Python 3.9

* Python 3.10

Older versions of Python are not supported and will cause errors.


Do I have to send all the optional arguments?
---------------------------------------------

The Akismet web service supports a large number of optional arguments
to provide additional information for classification and training. You
can :ref:`send these arguments <optional-arguments>` when calling
:meth:`~akismet.Akismet.comment_check`,
:meth:`~akismet.Akismet.submit_spam`, or
:meth:`~akismet.Akismet.submit_ham`. The Akismet documentation
recommends sending as much information as possible, though only the
`user_ip` and `user_agent` arguments to those methods are actually
required.


Is this only for blog comments?
-------------------------------

The Akismet web service can handle many types of user-submitted
content, including comments, contact-form submissions, user signups
and more. See :ref:`the documentation of optional arguments
<optional-arguments>` for details on how to indicate the type of
content you're sending to Akismet.


How can I test that it's working?
---------------------------------

If you want to verify `akismet` itself, you can run the test suite;
`akismet` uses `tox <https://tox.readthedocs.io/en/latest/>`_ for
testing against the full list of supported Python versions, and
installs all test dependencies into the `tox` virtualenvs.

Running the test suite requires two environment variables to be set:

* `TEST_AKISMET_API_KEY` containing your Akismet API key, and

* `TEST_AKISMET_BLOG_URL` containing the URL associated with your
  API key.

This allows the test suite to access the live Akismet web service to
verify functionality. Then you can invoke the test suite for the
version of Python you intend to use. For example, to test on Python
3.7:

.. code-block:: shell

   $ tox -e py37

If you want to manually perform your own tests, you can also
instantiate the :class:`~akismet.Akismet` class and call its
methods. When doing so, it is recommended that you pass the optional
keyword argument `is_test=1` to the
:meth:`~akismet.Akismet.comment_check`,
:meth:`~akismet.Akismet.submit_spam`, or
:meth:`~akismet.Akismet.submit_ham` methods; this tells the Akismet
web service that you are only issuing requests for testing purposes,
and will not result in any submissions being incorporated into
Akismet's training corpus.


What user-agent string is sent by `akismet`?
----------------------------------------------

The Akismet web service documentation recommends sending a string
identifying the application or platform with version, and Akismet
plugin/implementation name with version. In accordance with this,
`akismet` sends an HTTP `User-Agent` based on the versions of Python
and `akismet` in use. For example, `akismet` 1.1 on Python 3.7 will
send `Python/3.7 | akismet.py/1.1`.


Does `akismet` support the "pro-tip" header?
----------------------------------------------

For content determined to be "blatant" spam (and thus which does not
need to be placed into a queue for review by a human), the Akismet web
service will add the header `X-akismet-pro-tip: discard` to its
comment-check response.

Currently, `akismet` does not recognize or expose the presence of this
header, though a future version may do so.


How am I allowed to use this module?
------------------------------------

`akismet` is distributed under a `three-clause BSD license
<http://opensource.org/licenses/BSD-3-Clause>`_. This is an
open-source license which grants you broad freedom to use,
redistribute, modify and distribute modified versions of
`akismet`. For details, see the file `LICENSE` in the source
distribution of `akismet`.


I found a bug or want to make an improvement!
---------------------------------------------

The canonical development repository for `akismet` is online at
<https://github.com/ubernostrum/akismet>. Issues and pull requests can
both be filed there.
