# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""
The get_documentation_targets module includes functions to get the directories or
URLs for the documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "DOC_BUILD_PATH",
    "DOC_SOURCE_DIRECTORY",
    "DOC_HOME_FILENAME_STR",
    "DOC_HOME_ADDRESS",
    "DOC_HOME_QURL",
    "doc_qurl_for_gui_manual",
    "doc_path_for_gui_manual",
    "doc_qurl_for_rel_address",
]


from pathlib import Path
from typing import Literal

from qtpy import QtCore

from pydidas.core.utils.file_utils import path_as_formatted_str


def doc_qurl_for_gui_manual(
    name: str, class_type: Literal["frame", "window"]
) -> QtCore.QUrl:
    """
    Get the QUrl for the window manual HTML file.

    Parameters
    ----------
    name : str
        The class name of the window.
    class_type : Literal["frame", "window"], optional
        The type of the class for which the manual is requested. This can be either
        "frame" or "window".

    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the encoded path to the window manual.
    """
    _fname = path_as_formatted_str(doc_path_for_gui_manual(name, class_type))
    return QtCore.QUrl(f"file:///{_fname}")


def doc_path_for_gui_manual(name: str, class_type: Literal["frame", "window"]) -> Path:
    """
    Get the file system path for the filename of the manual for the given window class.

    Parameters
    ----------
    name : str
        The class name of the window.
    class_type : Literal["frame", "window"], optional
        The type of the class for which the manual is requested. This can be either
        "frame" or "window".

    Returns
    -------
    Path
        The full filename for the window manual.
    """
    _doc_dir = DOC_BUILD_PATH / "html" / "manuals" / "gui" / f"{class_type}s"
    return _doc_dir / f"{name}.html"


def doc_qurl_for_rel_address(rel_address: str | Path) -> QtCore.QUrl:
    """
    Get the QUrl for a relative address in the documentation.

    Parameters
    ----------
    rel_address : str or Path
        The relative address to the documentation file starting from the
        build directory.

    Returns
    -------
    QtCore.QUrl
        The QUrl object with the encoded path to the documentation file.
    """
    if isinstance(rel_address, Path):
        rel_address = str(rel_address)
    _path = path_as_formatted_str(DOC_BUILD_PATH / "html" / rel_address)
    return QtCore.QUrl(f"file:///{_path}")


DOC_BUILD_PATH = Path(__file__).parents[2] / "sphinx"
DOC_SOURCE_DIRECTORY = Path(__file__).parents[2] / "docs"
DOC_HOME_FILENAME_STR = path_as_formatted_str(DOC_BUILD_PATH / "html" / "index.html")
DOC_HOME_ADDRESS = f"file:///{DOC_HOME_FILENAME_STR}"
DOC_HOME_QURL = QtCore.QUrl(DOC_HOME_ADDRESS)
