# This file is part of pydidas
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the PydidasQTable class which is a table which scales in size with the font.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQTable"]


from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import UserConfigError
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas_qtcore import PydidasQApplication


class PydidasQTable(PydidasWidgetMixin, QtWidgets.QTableWidget):
    """
    A QTableWidget used for selecting a dataset from the workflow results.
    """

    init_kwargs = [
        "font_metric_height_factor",
        "font_metric_width_factor",
        "vertical_header",
        "horizontal_header",
        "relative_column_widths",
        "autoscale_height",
        # need to handle the Qt properties for columnCount and rowCount here tó
        # handle the relative column widths correctly
        "columnCount",
        "rowCount",
    ]

    sig_row_selected = QtCore.Signal(int)

    def __init__(self, **kwargs: Any):
        kwargs["font_metric_height_factor"] = kwargs.get("font_metric_height_factor", 6)
        self._rel_column_widths = kwargs.pop("relative_column_widths", None)
        self._autoscale_height = kwargs.pop("autoscale_height", False)
        self._qtapp = PydidasQApplication.instance()
        QtWidgets.QTableWidget.__init__(
            self, kwargs.pop("columnCount", 0), kwargs.pop("rowCount", 0)
        )
        PydidasWidgetMixin.__init__(self, **kwargs)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
            if self._rel_column_widths is None
            else QtWidgets.QHeaderView.Interactive
        )
        self.horizontalHeader().setVisible(kwargs.get("horizontal_header", False))
        self.verticalHeader().setVisible(kwargs.get("vertical_header", False))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.selectionModel().selectionChanged.connect(self.emit_row_selection)
        if self._autoscale_height:
            self.setWordWrap(True)

    @property
    def table_display_height(self) -> int:
        """Calculate the required height for the table"""
        _count = self.rowCount() or 1
        _height = self._font_metric_height_factor or 1
        _n_rows = min(_count, _height)
        return self.horizontalHeader().height() + sum(
            (self.rowHeight(_i) + 1) for _i in range(_n_rows)
        )

    @property
    def selected_row_id(self) -> int:
        """
        Get the selected node id.

        Returns
        -------
        int
            The selected node id.
        """
        _rows = [_item.row() for _item in self.selectedIndexes()]
        if len(_rows) == 0:
            return -1
        return _rows[0]

    @QtCore.Slot()
    def emit_row_selection(self):
        """
        Emit the signal of a new row selection.
        """
        self.sig_row_selected.emit(self.selected_row_id)

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
        if self._font_metric_width_factor is not None:
            _new_width = int(self._font_metric_width_factor * char_width)
            self.setFixedWidth(_new_width)
            if self._rel_column_widths is not None:
                if len(self._rel_column_widths) != self.columnCount():
                    raise UserConfigError(
                        f"Expected {self.columnCount()} relative column widths, "
                        f"got {len(self._rel_column_widths)}."
                    )
                _total_width_mult = sum(self._rel_column_widths)
                for _i_col, _rel_width in enumerate(self._rel_column_widths):
                    _width_i = int(_new_width * (_rel_width / _total_width_mult))
                    if (_i_col + 1) == self.columnCount():
                        _width_i -= self._qtapp.scrollbar_width
                    self.setColumnWidth(_i_col, _width_i)

    def _set_new_height(self):
        """Set the new height of the table based on the number of rows."""
        if self._autoscale_height:
            self.resizeRowsToContents()
            _height = sum(1 + self.rowHeight(row) for row in range(self.rowCount()))
        else:
            _height = self.table_display_height
        self.setFixedHeight(_height)

    @QtCore.Slot()
    def remove_all_rows(self) -> None:
        """
        Remove all rows from the table.
        """
        with QtCore.QSignalBlocker(self.selectionModel()):
            while self.rowCount() > 0:
                self.removeRow(0)
        self.setRowCount(0)
        self.setVisible(False)

    def add_row(self, *labels: str) -> None:
        """
        Add a row to the table with the given labels.

        Parameters
        ----------
        *labels : str
            The labels of the cells.
        """
        self.setVisible(True)
        if len(labels) != self.columnCount():
            raise UserConfigError(
                f"Expected {self.columnCount()} labels, got {len(labels)}."
            )
        _i_row = self.rowCount()
        self.setRowCount(_i_row + 1)
        for _col, _label in enumerate(labels):
            self.setItem(_i_row, _col, QtWidgets.QTableWidgetItem(_label))
        self._set_new_height()
