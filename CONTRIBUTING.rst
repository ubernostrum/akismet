Contributor guide
=================

Contributions are welcome, and several things about this repository
have been set up to make the process easier for everyone (including
you!).


Prerequisites
-------------

* Please use a code editor/IDE that supports `EditorConfig
  <https://editorconfig.org>`_. Most editors do nowadays, so you
  probably don't have to worry about it, but it will help to
  automatically apply some formatting and style rules.

* Please make sure you have `pre-commit <https://pre-commit.com>`_
  installed, and in your local checkout of this repository run
  ``pre-commit install`` to set up the pre-commit hooks.

The following two tools are *required* for working with this
repository:

* `PDM <https://pdm-project.org/>`_

* `nox <https://nox.thea.codes/en/stable/>`_

It is strongly *recommended* that you also have ``make`` installed, as
there is a ``Makefile`` provided which can perform some common dev tasks
for you.

You will also need at least one supported Python version. It is also
recommended that you test against *all* the supported Python verisions
before opening a pull request; you can use `PDM's Python installer
<https://pdm-project.org/latest/usage/project/#install-python-interpreters-with-pdm>`_
to install any versions of Python you need.


Local setup
-----------

Once you have the tools above installed, run the following in the root
of your git checkout::

   make install

This will create a local virtual environment and install
``akismet`` and its dependencies.

If you do not have ``make`` available, you can also run ``pdm install`` and
``pre-commit install`` to achieve the same result.


Testing
-------

To run the tests, run ``make test`` if you have ``make``, or invoke
``nox`` directly::

   nox --tags tests

By default this will run against as many supported Python versions as
you have installed. To select a single specific Python version, you
can run::

   nox --tags tests --python "3.11"

You can also run the full CI suite locally by running ``make ci`` or
``nox``. This will run the tests, check the documentation, lint the
code and check formatting, and build a package and perform checks on
it.

For more information about available ``make`` tasks, run ``make help``.

For more information about available ``nox`` tasks, run ``nox --list``
or read the file ``noxfile.py`` in the root of your source checkout, or the
testing documentation in the file ``docs/testing.rst``.


Code style
----------

The pre-commit hooks will auto-format code with `isort
<https://pycqa.github.io/isort/>`_ and `Black
<https://black.readthedocs.io/>`_. Many editors and IDEs also support
auto-formatting with these tools every time you save a file. The CI
suite will disallow any code that does not follow the isort/Black
format.

All code must also be compatible with all supported versions of
Python.


Other guidelines
----------------

* If you need to add a new file of code, please make sure to put a
  license identifier comment near the top of the file. You can copy
  and paste the license identifier comment from any existing file,
  where it looks like this:
  ``# SPDX-License-Identifier: BSD-3-Clause``

* Documentation and tests are not just recommended -- they're
  required. Any new file, class, method or function must have a
  docstring and must either include that docstring (via autodoc) in
  the built documentation, or must have manually-written documentation
  in the ``docs/`` directory. Any new feature or bugfix must have
  sufficient tests to prove that it works, and the test coverage
  report must come out at 100%. The CI suite will fail if test
  coverage is below 100%, if there's any code which doesn't have a
  docstring, or if there are any misspelled words in the documentation
  (and if there's a word the spell-checker should learn to recognize,
  add it to ``docs/spelling_wordlist.txt``).
