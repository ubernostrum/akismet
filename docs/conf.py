"""
Configuration file for the Sphinx documentation builder:

https://www.sphinx-doc.org/

"""

import sys
from importlib.metadata import version as get_version

extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "akismet"
copyright = "Michael Foord, James Bennett, and contributors"
version = get_version("akismet")
release = version
exclude_trees = ["_build"]
pygments_style = "sphinx"
htmlhelp_basename = "akismetdoc"
latex_documents = [
    (
        "index",
        "akismet.tex",
        "akismet Documentation",
        "Michael Foord and James Bennett",
        "manual",
    ),
]
html_theme = "furo"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Spelling check needs an additional module that is not installed by default.
# Add it only if spelling check is requested so docs can be generated without it.
if "spelling" in sys.argv:
    extensions.append("sphinxcontrib.spelling")

# Spelling language.
spelling_lang = "en_US"

# Location of word list.
spelling_word_list_filename = "spelling_wordlist.txt"

# OGP metadata configuration.
ogp_enable_meta_description = True
ogp_site_url = "https://akismet.readthedocs.io/"
