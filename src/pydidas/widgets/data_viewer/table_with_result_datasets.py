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

from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory.pydidas_table import PydidasQTable
from pydidas.workflow import ProcessingResults, WorkflowResults


RESULTS = WorkflowResults()


class TableWithResultDatasets(PydidasQTable):
    """
    A QTableWidget used for selecting a dataset from the workflow results.
    """

    sig_node_selected = QtCore.Signal(int)

    def __init__(self, **kwargs: Any):
        kwargs["font_metric_width_factor"] = kwargs.get(
            "font_metric_width_factor", FONT_METRIC_CONFIG_WIDTH
        )
        kwargs["font_metric_height_factor"] = kwargs.get("font_metric_height_factor", 6)
        PydidasQTable.__init__(self, **kwargs)
        apply_qt_properties(self, columnCount=1, rowCount=0)
        self._row_items = {}
        self.selectionModel().selectionChanged.connect(self.emit_new_node_selection)

    @QtCore.Slot()
    def emit_new_node_selection(self):
        """
        Emit the signal of a new selection.
        """
        if self.selected_row_id >= 0:
            self.sig_node_selected.emit(self._row_items[self.selected_row_id])

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
