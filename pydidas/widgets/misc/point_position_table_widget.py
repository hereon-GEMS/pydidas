# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PointPositionTableWidget class which is a table to select and display
points (i.e. x/y tuples) in a plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PointPositionTableWidget"]


from typing import List, Tuple

from qtpy import QtCore, QtWidgets

from ...core.constants import ALIGN_CENTER
from ...core.utils import apply_qt_properties
from ..factory import CreateWidgetsMixIn
from ..parameter_config import ParameterWidgetsMixIn


class _TableWithXYPositions(QtWidgets.QTableWidget):
    """
    A QTableWidget used for displaying a single column of (x, y) points.
    """

    sig_new_selection = QtCore.Signal(object)
    sig_remove_points = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)
        apply_qt_properties(
            self,
            columnCount=1,
            rowCount=0,
            horizontalHeaderLabels=[["(x, y) position"]],
            verticalScrollBarPolicy=QtCore.Qt.ScrollBarAlwaysOn,
            editTriggers=QtWidgets.QTableWidget.NoEditTriggers,
        )
        self.horizontalHeader().resizeSection(0, 200)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.selectionModel().selectionChanged.connect(self.emit_new_selection)

    def keyPressEvent(self, event):
        """
        Extend the generic keyPressEvent to add a binding for the Del key.

        Parameters
        ----------
        event : QtGui.QKeyEvent
            The keyPressEvent
        """
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_selected_points()
        else:
            super().keyPressEvent(event)

    @QtCore.Slot()
    def emit_new_selection(self):
        """
        Emit
        """
        self.sig_new_selection.emit(self._get_selected_points())

    @QtCore.Slot()
    def remove_selected_points(self):
        """
        Remove the selected points.
        """
        _points_to_remove = self._get_selected_points()
        _rows_to_remove = self.get_rows_of_selected_points()
        _new_row_count = self.rowCount() - len(_rows_to_remove)
        with QtCore.QSignalBlocker(self.selectionModel()):
            for _row in _rows_to_remove:
                self.removeRow(_row)
        self.setRowCount(_new_row_count)
        self.sig_remove_points.emit(_points_to_remove)

    @QtCore.Slot()
    def remove_all_points(self):
        """
        Remove all points.
        """
        _points_to_remove = self._get_all_points()
        with QtCore.QSignalBlocker(self.selectionModel()):
            while self.rowCount() > 0:
                self.removeRow(0)
        self.setRowCount(0)
        self.sig_remove_points.emit(_points_to_remove)

    def _get_selected_points(self) -> List[Tuple[float, float]]:
        """
        Get the selected points.

        Returns
        -------
        list
            List of the (x, y) position tuples.
        """
        _indices = self.selectedIndexes()
        _selected_points = []
        for _index_item in _indices:
            _data = _index_item.data().strip("()").split(",")
            _pos = (float(_data[0]), float(_data[1]))
            _selected_points.append(_pos)
        return _selected_points

    def _get_all_points(self) -> List[Tuple[float, float]]:
        """
        Get a list of all points.

        Returns
        -------
        List
            The list with all points
        """
        _points = []
        for _index in range(self.rowCount()):
            _item = self.item(_index, 0)
            _data = _item.data(QtCore.Qt.DisplayRole).strip("()").split(",")
            _pos = (float(_data[0]), float(_data[1]))
            _points.append(_pos)
        return _points

    def get_rows_of_selected_points(self) -> List:
        """
        Get the row numbers of the selected points, sorted in inverse order.

        Returns
        -------
        list
            The list with the row numbers of the selection.
        """
        _rows = [_item.row() for _item in self.selectedIndexes()]
        _rows.sort(reverse=True)
        return _rows


class PointPositionTableWidget(
    QtWidgets.QWidget, CreateWidgetsMixIn, ParameterWidgetsMixIn
):
    """
    A widget to display a list of points in an associated plot.
    """

    widget_width = 220

    sig_new_selection = QtCore.Signal(object)
    sig_remove_points = QtCore.Signal(object)

    def __init__(self, plot, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        self.setFixedWidth(self.widget_width)
        self._points = []
        self._plot = plot
        self._config = {
            "overlay_color": kwargs.get("overlay_color", "orange"),
        }
        self.add_any_widget(
            "table",
            _TableWithXYPositions(),
            fixedWidth=self.widget_width,
        )
        self.create_button(
            "but_delete_selected_points",
            "Delete selected points",
            fixedWidth=self.widget_width,
            fixedHeight=25,
        )
        self.create_button(
            "but_delete_all_points",
            "Delete all points",
            fixedWidth=self.widget_width,
            fixedHeight=25,
        )

        self._widgets["but_delete_selected_points"].clicked.connect(
            self._widgets["table"].remove_selected_points
        )
        self._widgets["but_delete_all_points"].clicked.connect(
            self._widgets["table"].remove_all_points
        )
        self._widgets["table"].sig_new_selection.connect(self.sig_new_selection)
        self._widgets["table"].sig_remove_points.connect(self.sig_remove_points)

    def add_point_to_table(self, xpos: float, ypos: float):
        """
        Add a newly selected point to the table.

        Parameters
        ----------
        xpos : float
            The x position.
        ypos : float
            The y position
        """
        _table = self._widgets["table"]
        _row = _table.rowCount()
        _table.setRowCount(_row + 1)
        _widget = QtWidgets.QTableWidgetItem(f"({xpos:.3f}, {ypos:.3f})")
        _widget.setTextAlignment(ALIGN_CENTER)
        _table.setItem(_row, 0, _widget)
