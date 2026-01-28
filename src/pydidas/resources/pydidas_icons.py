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
Module with access to pydidas icons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "ICON_PATH",
    "pydidas_icon_with_bg",
    "pydidas_error_icon",
    "pydidas_error_icon_with_bg",
    "create_pydidas_icon",
    "create_mdi_icon",
]


from pathlib import Path

from qtpy import QtCore, QtGui

from pydidas.core import UserConfigError


ICON_PATH = Path(__file__).parent / "icons"
MDI_ICON_PATH = Path(__file__).parent / "mdi_icons"


def pydidas_icon() -> QtGui.QIcon:
    """Create a QIcon from the pydidas icon."""
    return QtGui.QIcon(str(ICON_PATH / "pydidas_snakes.svg"))


def pydidas_icon_with_bg() -> QtGui.QIcon:
    """Create a QIcon from the pydidas icon with a white background."""
    return QtGui.QIcon(str(ICON_PATH / "pydidas_snakes_w_bg.svg"))


def pydidas_error_icon() -> QtGui.QIcon:
    """Create a QIcon from the icon for a pydidas error with transparent background."""
    return QtGui.QIcon(str(ICON_PATH / "pydidas_error.svg"))


def pydidas_error_icon_with_bg() -> QtGui.QIcon:
    """Create a QIcon from the icon for a pydidas error with a white background."""
    return QtGui.QIcon(str(ICON_PATH / "pydidas_error_w_bg.svg"))


def create_pydidas_icon(icon_name: str) -> QtGui.QIcon:
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
    if (ICON_PATH / icon_name).is_file():
        _filenames = [ICON_PATH / icon_name]
    else:
        _filenames = list(ICON_PATH.glob(f"{icon_name}.*"))
    if len(_filenames) == 0:
        raise FileNotFoundError(f"Could not find the icon with the name {icon_name}")
    if len(_filenames) > 1:
        raise ValueError(f"Found multiple icons with the name {icon_name}")
    _filename = _filenames[0]
    if _filename.suffix == ".svg":
        return _create_icon_from_svg(_filename)
    return QtGui.QIcon(str(_filename))


def create_mdi_icon(icon_name: str) -> QtGui.QIcon:
    """
    Create a QIcon from the given MDI icon_name.

    Note that not all MDI icons are included in pydidas and this function
    will only work for those icons which have been included.

    Parameters
    ----------
    icon_name : str
        The name of the icon. This is equivalent to the filename
        without the suffix.

    Returns
    -------
    QtGui.QIcon
        The QIcon created from the MDI icon file.
    """
    _fname = (MDI_ICON_PATH / icon_name).with_suffix(".svg")
    if not _fname.is_file():
        raise UserConfigError(
            f"Could not find MDI icon with name {icon_name}. Please check that "
            "the icon has been included in pydidas."
        )
    return _create_icon_from_svg(_fname)


def _create_icon_from_svg(path: Path | str) -> QtGui.QIcon:
    """Create a QIcon from a svg image at the given path."""
    icon = QtGui.QIcon()
    icon.addFile(str(path), QtCore.QSize(128, 128))
    return icon
