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
Module with the GlobalConfigWindow class which is a QMainWindow widget
to view and modify the global settings in a dedicatd window.
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
]

import os

from qtpy import QtCore


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
