"""
Automated testing via nox (https://nox.thea.codes/).

Combined with a working installation of nox (see ``nox`` documentation), this file
specifies a matrix of tests, linters, and other quality checks which can be run
individually or as a suite.

To see available tasks, run ``python -m nox --list``. To run all available tasks --
which requires functioning installs of all supported Python versions -- run ``python -m
nox``. To run a single task, use ``python -m nox --session`` with the name of that task.

"""

import os
import pathlib
import shutil
import typing

import nox

nox.options.default_venv_backend = "venv"
nox.options.keywords = "not release"
nox.options.reuse_existing_virtualenvs = True

PACKAGE_NAME = "akismet"

NOXFILE_PATH = pathlib.Path(__file__).parents[0]
ARTIFACT_PATHS = (
    NOXFILE_PATH / "src" / f"{PACKAGE_NAME}.egg-info",
    NOXFILE_PATH / "build",
    NOXFILE_PATH / "dist",
    NOXFILE_PATH / "__pycache__",
    NOXFILE_PATH / "src" / "__pycache__",
    NOXFILE_PATH / "src" / PACKAGE_NAME / "__pycache__",
    NOXFILE_PATH / "tests" / "__pycache__",
)

TEST_KEY = "INVALID_TEST_KEY"
TEST_URL = "http://example.com"


def clean(paths: typing.Iterable[os.PathLike] = ARTIFACT_PATHS) -> None:
    """
    Clean up after a test run.

    """
    [
        shutil.rmtree(path) if path.is_dir() else path.unlink()
        for path in paths
        if path.exists()
    ]


# Tasks which run the package's test suites.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"], tags=["tests"])
def tests_with_coverage(session: nox.Session) -> None:
    """
    Run the package's unit tests, with coverage report.

    """
    session.install(".[tests]")
    session.run(
        f"python{session.python}",
        "-Wonce::DeprecationWarning",
        "-Im",
        "coverage",
        "run",
        "--source",
        PACKAGE_NAME,
        "-m",
        "unittest",
        "discover",
        env={"PYTHON_AKISMET_API_KEY": TEST_KEY, "PYTHON_AKISMET_BLOG_URL": TEST_URL},
    )
    session.run(
        f"python{session.python}",
        "-Im",
        "coverage",
        "report",
        "--show-missing",
    )
    clean()


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"], tags=["tests", "release"])
def tests_end_to_end(session: nox.Session) -> None:
    """
    Run the end-to-end (live Akismet API) tests.

    """
    session.install(".[tests]")
    session.run(
        f"python{session.python}",
        "-Wonce::DeprecationWarning",
        "-Im",
        "unittest",
        "discover",
        "--pattern",
        "end_to_end*",
        env={
            "PYTHON_AKISMET_API_KEY": os.getenv("PYTHON_AKISMET_API_KEY", ""),
            "PYTHON_AKISMET_BLOG_URL": os.getenv("PYTHON_AKISMET_BLOG_URL", ""),
        },
    )
    clean()


# Tasks which test the package's documentation.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.12"], tags=["docs"])
def docs_build(session: nox.Session) -> None:
    """
    Build the package's documentation as HTML.

    """
    session.install(".[docs]")
    session.chdir("docs")
    session.run(
        f"python{session.python}",
        "-Im",
        "sphinx",
        "-b",
        "html",
        "-d",
        f"{session.bin}/../tmp/doctrees",
        ".",
        f"{session.bin}/../tmp/html",
    )
    clean()


@nox.session(python=["3.12"], tags=["docs"])
def docs_docstrings(session: nox.Session) -> None:
    """
    Enforce the presence of docstrings on all modules, classes, functions, and
    methods.

    """
    # interrogate implicitly depends on pkg_resources, which is part of setuptools but
    # as of Python 3.12, the venv module no longer automatically installed setuptools
    # into newly-created environments. So we install it manually here.
    session.install("interrogate", "setuptools")
    session.run(f"python{session.python}", "-Im", "interrogate", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "interrogate",
        "-v",
        "src/",
        "tests/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.12"], tags=["docs"])
