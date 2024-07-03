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

import requests


sys.path.insert(0, os.path.abspath("./../../.."))
sys.path.insert(0, os.path.abspath("./../.."))


def is_on_github_actions():
    """
    Check if the current build is running on GitHub Actions.

    The code is adapted  from the discussion at:
    https://github.com/orgs/community/discussions/49224

    Returns
    -------
    bool
        True if the build is running on GitHub Actions, False otherwise.
    """
    if (
        "CI" not in os.environ
        or not os.environ["CI"]
        or "GITHUB_RUN_ID" not in os.environ
    ):
        return False

    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
    url = (
        "https://api.github.com/repos/"
        f"{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    )
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and "workflow_runs" in response.json()


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
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []
tls_verify = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # Toc options
    "collapse_navigation": True,
    "navigation_depth": 5,
    # manual options
    "body_min_width": 800,
    # pydata scheme options:
    "show_version_warning_banner": True,
    "github_url": "https://github.com/hereon-GEMS/pydidas",
    "logo": {
        "text": " pydidas",
        "alt_text": "pydidas",
    },
}
if is_on_github_actions():
    html_theme_options["switcher"] = {
        "version_match": pydidas_version.strip("\"'"),
        "json_url": (
            "https://raw.githubusercontent.com/hereon-GEMS/pydidas/"
            "_gh_pages_release_versions/pydata_version_switcher.json"
        ),
    }
    html_theme_options["navbar_end"] = ["version-switcher", "navbar-icon-links"]


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "./images/logo/pydidas_snakes_circ_bg.png"
html_title = "pydidas"


def setup(app):
    app.add_css_file("_css/pydidas-custom.css")
