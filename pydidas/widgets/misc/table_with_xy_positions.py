# This file is part of pydidas
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the TableWithXYPositions class which is a QTableWidget with one column
to display (x, y) coordinates.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["TableWithXYPositions"]


from qtpy import QtCore, QtWidgets

from ...core.constants import ALIGN_CENTER
from ...core.utils import SignalBlocker, apply_qt_properties


class TableWithXYPositions(QtWidgets.QTableWidget):
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
        self.sig_new_selection.emit(self.get_selected_points())

    @QtCore.Slot()
    def remove_selected_points(self):
        """
        Remove the selected points.
        """
        _points_to_remove = self.get_selected_points()
        _rows_to_remove = self.get_rows_of_selected_points()
        _new_row_count = self.rowCount() - len(_rows_to_remove)
        with SignalBlocker(self.selectionModel()):
            for _row in _rows_to_remove:
                self.removeRow(_row)
        self.setRowCount(_new_row_count)
        self.sig_remove_points.emit(_points_to_remove)

    def add_point_to_table(self, xpos, ypos):
        """
        Add a newly selected point to the table.

        Parameters
        ----------
        xpos : float
            The x position.
        ypos : float
            The y position
        """
        _row = self.rowCount()
        self.setRowCount(_row + 1)
        _widget = QtWidgets.QTableWidgetItem(f"({xpos:.3f}, {ypos:.3f})")
        _widget.setTextAlignment(ALIGN_CENTER)
        self.setItem(_row, 0, _widget)

    def get_selected_points(self):
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

    def get_rows_of_selected_points(self):
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
