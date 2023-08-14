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
Module with various utility functions for widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "BlockUpdates",
    "delete_all_items_in_layout",
    "create_default_grid_layout",
    "get_pyqt_icon_from_str",
    "get_max_pixel_width_of_entries",
    "update_param_and_widget_choices",
]


import qtawesome
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QBoxLayout, QGridLayout, QStackedLayout, QStyle

from ..core import PydidasGuiError
from ..resources import icons


def delete_all_items_in_layout(layout):
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
    _layout = QGridLayout()
    _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    _layout.setHorizontalSpacing(5)
    _layout.setVerticalSpacing(5)
    return _layout


def get_pyqt_icon_from_str(ref_string):
    """
    Get a QIcon from the reference string.

    Four types of strings can be processsed:
        1. References to a qtawesome icon. The reference must be preceeded
           by 'qta::'.
        2. A reference number of a QStandardIcon, preceeded by a 'qt-std::'.
        3. A reference to a image file in the file system. This must be
           preceeded by 'path::'.
        4. A reference to a icon in pydidas.core.icons with the filename preceded
           by a 'pydidas::'

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
        _ref = getattr(QStyle, _ref)
        app = QtWidgets.QApplication.instance()
        _menu_icon = app.style().standardIcon(_ref)
    elif _type == "pydidas":
        _menu_icon = icons.get_pydidas_qt_icon(_ref)
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
    _width = max(metrics.boundingRect(_item).width() for _item in entries)
    return _width


def get_widget_layout_args(parent, **kwargs):
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


def get_grid_pos(parent, **kwargs):
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


def update_param_and_widget_choices(param_widget, new_choices):
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
        _param.choices = None
        _param.value = new_choices[0]
        _param.choices = new_choices
    param_widget.io_widget.setEnabled(len(new_choices) != 0)
    with QtCore.QSignalBlocker(param_widget.io_widget):
        if len(new_choices) == 0:
            param_widget.io_widget.update_choices([""])
            param_widget.io_widget.setCurrentText("")
            return
        param_widget.io_widget.update_choices(new_choices)
        param_widget.io_widget.setCurrentText(new_choices[0])


class BlockUpdates:
    """Class to block UI updates from a QWidget."""

    def __init__(self, caller):
        self._caller = caller
        self._update_status = caller.updatesEnabled()

    def __enter__(self):
        self._caller.setUpdatesEnabled(False)

    def __exit__(self, type_, value, traceback):
        self._caller.setUpdatesEnabled(self._update_status)
