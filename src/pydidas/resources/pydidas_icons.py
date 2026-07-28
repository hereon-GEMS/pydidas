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
from xml.etree import ElementTree

from qtpy import QtCore, QtGui, QtSvg

from pydidas.core import UserConfigError
from pydidas_qtcore import PydidasQApplication


ICON_PATH = Path(__file__).parent / "_icons"
MDI_ICON_PATH = Path(__file__).parent / "_mdi_icons"


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
    _app = PydidasQApplication.instance()
    _dark = _app.is_dark_mode if _app else False
    _color = "#ffffff" if _dark else "#000000"
    _bg_color = "#000000" if _dark else "#ffffff"

    _tree = ElementTree.parse(path)
    _root = _tree.getroot()
    _root.set("fill", _color)
    for elem in _root.iter():
        if "fill" in elem.attrib and elem.attrib["fill"] != "none":
            elem.set("fill", _color)
        if "stroke" in elem.attrib and elem.attrib["stroke"] != "none":
            elem.set("stroke", _color)
        if "style" in elem.attrib and elem.attrib["style"] != "none":
            try:
                style = elem.attrib["style"]
                style_dict = {}
                for item in style.split(";"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        style_dict[k.strip()] = v.strip()
                if "fill" in style_dict and style_dict["fill"] != "none":
                    match style_dict["fill"]:
                        case "#ffffff":
                            style_dict["fill"] = _bg_color
                        case "#000000":
                            style_dict["fill"] = _color
                if "stroke" in style_dict and style_dict["stroke"] != "none":
                    match style_dict["stroke"]:
                        case "#ffffff":
                            style_dict["stroke"] = _bg_color
                        case "#000000":
                            style_dict["stroke"] = _color
                elem.attrib["style"] = ";".join(
                    [f"{k}:{v}" for k, v in style_dict.items()]
                )
            except Exception:
                pass
    _svg_string = ElementTree.tostring(_root, encoding="utf-8")
    _byte_array = QtCore.QByteArray(_svg_string)

    _renderer = QtSvg.QSvgRenderer(_byte_array)
    _pixmap = QtGui.QPixmap(128, 128)
    _pixmap.fill(QtCore.Qt.GlobalColor.transparent)

    _painter = QtGui.QPainter(_pixmap)
    _renderer.render(_painter)
    _painter.end()

    return QtGui.QIcon(_pixmap)
