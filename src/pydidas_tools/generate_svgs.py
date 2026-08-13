# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Generate svg files for light and dark modes
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

from pathlib import Path
from xml.etree import ElementTree

from pydidas.core.utils import get_extension
from pydidas.resources.pydidas_icons import ICON_PATH, MDI_ICON_PATH
from pydidas_qtcore import PydidasQApplication


def convert_style_tag(style: str) -> str:
    """Swap white and black in a style string"""
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
    return ";".join([f"{k}:{v}" for k, v in style_dict.items()])


def generate_dark_icon(path: Path):
    """Swaps white and black in svg files"""
    _tree = ElementTree.parse(path)
    _root = _tree.getroot()
    for elem in _root.iter():
        if "fill" in elem.attrib and elem.attrib["fill"] != "none":
            elem.set("fill", _color)
        if "stroke" in elem.attrib and elem.attrib["stroke"] != "none":
            elem.set("stroke", _color)
        if "style" in elem.attrib and elem.attrib["style"] != "none":
            try:
                elem.attrib["style"] = convert_style_tag(elem.attrib["style"])
            except Exception:
                pass
    _svg_string = ElementTree.tostring(_root, encoding="unicode")

    (path.parent / "dark" / path.name).write_text(_svg_string, encoding="utf-8")


def generate_dark_mdi(path: Path):
    """Makes mdi icons white"""
    _tree = ElementTree.parse(path)
    _root = _tree.getroot()
    _root.set("fill", _color)
    _svg_string = ElementTree.tostring(_root, encoding="unicode")
    (path.parent / "dark" / path.name).write_text(_svg_string, encoding="utf-8")


_app = PydidasQApplication.instance()
_dark = _app.is_dark_mode if _app else False
_color = "#ffffff" if _dark else "#000000"
_bg_color = "#000000" if _dark else "#ffffff"

(ICON_PATH / "dark").mkdir(exist_ok=True)
(MDI_ICON_PATH / "dark").mkdir(exist_ok=True)

for path in ICON_PATH.iterdir():
    if path.is_file() and get_extension(path) == ".svg":
        _name = path.name
        if not (path.parent / "dark" / path.name).is_file():
            generate_dark_icon(path)

for path in MDI_ICON_PATH.iterdir():
    if path.is_file():
        _name = path.name
        if not (path.parent / "dark" / path.name).is_file():
            generate_dark_mdi(path)
