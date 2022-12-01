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
The get_documentation_targets module includes functions to get the directories or
URLs for the documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "DOC_MAKE_DIRECTORY",
    "DOC_HOME_FILENAME",
    "DOC_HOME_ADDRESS",
    "DOC_HOME_QURL",
    "doc_filename_for_frame_manual",
    "doc_qurl_for_frame_manual",
    "doc_qurl_for_window_manual",
    "doc_filename_for_window_manual",
]


import os

from qtpy import QtCore


def doc_qurl_for_window_manual(name):
    """
    Get the QUrl for the window manual html file.

    Parameters
    ----------
    name : str
        The class name of the window.

    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the encoded path to the window manual.
    """
    _path = doc_filename_for_window_manual(name).replace("\\", "/")
    _url = QtCore.QUrl("file:///" + _path)
    return _url


def doc_filename_for_window_manual(name):
    """
    Get the file system path for the filename of the manual for the given window class.

    Parameters
    ----------
    name : str
        The class name of the window.

    Returns
    -------
    str
        The full filename for the window manual.
    """
    _docdir = os.path.join(
        DOC_MAKE_DIRECTORY, "build", "html", "manuals", "gui", "windows"
    )
    return os.path.join(_docdir, f"{name}.html")


def doc_qurl_for_frame_manual(name):
    """
    Get the QUrl for the frame manual html.

    Parameters
    ----------
    name : str
        The class name of the Frame.

    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the encoded path to the frame manual.
    """
    _path = doc_filename_for_frame_manual(name)
    _url = QtCore.QUrl("file:///" + _path.replace("\\", "/"))
    return _url


def doc_filename_for_frame_manual(name):
    """
    Get the file system path for the filename of the frame manual for the given class.

    Parameters
    ----------
    name : str
        The class name of the Frame.

    Returns
    -------
    str
        The full filename for the frame manual.
    """
    return os.path.join(
        DOC_MAKE_DIRECTORY, "build", "html", "manuals", "gui", "frames", f"{name}.html"
    )


def _doc_home_address():
    """
    Get the pydidas documentation home address in a browser-readable format.

    Returns
    -------
    _address : str
        The address of the documentation index.html.
    """
    _address = "file:///" + _doc_home_filename()
    _address = _address.replace("\\", "/")
    return _address


def _doc_home_filename():
    """
    Get the filename of the pydidas documentation homepage.

    Returns
    -------
    _docfile : str
        The full path and filename of the index.html file.
    """
    _docfile = os.path.join(_doc_make_directory(), "build", "html", "index.html")
    return _docfile


def _doc_make_directory():
    """
    Get the directory with the documentation make files.

    Returns
    -------
    str
        The directory name of the directory with the make files.
    """
    _name = __file__
    for _ in range(3):
        _name = os.path.dirname(_name)
    return os.path.join(_name, "docs")


def _get_doc_home_qurl():
    """
    Get the full filepath & -name of the index.html for the pydidas
    documentation.
    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the path to the index.html file.
    """
    return QtCore.QUrl(_doc_home_address())


DOC_HOME_QURL = _get_doc_home_qurl()
DOC_MAKE_DIRECTORY = _doc_make_directory()
DOC_HOME_FILENAME = _doc_home_filename()
DOC_HOME_ADDRESS = _doc_home_address()
