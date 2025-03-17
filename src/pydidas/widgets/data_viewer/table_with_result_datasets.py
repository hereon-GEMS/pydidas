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
Module with the TableWithResultDatasets class which is a table to select result datasets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TableWithResultDatasets"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.workflow import ProcessingResults, WorkflowResults


RESULTS = WorkflowResults()


class TableWithResultDatasets(QtWidgets.QTableWidget):
    """
    A QTableWidget used for selecting a dataset from the workflow results.
    """

    init_kwargs = ["font_metric_height_factor", "font_metric_width_factor"]

    sig_new_selection = QtCore.Signal(int)

    def __init__(self, **kwargs: dict):
        QtWidgets.QTableWidget.__init__(self, kwargs.get("parent", None))
        apply_qt_properties(
            self,
            columnCount=1,
            rowCount=0,
            verticalScrollBarPolicy=QtCore.Qt.ScrollBarAlwaysOn,
            editTriggers=QtWidgets.QTableWidget.NoEditTriggers,
        )
        self._font_metric_width_factor = kwargs.get(
            "font_metric_width_factor", FONT_METRIC_CONFIG_WIDTH
        )
        self._font_metric_height_factor = kwargs.get("font_metric_height_factor", 6)
        self._row_items = {}
        self._qtapp = QtWidgets.QApplication.instance()
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)
        self.process_new_font_metrics(*self._qtapp.font_metrics)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.selectionModel().selectionChanged.connect(self.emit_new_selection)

    @property
    def table_display_height(self) -> int:
        """Calculate the required height for the table"""
        _nrows = min(self.rowCount(), self._font_metric_height_factor)
        return self.horizontalHeader().height() + sum(
            (self.rowHeight(_i) + 1) for _i in range(_nrows)
        )

    @property
    def selected_node_id(self) -> int:
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
        return self._row_items[_rows[0]]

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
        _new_width = int(self._font_metric_width_factor * char_width)
        self.setFixedWidth(_new_width)
        self.setFixedHeight(self.table_display_height)

    @QtCore.Slot()
    def emit_new_selection(self):
        """
        Emit the signal of a new selection.
        """
        self.sig_new_selection.emit(self.selected_node_id)

    @QtCore.Slot()
    def remove_all_rows(self):
        """
        Remove all points.
        """
        with QtCore.QSignalBlocker(self.selectionModel()):
            while self.rowCount() > 0:
                self.removeRow(0)
        self.setRowCount(0)
        self.setVisible(False)

    def update_choices_from_workflow_results(self, results: ProcessingResults):
        """
        Update the available choices from the WorkflowResults.

        Parameters
        ----------
        results : ProcessingResults
            The ProcessingResults instance.
        """
        _labels = results.result_titles
        self.remove_all_rows()
        self._row_items = {_i: _nodeid for _i, _nodeid in enumerate(_labels)}
        self.setRowCount(len(_labels))
        for _i_row, (_node_id, _label) in enumerate(_labels.items()):
            _title = f"Node #{_node_id:02d}" + ("" if _label == "" else f": {_label}")
            _widget = QtWidgets.QTableWidgetItem(_label)
            self.setItem(_i_row, 0, _widget)
        self.setVisible(True)
        self.setFixedHeight(self.table_display_height)
