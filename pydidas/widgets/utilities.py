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
Module with various utility functions for widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "delete_all_items_in_layout",
    "create_default_grid_layout",
    "get_pyqt_icon_from_str_reference",
    "get_max_pixel_width_of_entries",
]


from qtpy import QtWidgets, QtCore, QtGui
import qtawesome


def delete_all_items_in_layout(layout):
    """
    Function to recursively delete items in a QLayout.

    Parameters
    ----------
    layout : QLayout
        The layout to be cleared.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                delete_all_items_in_layout(item.layout())


def create_default_grid_layout():
    """
    Create a QGridLayout with default parameters.

    The default parameters are

        - vertical spacing : 5
        - horizontal spacing : 5
        - alignment : left | top

    Returns
    -------
    layout : QGridLayout
        The layout.
    """
    _layout = QtWidgets.QGridLayout()
    _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    _layout.setHorizontalSpacing(5)
    _layout.setVerticalSpacing(5)
    return _layout


def get_pyqt_icon_from_str_reference(ref_string):
    """
    Get a QIcon from the reference string.

    Three types of strings can be processsed:
        1. References to a qtawesome icon. The reference must be preceeded
           by 'qta::'.
        2. A reference number of a QStandardIcon, preceeded by a 'qt-std::'.
        3. A reference to a image file in the file system. This must be
           preceeded by 'path::'.

    Parameters
    ----------
    ref_string : str
        The reference string for the icon.

    Raises
    ------
    TypeError
        If no correct preceeding type has been found.

    Returns
    -------
    QtGui.QIcon
        The icon

    """
    _type, _ref = ref_string.split("::")
    if _type == "qta":
        _menu_icon = qtawesome.icon(_ref)
    elif _type == "qt-std":
        _num = int(_ref)
        app = QtWidgets.QApplication.instance()
        _menu_icon = app.style().standardIcon(_num)
    elif _type == "path":
        _menu_icon = QtGui.QIcon(_ref)
    else:
        raise TypeError("Cannot interpret the string reference for the menu icon.")
    return _menu_icon


def get_max_pixel_width_of_entries(entries):
    """
    Get the maximum width from a number of entries.

    This function calculates the width (in pixels) of a list of given strings.

    Parameters
    ----------
    entries : Union[str, tuple, list]
        The entries.

    Returns
    -------
    width : int
        The maximum width of the entries in pixels.
    """
    if isinstance(entries, str):
        entries = [entries]

    font = QtWidgets.QApplication.instance().font()
    metrics = QtGui.QFontMetrics(font)
    _width = max([metrics.boundingRect(_item).width() for _item in entries])
    return _width