def docs_spellcheck(session: nox.Session) -> None:
    """
    Spell-check the package's documentation.

    """
    session.install(
        "pyenchant",
        "sphinxcontrib-spelling",
        ".[docs]",
    )
    build_dir = session.create_tmp()
    session.chdir("docs")
    session.run(
        f"python{session.python}",
        "-Im",
        "sphinx",
        "-W",  # Promote warnings to errors, so that misspelled words fail the build.
        "-b",
        "spelling",
        "-d",
        f"{build_dir}/doctrees",
        ".",
        f"{build_dir}/html",
        # On Apple Silicon Macs, this environment variable needs to be set so
        # pyenchant can find the "enchant" C library. See
        # https://github.com/pyenchant/pyenchant/issues/265#issuecomment-1126415843
        env={"PYENCHANT_LIBRARY_PATH": os.getenv("PYENCHANT_LIBRARY_PATH", "")},
    )
    clean()


# Code formatting checks.
#
# These checks do *not* reformat code -- that happens in pre-commit hooks -- but will
# fail a CI build if they find any code that needs reformatting.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.12"], tags=["formatters"])
def format_black(session: nox.Session) -> None:
    """
    Check code formatting with Black.

    """
    session.install("black>=24.0,<25.0")
    session.run(f"python{session.python}", "-Im", "black", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "black",
        "--check",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.12"], tags=["formatters"])
def format_isort(session: nox.Session) -> None:
    """
    Check code formating with Black.

    """
    session.install("isort")
    session.run(f"python{session.python}", "-Im", "isort", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "isort",
        "--check-only",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


# Linters.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.12"], tags=["linters", "security"])
def lint_bandit(session: nox.Session) -> None:
    """
    Lint code with the Bandit security analyzer.

    """
    session.install("bandit[toml]")
    session.run(f"python{session.python}", "-Im", "bandit", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "bandit",
        "-c",
        "./pyproject.toml",
        "-r",
        "src/",
        "tests/",
    )
    clean()


@nox.session(python=["3.12"], tags=["linters"])
def lint_flake8(session: nox.Session) -> None:
    """
    Lint code with flake8.

    """
    session.install("flake8", "flake8-bugbear")
    session.run(f"python{session.python}", "-Im", "flake8", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "flake8",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )
    clean()


@nox.session(python=["3.12"], tags=["linters"])
def lint_pylint(session: nox.Session) -> None:
    """
    Lint code with Pylint.

    """
    # Pylint requires that all dependencies be importable during the run. This package
    # does not have any direct dependencies, nor does the normal test suite, but the
    # full conformance suite does require a few extra libraries, so they're installed
    # here.
    session.install("httpx", "pylint")
    session.run(f"python{session.python}", "-Im", "pylint", "--version")
    session.run(f"python{session.python}", "-Im", "pylint", "src/", "tests/")
    clean()


# Packaging checks.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.12"], tags=["packaging"])
def package_build(session: nox.Session) -> None:
    """
    Check that the package builds.

    """
    session.install("build")
    session.run(f"python{session.python}", "-Im", "build", "--version")
    session.run(f"python{session.python}", "-Im", "build")
    clean()


@nox.session(python=["3.12"], tags=["packaging"])
def package_description(session: nox.Session) -> None:
    """
    Check that the package description will render on the Python Package Index.

    """
    package_dir = session.create_tmp()
    session.install("build", "twine")
    session.run(f"python{session.python}", "-Im", "build", "--version")
    session.run(f"python{session.python}", "-Im", "twine", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"python{session.python}", "-Im", "twine", "check", f"{package_dir}/build/*"
    )
    clean()


@nox.session(python=["3.12"], tags=["packaging"])
def package_manifest(session: nox.Session) -> None:
    """
    Check that the set of files in the package matches the set under version control.

    """
    session.install("check-manifest")
    session.run(f"python{session.python}", "-Im", "check_manifest", "--version")
    session.run(f"python{session.python}", "-Im", "check_manifest", "--verbose")
    clean()


@nox.session(python=["3.12"], tags=["packaging"])
def package_pyroma(session: nox.Session) -> None:
    """
    Check package quality with pyroma.

    """
    session.install("pyroma")
    session.run(f"python{session.python}", "-Im", "pyroma", ".")
    clean()


@nox.session(python=["3.12"], tags=["packaging"])
def package_wheel(session: nox.Session) -> None:
    """
    Check the built wheel package for common errors.

    """
    package_dir = session.create_tmp()
    session.install("build", "check-wheel-contents")
    session.run(f"python{session.python}", "-Im", "build", "--version")
    session.run(f"python{session.python}", "-Im", "check_wheel_contents", "--version")
    session.run(
        f"python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"python{session.python}", "-Im", "check_wheel_contents", f"{package_dir}/build"
    )
    clean()
