.. _install:


Installation guide
==================

``akismet`` |version| is officially tested and supported on the
following versions of Python:

* Python 2.7

* Python 3.3

* Python 3.4

* Python 3.5

* Python 3.6


Normal installation
-------------------

The preferred method of installing ``akismet`` is via ``pip``, the
standard Python package-installation tool. If you don't have ``pip``,
instructions are available for `how to obtain and install it
<https://pip.pypa.io/en/latest/installing.html>`_. If you're using
Python 2.7.9 or later (for Python 2) or Python 3.4 or later (for
Python 3), ``pip`` came bundled with your installation of Python.

Once you have ``pip``, simply type::

    pip install akismet


Manual installation
-------------------

It's also possible to install ``akismet`` manually. To do so, obtain
the latest packaged version from `the listing on the Python Package
Index <https://pypi.python.org/pypi/akismet/>`_. Unpack the
``.tar.gz`` file, and run::

    python setup.py install

Once you've installed ``akismet``, you can verify successful
installation by opening a Python interpreter and typing ``import
akismet``.

If the installation was successful, you'll simply get a fresh Python
prompt. If you instead see an ``ImportError``, check the configuration
of your install tools and your Python import path to ensure
``akismet`` installed into a location Python can import from.


Installing from a source checkout
---------------------------------

The development repository for ``akismet`` is at
<https://github.com/ubernostrum/akismet>. Presuming you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the
repository by typing::

    git clone https://github.com/ubernostrum/akismet.git

From there, you can use normal git commands to check out the specific
revision you want, and install it using ``python setup.py install``.