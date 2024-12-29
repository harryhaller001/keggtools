"""sphinx docs configuration."""

import os
from datetime import datetime
import sys

# Import version from package
from keggtools import __version__


# https://github.com/sphinx-doc/sphinx/issues/4317
sys.path.insert(0, os.path.abspath("../"))


project = "keggtools"
author = "harryhaller001"
copyright = f"{datetime.now():%Y}, {author}."
version = __version__
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "nbsphinx",
]

nbsphinx_execute = "never"

# Mapping for intersphinx extension
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/dev", None),
}


source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"


exclude_trees = ["_build", "cloudflare-workers", "dist", "data"]

exclude_patterns = [
    "wrangler.toml",
    "wrangler.toml.example",
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "*.sqlite",
    "data",
]

# Generate the API documentation when building
autosummary_generate = True
autodoc_member_order = "bysource"
autoapi_dirs = ["../keggtools"]

# Configuration of sphinx.ext.coverage
coverage_show_missing_items = True


html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]

html_show_sphinx = False
html_context = {
    "display_github": True,
    "github_user": "harryhaller001",
    "github_repo": "keggtools",
    "github_version": "main",
    "conf_py_path": "/docs/",
}
