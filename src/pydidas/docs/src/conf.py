# This file is part of pydidas.
#
# Copyright 2021 - 2025, Helmholtz-Zentrum Hereon
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

import importlib
import os
import sys
from pathlib import Path


sys.path.insert(0, os.path.abspath("./../../.."))
sys.path.insert(0, os.path.abspath("./../.."))


# -- Project information -----------------------------------------------------

project = "pydidas"
copyright = "2021 - 2025, Helmholtz-Zentrum Hereon"
author = "Malte Storm"


# The full version, including alpha/beta/rc tags
with open(Path(__file__).parents[2].joinpath("version.py"), "r") as f:
    _lines = f.readlines()

    for _line in _lines:
        if _line.startswith("__version__"):
            pydidas_version = _line.split("=")[1].strip()
            break

release = pydidas_version.strip("\"'")
version = release

spec = importlib.util.spec_from_file_location(
    "generic_params", "../../core/generic_params/generic_params.py"
)
generic_params = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generic_params)

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
    "sphinx_design",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []
tls_verify = False
add_function_parentheses = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the
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
    "use_edit_page_button": True,
}
if os.getenv("GITHUB_ACTIONS", "false") == "true":
    html_theme_options["switcher"] = {
        "version_match": pydidas_version,
        "json_url": (
            "https://raw.githubusercontent.com/hereon-GEMS/pydidas/"
            "gh-pages-version-snapshots/pydata_version_switcher.json"
        ),
    }
    html_theme_options["navbar_end"] = [
        "version-switcher",
        "theme-switcher",
        "navbar-icon-links",
    ]


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_show_sourcelink = True
html_logo = "./images/logo/pydidas_snakes_circ_bg.png"
html_title = "pydidas"
html_context = {
    "github_url": "https://github.com",
    "github_user": "hereon-GEMS",
    "github_repo": "pydidas",
    "github_version": "master",
    "doc_path": "pydidas/docs/src",
}

# dynamically create documentation for generic parameters:
_fname = Path(__file__).parent / "dev_guide" / "dev_guide_list_of_generic_params.rst"
generic_params.create_generic_params_rst_docs(_fname)


def setup(app):
    app.add_css_file("_css/pydidas-custom.css")
