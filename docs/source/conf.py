# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "configoose"
copyright = "2024, Eric Ringeisen"
author = "Eric Ringeisen"
release = "2024.06.03"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# 'sphinx.ext.autodoc' enables directives such as ..automodule
extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]


# this is to enable the autodoc feature as described in:
# https://sphinx-rtd-tutorial.readthedocs.io/en/latest/sphinx-config.html
import os
import sys

sys.path.insert(0, os.path.abspath("../../src/configoose"))

autodoc_default_options = {
    "members": True,
    "special-members": "__call__",
}
