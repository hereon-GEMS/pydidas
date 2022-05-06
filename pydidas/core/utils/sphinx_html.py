# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The run_sphinx_html module includes functions to check whether the Sphinx
documentation exists or whether it needs to be created and a function to
generate the Sphinx html documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["check_sphinx_html_docs", "run_sphinx_html_build"]

import os
import sys
import subprocess

from .get_documentation_targets import get_doc_make_directory, get_doc_home_filename


def check_sphinx_html_docs(doc_dir=None):
    """
    This functions checks whether the index.html file for the built sphinx
    documentation exists or is in the process of being created and calls the
    builder if neither check is true.

    Parameters
    ----------
    build_dir : Union[pathlib.Path, str, None], optional
        An optional build directory. If None, this defaults to the generic
        pydidas documentation directory. The default is None.

    Returns
    -------
    bool :
        Flag whether the Sphinx documentation exists or is being built. If
        either of these cases is true, the function will return True. Else,
        it will return a False which can trigger a call to build the
        documentation.
    """
    _sphinx_running = "sphinx-build" in sys.argv[0]
    if doc_dir is None:
        _index_file = get_doc_home_filename()
    else:
        _index_file = os.path.join(doc_dir, "index.html")
    if not os.path.exists(_index_file) and not _sphinx_running:
        return False
    return True


def run_sphinx_html_build(build_dir=None, verbose=True):
    """
    Run the sphinx process to generate the html documentation.

    Parameters
    ----------
    build_dir : Union[pathlib.Path, str, None], optional
        An optional build directory. If None, this defaults to the generic
        pydidas documentation directory. The default is None.
    verbose : bool, optional
        Flag to control printing of a message. The default is True.
    """
    if build_dir is None:
        build_dir = get_doc_make_directory()
    if verbose:
        print("=" * 60)
        print("-" * 60)
        print("----- The html documentation has not yet been created! -----")
        print("----- Running sphinx-build. This may take a bit.       -----")
        print("----- pydidas will automatically load once building of -----")
        print("----- the documentation has been finished.             -----")
        print("-" * 60)
        print("=" * 60)
    if sys.platform in ["win32", "win64"]:
        subprocess.call([os.path.join(build_dir, "make.bat"), "html"])
    else:
        subprocess.call(["make", "-C", build_dir, "html"])
