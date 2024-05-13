"""
Library version number.

"""

# SPDX-License-Identifier: BSD-3-Clause

# This is set here instead of in common.py or __init__.py because it's read dynamically
# by setuptools during the package build, and both common.py and __init__.py (which
# imports common.py) need to import the third-party httpx library, which is not
# available during package build (it only becomes available after package install).
LIBRARY_VERSION = "24.5.1"
