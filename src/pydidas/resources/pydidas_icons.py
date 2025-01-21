# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with access to pydidas icons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "ICON_PATH",
    "pydidas_icon_with_bg",
    "get_pydidas_qt_icon",
    "pydidas_error_icon",
    "pydidas_error_icon_with_bg",
    "get_pydidas_qt_icon",
    "get_mdi_qt_icon",
]


import os
from pathlib import Path
from typing import Union

from qtpy import QtCore, QtGui


ICON_PATH = Path(__file__).parent.joinpath("icons")


def __icon_path_str(icon_name: str) -> str:
    """
    Get the path to the icon with the given name.

    Parameters
    ----------
    icon_name : str
        The icon name.

    Returns
    -------
    str
        The path to the icon.
    """
    return str(ICON_PATH.joinpath(icon_name))


def pydidas_icon() -> QtGui.QIcon:
    """
    Get the pydidas icon.

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas icon.
    """
    return QtGui.QIcon(__icon_path_str("pydidas_snakes.svg"))


def pydidas_icon_with_bg() -> QtGui.QIcon:
    """
    Get the pydidas icon with a white background (with rounded corners).

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas con with background.
    """
    return QtGui.QIcon(__icon_path_str("pydidas_snakes_w_bg.svg"))


def pydidas_error_icon() -> QtGui.QIcon:
    """
    Get the icon for a pydidas error.

    Returns
    -------
    icon : QtGui.QIcon
        A QIcon with the pydidas error icon.
    """
    return QtGui.QIcon(__icon_path_str("pydidas_error.svg"))


def pydidas_error_icon_with_bg() -> QtGui.QIcon:
    """
    Get the icon for a pydidas error with a white background.

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas error icon with background.
    """
    return QtGui.QIcon(__icon_path_str("pydidas_error_w_bg.svg"))


def get_pydidas_qt_icon(icon_name: str) -> QtGui.QIcon:
    """
    Get the QIcon from the file with the given name.

    Parameters
    ----------
    icon_name : str
        The icon name. The file extension is automatically added.

    Returns
    -------
    QtGui.QIcon
        The QIcon created from the image file.
    """
    _fnames = [_name for _name in os.listdir(ICON_PATH) if _name.startswith(icon_name)]
    if len(_fnames) == 0:
        raise FileNotFoundError(f"Could not find the icon with the name {icon_name}")
    if len(_fnames) > 1:
        raise ValueError(f"Found multiple icons with the name {icon_name}")
    _filename = __icon_path_str(_fnames[0])
    if _filename.endswith(".svg"):
        return __load_svg_icon(_filename)
    return QtGui.QIcon(_filename)


def get_mdi_qt_icon(filename: str) -> QtGui.QIcon:
    """
    Get the QIcon from the file with the given name.

    Parameters
    ----------
    filename : str
        The filename of the mdi icon.

    Returns
    -------
    QtGui.QIcon
        The QIcon created from the mdi icon file.
    """
    _path = __icon_path_str(filename + ".svg").replace("icons", "mdi_icons")
    return __load_svg_icon(_path)
    # return QtGui.QIcon(os.path.join(ICON_PATH.replace("icons", "mdi_icons"), filename))


def __load_svg_icon(path: Union[Path, str]) -> QtGui.QIcon:
    """
    Load an svg icon from the given path.

    Parameters
    ----------
    path : Union[Path, str]
        The path to the svg icon.

    Returns
    -------
    QtGui.QIcon
        The icon.
    """
    icon = QtGui.QIcon()
    icon.addFile(str(path), QtCore.QSize(128, 128))
    return icon
