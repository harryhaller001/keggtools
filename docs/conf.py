"""sphinx docs configuration."""

import os
from datetime import datetime
import sys

# Import version from package
from keggtools import __version__


# https://github.com/sphinx-doc/sphinx/issues/4317
sys.path.insert(0, os.path.abspath("../src/keggtools"))


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
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    # Required for syntax highlighing (https://github.com/spatialaudio/nbsphinx/issues/24)
    "IPython.sphinxext.ipython_console_highlighting",
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


exclude_trees = ["_build", "dist", "data"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "*.sqlite",
    "data",
]


# Generate the API documentation when building
autoapi_type = "python"
autoapi_add_toctree_entry = False
autoapi_ignore: list[str] = ["_*.py"]
autoapi_dirs = ["../src/keggtools"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_member_order = "alphabetical"

autosummary_generate = True

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Configuration of sphinx.ext.coverage
coverage_show_missing_items = True

# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_attr_annotations = True


html_theme = "sphinx_book_theme"
html_theme_options = dict(
    repository_url="https://github.com/harryhaller001/keggtools",
    repository_branch="main",
    use_download_button=True,
    use_fullscreen_button=False,
    use_repository_button=True,
    # collapse_navbar=False,
)

html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
html_title = "keggtools"
html_show_sphinx = False
html_context = dict(
    display_github=True,
    github_user="harryhaller001",
    github_repo="keggtools",
    github_version="main",
    conf_py_path="/docs/",
    github_button=True,
    show_powered_by=False,
)
