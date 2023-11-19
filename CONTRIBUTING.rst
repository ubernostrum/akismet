Contributor guide
=================

Contributions are welcome, and several things about this repository
have been set up to make the process easier for everyone (including
you!).


Dev environment recommendations
-------------------------------

* Please use a code editor/IDE that supports `EditorConfig
  <https://editorconfig.org>`_ Most editors do nowadays, so you
  probably don't have to worry about it, but it will help to
  automatically apply some formatting and style rules.

* Please make sure you have `pre-commit <https://pre-commit.com>`_
  installed, and in your local checkout of this repository run
  ``pre-commit install`` to set up the pre-commit hooks.

* Please have `nox <https://nox.thea.codes/en/stable/>`_ installed on
  your computer, and run at least the unit-test suite (``python -m nox
  --tag tests``) before you push your commits to GitHub. If you can
  manage it, installing the full set of supported Python versions and
  running the entire suite (``python -m nox``) is even better. Tools
  like `pyenv <https://github.com/pyenv/pyenv>`_ or ``asdf
  <https://asdf-vm.com>`_ can help with installing and managing
  multiple Python versions.

Following these steps will catch a lot of potential problems for you,
and can even fix several of them automatically.


Code style
----------

The pre-commit hooks will auto-format code with `isort
<https://pycqa.github.io/isort/>`_ and `Black
<https://black.readthedocs.io/>`_. Most editors and IDEs also support
auto-formatting with these tools every time you save a file. The CI
suite will disallow any code that does not follow the isort/Black
format.

All code must also be compatible with all versions of Python currently
supported by the Python core team. See `the Python dev guide
<https://devguide.python.org/versions/>`_ for a current chart of
supported versions.


Other guidelines
----------------

* If you need to add a new file of code, please make sure to put a
  license identifier comment on the first line after the file's
  docstring. You can copy and paste the license identifier comment
  from any existing file, where it looks like this: ``#
  SPDX-License-Identifier: BSD-3-Clause``

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

* Other than the tests in the special ``tests/end_to_end.py`` file,
  tests for this module must not make real requests to the Akismet web
  service and must not require a valid Akismet API key -- see the
  existing test files for examples of how to write tests that use mock
  responses.
