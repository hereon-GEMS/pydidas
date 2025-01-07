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
Module with various utility functions for widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "delete_all_items_in_layout",
    "create_default_grid_layout",
    "get_pyqt_icon_from_str",
    "get_max_pixel_width_of_entries",
    "update_param_and_widget_choices",
    "icon_with_inverted_colors",
]


from typing import Union

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QBoxLayout, QGridLayout, QStackedLayout, QStyle

from pydidas.core import PydidasGuiError
from pydidas.resources import icons


def delete_all_items_in_layout(layout: QtWidgets.QLayout):
    """
    Recursively delete items in a QLayout.

    Parameters
    ----------
    layout : QLayout
        The layout to be cleared.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            if item.spacerItem() is not None:
                layout.removeItem(item)
            if item.layout() is not None:
                delete_all_items_in_layout(item.layout())
                layout.remove(item)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


def create_default_grid_layout() -> QGridLayout:
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
    _layout = QGridLayout()
    _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    _layout.setHorizontalSpacing(5)
    _layout.setVerticalSpacing(5)
    return _layout


def get_pyqt_icon_from_str(ref_string: str) -> QtGui.QIcon:
    """
    Get a QIcon from the reference string.

    Four types of strings can be processed:
        1. A reference number of a QStandardIcon, preceded by a 'qt-std::'.
        2. A reference to an image file in the file system. This must be
           preceded by 'path::'.
        3. A reference to an icon in pydidas.core.icons with the filename preceded
           by a 'pydidas::'
        4. A reference to a mdi icon with the filename preceded by a 'mdi::'
           Note that this only works for those mdi icons which have been included
           in pydidas.

    Parameters
    ----------
    ref_string : str
        The reference string for the icon.

    Raises
    ------
    TypeError
        If no correct preceding type has been found.

    Returns
    -------
    QtGui.QIcon
        The icon
    """
    _type, _ref = ref_string.split("::")
    if _type == "qt-std":
        _ref = getattr(QStyle, _ref)
        app = QtWidgets.QApplication.instance()
        return app.style().standardIcon(_ref)
    if _type == "pydidas":
        return icons.get_pydidas_qt_icon(_ref)
    if _type == "path":
        return QtGui.QIcon(_ref)
    if _type == "mdi":
        return icons.get_mdi_qt_icon(_ref)
    raise TypeError("Cannot interpret the string reference for the menu icon.")


def get_max_pixel_width_of_entries(entries: Union[str, tuple, list]) -> int:
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
    _width = max(metrics.boundingRect(_item).width() for _item in entries)
    return _width


def get_widget_layout_args(parent: QtWidgets.QWidget, **kwargs: dict):
    """
    Get the arguments for adding a widget to the layout of the parent.

    Parameters
    ----------
    parent : QWidget
        The parent QWidget to which the new widget shall be added.
    **kwargs : dict
        The keyword arguments dictionary from the calling method. This
        method only takes the "gridPos", "stretch" and "alignment" arguments from the
        kwargs.

    Raises
    ------
    PydidasGuiError
        If the parent widget has no supported layout. Supported are
        QBoxLayout, QStackedLayout or QGridLayout and subclasses.

    Returns
    -------
    list
        The list of layout arguments required for adding the widget to
        the layout of the parent widget.
    """
    if not isinstance(parent.layout(), (QBoxLayout, QStackedLayout, QGridLayout)):
        raise PydidasGuiError(
            f'Layout of parent widget "{parent}" is not of type '
            "QBoxLayout, QStackedLayout or QGridLayout."
        )

    _alignment = kwargs.get("alignment", None)
    if isinstance(parent.layout(), QtWidgets.QBoxLayout):
        return [kwargs.get("stretch", 0), _alignment]
    if isinstance(parent.layout(), QtWidgets.QStackedLayout):
        return []
    _grid_pos = get_grid_pos(parent, **kwargs)
    if _alignment is not None:
        return [*_grid_pos, _alignment]
    return [*_grid_pos]


def get_grid_pos(parent: QtWidgets.QWidget, **kwargs: dict):
    """
    Get the gridPos format from the kwargs or create it.

    Parameters
    ----------
    parent : QWidget
        The parent QWidget to be added to the layout.
    **kwargs : dict
        The keyword arguments dictionary from the calling method. This
        method only takes the "gridPos" and "alignment" arguments from the
        kwargs.

    Raises
    ------
    PydidasGuiError
        If gridPos has been specified but is not of type tuple and not of
        length 4.

    Returns
    -------
    gridPos : tuple
        The 4-tuple of the gridPos.
    """
    _grid_pos = kwargs.get("gridPos", None)
    _default_row = 0 if parent.layout().count() == 0 else parent.layout().rowCount()
    if _grid_pos is None:
        _grid_pos = (
            kwargs.get("row", _default_row),
            kwargs.get("column", 0),
            kwargs.get("n_rows", 1),
            kwargs.get("n_columns", 1),
        )
    if not (isinstance(_grid_pos, tuple) and len(_grid_pos) == 4):
        raise PydidasGuiError(
            'The passed value for "gridPos" is not of type tuple and/or not'
            " of length 4."
        )
    if _grid_pos[0] == -1:
        _grid_pos = (_default_row,) + _grid_pos[1:4]
    if _grid_pos[1] == -1:
        _grid_pos = (_grid_pos[0], parent.layout().columnCount()) + _grid_pos[2:]
    return _grid_pos


def update_param_and_widget_choices(param_widget: QtWidgets.QWidget, new_choices: list):
    """
    Update the choices for the given Parameter and in its widget.

    This function will update the choices and also set the combo box widget to an
    allowed choice.

    Parameters
    ----------
    param_widget : pydidas.widgets.parameter_config.ParameterWidget
        The pydidas ParameterWidget instance.
    new_choices : list
        The list of new choices.
    """
    _param = param_widget.param
    if len(new_choices) == 0:
        _param.choices = None
        _param.value = ""
    else:
        _param.update_value_and_choices(new_choices[0], new_choices)
    param_widget.io_widget.setEnabled(len(new_choices) != 0)
    with QtCore.QSignalBlocker(param_widget.io_widget):
        if len(new_choices) == 0:
            param_widget.io_widget.update_choices([""])
            param_widget.io_widget.setCurrentText("")
            return
        param_widget.io_widget.update_choices(new_choices)
        param_widget.io_widget.setCurrentText(new_choices[0])


def icon_with_inverted_colors(icon: QtGui.QIcon) -> QtGui.QIcon:
    """
    Invert the colors of a QIcon.

    Parameters
    ----------
    icon : QIcon
        The icon to be inverted.

    Returns
    -------
    QIcon
        The inverted icon.
    """
    _pixmap = icon.pixmap(30, 30)
    _image = _pixmap.toImage()
    _image.invertPixels()
    _inverted_pixmap = QtGui.QPixmap.fromImage(_image)
    return QtGui.QIcon(_inverted_pixmap)
