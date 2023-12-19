# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
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
]


import os
from pathlib import Path

from qtpy import QtGui


ICON_PATH = str(Path(__file__).parent.joinpath("icons"))


def pydidas_icon() -> QtGui.QIcon:
    """
    Get the pydidas icon.

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas icon.
    """
    return QtGui.QIcon(os.path.join(ICON_PATH, "pydidas_snakes.svg"))


def pydidas_icon_with_bg() -> QtGui.QIcon:
    """
    Get the pydidas icon with a white background (with rounded corners).

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas con with background.
    """
    return QtGui.QIcon(os.path.join(ICON_PATH, "pydidas_snakes_w_bg.svg"))


def pydidas_error_icon() -> QtGui.QIcon:
    """
    Get the icon for a pydidas error.

    Returns
    -------
    icon : QtGui.QIcon
        A QIcon with the pydidas error icon.
    """
    return QtGui.QIcon(os.path.join(ICON_PATH, "pydidas_error.svg"))


def pydidas_error_icon_with_bg() -> QtGui.QIcon:
    """
    Get the icon for a pydidas error with a white background.

    Returns
    -------
    QtGui.QIcon
        A QIcon with the pydidas error icon with background.
    """
    return QtGui.QIcon(os.path.join(ICON_PATH, "pydidas_error_w_bg.svg"))


def get_pydidas_qt_icon(filename) -> QtGui.QIcon:
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
    return QtGui.QIcon(os.path.join(ICON_PATH, filename))
