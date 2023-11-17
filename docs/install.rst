.. _install:


Installation guide
==================

The |release| version of ``akismet`` is officially tested and supported
on the following versions of Python:

* Python 3.8

* Python 3.9

* Python 3.10

* Python 3.11

* Python 3.12


Installing ``akismet``
----------------------

To install ``akismet``, run the following command from a command
prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install akismet

.. tab:: Windows

   .. code-block:: shell

      py -m pip install akismet

This will use ``pip``, the standard Python package-installation tool. If you
are using a supported version of Python, your installation of Python should
have come with ``pip`` bundled. If ``pip`` does not appear to be present, you
can try running the following from a command prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m ensurepip --upgrade

.. tab:: Windows

   .. code-block:: shell

      py -m ensurepip --upgrade

Instructions are also available for `how to obtain and manually install or
upgrade pip <https://pip.pypa.io/en/latest/installation/>`_.


Configuration
-------------

To use this library, you will need to obtain an Akismet API key and register a site for
use with the Akismet web service; you can do this at <https://akismet.com>. Once you
have a key and corresponding registered site URL to use with it, place them in the
environment variables ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``, and
they will be automatically detected and used.

You can also optionally set the environment variable ``PYTHON_AKISMET_TIMEOUT``
to a :class:`float` or :class:`int` containing a connection-timeout threshold
to use for making requests to the Akismet web service; if not set, this will
default to ``1.0`` (one second).


Installing from a source checkout
---------------------------------

If you want to work on ``akismet``, you can obtain a source checkout.

The development repository for ``akismet`` is at
<https://github.com/ubernostrum/akismet>. If you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the repository by
typing::

    git clone https://github.com/ubernostrum/akismet.git

From there, you can use git commands to check out the specific revision you
want, and perform an "editable" install (allowing you to change code as you
work on it) by typing:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install -e .

.. tab:: Windows

   .. code-block:: shell

      py -m pip install -e .


.. _testing:

Running the test suite
----------------------

A standard install of ``akismet`` does not install the test suite; you will
need to perform a git checkout as described above, though performing the
"editable" install step is not necessary for running the tests.

``akismet``'s tests are run using `nox <https://nox.thea.codes/>`_, so you will
also need to install it, after which you can run the tests:

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
installed, test runs for Python 3.10, 3.11, and 3.12 would be skipped.

Running the test suite also requires two environment variables to be set:

* ``TEST_AKISMET_API_KEY`` containing your Akismet API key, and

* ``TEST_AKISMET_BLOG_URL`` containing the URL associated with your API key.

The test suite makes significant use of custom HTTP clients, relying on the
``httpx`` package's `mock HTPTP transport
<https://www.python-httpx.org/advanced/#mock-transports>`_ to generate test
responses without needing to contact the live Akismet web service.

If you want to manually perform your own tests, you can also instantiate an
Akismet client class and call its methods to communicate with the live Akismet
web service. When doing so, it is recommended that you pass the optional
keyword argument ``is_test=1`` to the comment-check, submit-ham, and
submit-spam operations; this tells the Akismet web service that you are only
issuing requests for testing purposes, and will not result in any submissions
being incorporated into Akismet's training corpus.
