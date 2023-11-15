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


How can I test that it's working?
---------------------------------

``akismet``'s tests are run using `nox <https://nox.thea.codes/>`_, but typical
installation of ``akismet`` (via ``pip install akismet``) will not install the
tests.

To run the tests, download the source (``.tar.gz``) distribution of ``akismet``
|release| from `its page on the Python Package Index
<https://pypi.org/project/akismet/>`_, unpack it (``tar zxvf
akismet-|version|.tar.gz`` on most Unix-like operating systems), and in the
unpacked directory run the following at a command prompt:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install nox
      python -m nox

.. tab:: Windows

   .. code-block:: shell

      py -m pip install nox
      py -m nox

Note that to run the full test matrix you will need to have each supported
version of Python available. To run only specific test tasks, you can invoke
``nox`` with the ``-s`` flag to select a single test task, ``-t`` to run all
tasks matching a particular tag (like ``docs``), or ``--python`` passing a
Python version to run only tasks for that version. For example, to run tests
for Python 3.10 only, you could run:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --python "3.10"

.. tab:: Windows

   .. code-block:: shell

      py -m nox --python "3.10"

By default, ``nox`` will only run the tasks whose associated Python versions
are available on your system. For example, if you have only Python 3.8 and 3.9
installed, test runs for Python 3.7, 3.10, and 3.11 would be skipped.

Running the test suite also requires two environment variables to be set:

* ``TEST_AKISMET_API_KEY`` containing your Akismet API key, and

* ``TEST_AKISMET_BLOG_URL`` containing the URL associated with your API key.

This allows the test suite to access the live Akismet web service to verify
functionality.

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
example, ``akismet`` 1.3 on Python 3.10.4 will send ``akismet/1.3 | Python
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
