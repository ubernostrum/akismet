.. _testing:

Testing guide
=============

A standard install of ``akismet`` does not install the test suite; you will
need to perform :ref:`a source checkout as described in the installation guide
<source-install>`, though performing the "editable" install step is not
necessary for running the tests.

``akismet``'s testing tasks are run using `nox <https://nox.thea.codes/>`_, so
you will also need to install it, after which you can run ``nox``, which should
be done from the root of your git checkout of ``akismet``:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install --upgrade nox
      python -m nox

.. tab:: Windows

   .. code-block:: shell

      py -m pip install --upgrade nox
      py -m nox

Note that to run the full test matrix you will need to have each supported
version of Python available. To run only the subset of test tasks for a
specific Python version, pass the ``--python`` flag with a version number. For
example, to run tasks for Python 3.10 only, you could run:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --python "3.10"

.. tab:: Windows

   .. code-block:: shell

      py -m nox --python "3.10"

By default, ``nox`` will only run the tasks whose associated Python versions
are available on your system. For example, if you have only Python 3.8 and 3.9
installed, test runs for Python 3.10, 3.11, and 3.12 would be skipped. To
install and manage multiple versions of Python, tools like `pyenv
<https://github.com/pyenv/pyenv>`_ or `asdf <https://asdf-vm.com>`_ are
recommended.

To see a list of all available test tasks, run:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --list

.. tab:: Windows

   .. code-block:: shell

      py -m nox --list

All test tasks defined for ``akismet`` are also categorized with tags, which
``nox`` understands and can use. For example, to run just the standard
unit-test suite and no other tasks:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --tag tests

.. tab:: Windows

   .. code-block:: shell

      py -m nox --tag tests

Other useful tags are: ``docs`` (documentation build and checks);
``formatters`` (code-formatting checks); ``linters`` (code linters);
``security`` (security checks); and ``packaging`` (tests for the packaging
configuration and build).

The test suite makes significant use of custom HTTP clients, relying on the
``httpx`` package's `mock HTTP transport
<https://www.python-httpx.org/advanced/#mock-transports>`_ to generate test
responses without needing to contact the live Akismet web service, so setting
the environment variables for your Akismet API key and site URL is not
necessary to run the normal test suite.

However, there is a separate test file -- found at ``tests/end_to_end.py`` --
which is not run as part of the usual test suite invoked by ``nox`` and which
makes live requests to Akismet. Running the tests in that file *does* require
setting the ``PYTHON_AKISMET_API_KEY`` and ``PYTHON_AKISMET_BLOG_URL``
environment variables to valid values, after which you can run the end-to-end
tests by invoking ``nox`` and asking it to run tasks with the keyword
``release`` (normally this test file is only run as a final check prior to
issuing a new release, hence the keyword name):

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m nox --keyword release

.. tab:: Windows

   .. code-block:: shell

      py -m nox --keyword release

If you also want to manually perform your own tests, you can instantiate an
Akismet client class and call its methods to communicate with the live Akismet
web service. When doing so, it is recommended that you pass the optional
keyword argument ``is_test=1`` to the comment-check, submit-ham, and
submit-spam operations; this tells the Akismet web service that you are only
issuing requests for testing purposes, and will not result in any submissions
being incorporated into Akismet's training corpus.
