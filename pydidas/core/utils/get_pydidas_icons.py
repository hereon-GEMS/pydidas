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
Module with functions to get the different pydidas icons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "get_pydidas_icon",
    "get_pydidas_icon_fname",
    "get_pydidas_icon_path",
    "get_pydidas_icon_w_bg",
    "get_pydidas_error_icon",
    "get_pydidas_error_icon_w_bg",
    "get_pydidas_qt_icon",
]

import os

from qtpy import QtGui


def get_pydidas_icon():
    """
    Get the pydidas icon.

    Returns
    -------
    icon : QtGui.QIcon
        The instantiated pydidas icon.
    """
    _icon = QtGui.QIcon(get_pydidas_icon_fname())
    return _icon


def get_pydidas_icon_fname():
    """
    Get the filename for the pydidas icon.

    Returns
    -------
    str
        The full filename and path for the pydidas icon file.
    """
    return os.path.join(get_pydidas_icon_path(), "pydidas_snakes.svg")


def get_pydidas_icon_path():
    """
    Get the file path for the pydidas icons.

    Returns
    -------
    str
        The full path for the pydidas icon files.
    """
    _path = __file__
    for _ in range(2):
        _path = os.path.dirname(_path)
    return os.path.join(_path, "icons")


def get_pydidas_icon_w_bg():
    """
    Get the pydidas icon with a white background (with rounded corners).

    Returns
    -------
    icon : QtGui.QIcon
        The instantiated pydidas icon with a white background.
    """
    _fname = os.path.join(get_pydidas_icon_path(), "pydidas_snakes_w_bg.svg")
    _icon = QtGui.QIcon(_fname)
    return _icon


def get_pydidas_error_icon():
    """
    Get the icon for a pydidas error.

    Returns
    -------
    icon : QtGui.QIcon
        The instantiated pydidas icon.
    """
    _logopath = os.path.join(get_pydidas_icon_path(), "pydidas_error.svg")
    _icon = QtGui.QIcon(_logopath)
    return _icon


def get_pydidas_error_icon_w_bg():
    """
    Get the icon for a pydidas error with a white background.

    Returns
    -------
    icon : QtGui.QIcon
        The instantiated pydidas error icon with background.
    """
    _logopath = os.path.join(get_pydidas_icon_path(), "pydidas_error_w_bg.svg")
    _icon = QtGui.QIcon(_logopath)
    return _icon


def get_pydidas_qt_icon(filename):
    """
    Get the QIcon from the file with the given name.

    Parameters
    ----------
    filename : str
        The filename of the image. Only the filename in the pydidas icon path is
        needed.

    Returns
    -------
    QtGui.QIcon
        The QIcon created from the image file.
    """
    return QtGui.QIcon(os.path.join(get_pydidas_icon_path(), filename))
