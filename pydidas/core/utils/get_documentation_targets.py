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
    "get_doc_make_directory",
    "get_doc_home_filename",
    "get_doc_home_address",
    "get_doc_home_qurl",
    "get_doc_directory_for_frame_manuals",
    "get_doc_filename_for_frame_manual",
    "get_doc_qurl_for_frame_manual",
]

import os

from qtpy import QtCore


def get_doc_qurl_for_frame_manual(name):
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
    _path = get_doc_filename_for_frame_manual(name)
    _url = QtCore.QUrl("file:///" + _path.replace("\\", "/"))
    return _url


def get_doc_filename_for_frame_manual(name):
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
    return os.path.join(get_doc_directory_for_frame_manuals(), f"{name}.html")


def get_doc_directory_for_frame_manuals():
    """
    Get the directory with the html documentation for the individual frames.

    Returns
    -------
    str
        The directory name of the directory with the html manuals for the individual
        frames.
    """
    _docdir = os.path.join(
        get_doc_make_directory(), "build", "html", "manuals", "frames"
    )
    return _docdir


def get_doc_home_qurl():
    """
    Get the full filepath & -name of the index.html for the pydidas
    documentation.

    Returns
    -------
    url : QtCore.QUrl
        The QUrl object with the path to the index.html file.
    """
    return QtCore.QUrl(get_doc_home_address())


def get_doc_home_address():
    """
    Get the pydidas documentation home address in a browser-readable format.

    Returns
    -------
    _address : str
        The address of the documentation index.html.
    """
    _address = "file:///" + get_doc_home_filename()
    _address = _address.replace("\\", "/")
    return _address


def get_doc_home_filename():
    """
    Get the filename of the pydidas documentation homepage.

    Returns
    -------
    _docfile : str
        The full path and filename of the index.html file.
    """
    _docfile = os.path.join(get_doc_make_directory(), "build", "html", "index.html")
    return _docfile


def get_doc_make_directory():
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
