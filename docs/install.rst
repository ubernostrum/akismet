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

To install the latest stable released version of ``akismet``, run the following
command from a command prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install --upgrade akismet

.. tab:: Windows

   .. code-block:: shell

      py -m pip install --upgrade akismet

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


.. _source-install:

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
