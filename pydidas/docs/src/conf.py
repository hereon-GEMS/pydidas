# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
from pathlib import Path


sys.path.insert(0, os.path.abspath("./../../.."))
sys.path.insert(0, os.path.abspath("./../.."))


# -- Project information -----------------------------------------------------

project = "pydidas"
copyright = "2023 - 2024, Helmholtz-Zentrum Hereon"
author = "Malte Storm"


# The full version, including alpha/beta/rc tags
with open(Path(__file__).parents[2].joinpath("version.py"), "r") as f:
    _lines = f.readlines()

    for _line in _lines:
        if _line.startswith("__version__"):
            pydidas_version = _line.split("=")[1].strip()
            break

release = pydidas_version
version = release

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []
tls_verify = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the
# documentation.
#
# nature scheme options
# html_theme_options = {'sidebarwidth': '350px',
#                       "body_min_width": 800,
#                      }
html_theme_options = {
    "analytics_id": "G-XXXXXXXXXX",  # Provided by Google in your dashboard
    "analytics_anonymize_ip": False,
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#4444AA",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 5,
    "includehidden": True,
    "titles_only": False,
    # manual options
    "body_min_width": 800,
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "./images/logo/pydidas_snakes_circ_bg.png"
html_title = "pydidas"


def setup(app):
    app.add_css_file("_css/pydidas-custom.css")
