# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Ajouter la racine du projet, app_api et app_front au sys.path pour Sphinx
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../app_api"))
sys.path.insert(0, os.path.abspath("../../app_front"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Toolbox microservice'
copyright = '2026, Nicolas Tchenio'
author = 'Nicolas Tchenio'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # pour docstrings Google
    'sphinx.ext.mathjax',   # Pour latex
    "sphinx.ext.viewcode", # pour afficher code source
    "myst_parser", # pour le markdown
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_logo = "_static/img/logo_toolbox_microservice.jpg"
html_title = "Documentation - Toolbox microservice"
