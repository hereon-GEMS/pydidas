# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PointsForBeamcenterWidget class which is a table to select and display
points (i.e. x/y tuples) in a plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PointsForBeamcenterWidget"]


from qtpy import QT_VERSION, QtCore, QtGui, QtWidgets

from pydidas.core import get_generic_parameter
from pydidas.core.constants import ALIGN_CENTER, FONT_METRIC_WIDE_BUTTON_WIDTH
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn


class _TableWithXYPositions(QtWidgets.QTableWidget):
    """
    A QTableWidget used for displaying a single column of (x, y) points.
    """

    sig_new_selection = QtCore.Signal(object)
    sig_remove_points = QtCore.Signal(object)

    def __init__(self, **kwargs: dict):
        QtWidgets.QTableWidget.__init__(self, kwargs.get("parent", None))
        apply_qt_properties(
            self,
            columnCount=1,
            rowCount=0,
            horizontalHeaderLabels=[["(x, y) position"]],
            verticalScrollBarPolicy=QtCore.Qt.ScrollBarAlwaysOn,
            editTriggers=QtWidgets.QTableWidget.NoEditTriggers,
        )
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.selectionModel().selectionChanged.connect(self.emit_new_selection)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
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

    def _get_selected_points(self) -> list[tuple[float, float], ...]:
        """
        Get the selected points.

        Returns
        -------
        list[tuple[float, float], ...]
            List of the (x, y) position tuples.
        """
        _indices = self.selectedIndexes()
        _selected_points = []
        for _index_item in _indices:
            _data = _index_item.data().strip("()").split(",")
            _pos = (float(_data[0]), float(_data[1]))
            _selected_points.append(_pos)
        return _selected_points

    def _get_all_points(self) -> list[tuple[float, float], ...]:
        """
        Get a list of all points.

        Returns
        -------
        list[tuple[float, float], ...]
            The list with all points (tuples of (x, y) positions).
        """
        _points = []
        for _index in range(self.rowCount()):
            _item = self.item(_index, 0)
            _data = _item.data(QtCore.Qt.DisplayRole).strip("()").split(",")
            _pos = (float(_data[0]), float(_data[1]))
            _points.append(_pos)
        return _points

    def get_rows_of_selected_points(self) -> list[int, ...]:
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


class PointsForBeamcenterWidget(
    QtWidgets.QWidget, CreateWidgetsMixIn, ParameterWidgetsMixIn
):
    """
    A widget to display a list of points in an associated plot.
    """

    sig_new_selection = QtCore.Signal(object)
    sig_remove_points = QtCore.Signal(object)
    sig_2click_usage = QtCore.Signal(bool)

    def __init__(self, plot, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        self._qtapp = QtWidgets.QApplication.instance()
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)
        self._points = []
        self._plot = plot
        self._color_param = get_generic_parameter("overlay_color")
        self.create_check_box(
            "two_click_selection",
            "Use 2-click point selection",
            checked=True,
            font_metric_width_factor=FONT_METRIC_WIDE_BUTTON_WIDTH,
            toolTip=(
                "The 2-click point selection requires two clicks in the image to "
                "select a new point: The first click zooms in on the selected point "
                "while the second click confirms the (finer) selection."
            ),
        )
        self.create_param_widget(
            self._color_param,
            font_metric_width_factor=FONT_METRIC_WIDE_BUTTON_WIDTH,
            linebreak=True,
        )
        self.add_any_widget(
            "table",
            _TableWithXYPositions(),
        )
        self.create_button(
            "but_delete_selected_points",
            "Delete selected points",
        )
        self.create_button(
            "but_delete_all_points",
            "Delete all points",
        )

        self.process_new_font_metrics(*self._qtapp.font_metrics)
        self._widgets["but_delete_selected_points"].clicked.connect(
            self._widgets["table"].remove_selected_points
        )
        self._widgets["but_delete_all_points"].clicked.connect(
            self._widgets["table"].remove_all_points
        )
        self._widgets["table"].sig_new_selection.connect(self.sig_new_selection)
        self._widgets["table"].sig_remove_points.connect(self.sig_remove_points)
        self._widgets["two_click_selection"].stateChanged.connect(
            self._toggle_2click_selection
        )

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

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Adjust the widget's width based on the font metrics.

        Parameters
        ----------
        char_width : float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        _new_width = int(FONT_METRIC_WIDE_BUTTON_WIDTH * char_width)
        self.setFixedWidth(_new_width)
        self._widgets["table"].setFixedWidth(_new_width)
        self._widgets["table"].horizontalHeader().resizeSection(
            0, int(0.91 * (_new_width - self._qtapp.scrollbar_width))
        )

    @QtCore.Slot(int)
    def _toggle_2click_selection(self, state: QtCore.Qt.CheckState):
        """
        Toggle the two-click selection option.

        Parameters
        ----------
        state : QtCore.Qt.CheckState
            The checkbox's state.
        """
        if QT_VERSION.startswith("6"):
            _usage = state == QtCore.Qt.Checked.value
        else:
            _usage = state == QtCore.Qt.Checked
        self.sig_2click_usage.emit(_usage)
