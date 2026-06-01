# This file is part of pydidas
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
Module with the TableWithNodeLabels class which is a table to select result datasets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TableWithNodeLabels"]


from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory.pydidas_table import PydidasQTable


class TableWithNodeLabels(PydidasQTable):
    """A QTableWidget used for selecting a node result from their titles."""

    sig_node_selected = QtCore.Signal(int)

    def __init__(self, **kwargs: Any) -> None:
        kwargs["font_metric_width_factor"] = kwargs.get(
            "font_metric_width_factor", FONT_METRIC_CONFIG_WIDTH
        )
        kwargs["font_metric_height_factor"] = kwargs.get("font_metric_height_factor", 6)
        PydidasQTable.__init__(self, **kwargs)
        apply_qt_properties(self, columnCount=1, rowCount=0)
        self._row_node_ids: dict[int, int] = {}
        self._row_labels: dict[int, str] = {}
        self.selectionModel().selectionChanged.connect(self.emit_new_node_selection)

    @property
    def selected_node_label(self) -> str:
        """
        Get the label of the currently selected node.

        Returns
        -------
        str
            The label of the currently selected node.
        """
        _label = self._row_labels.get(self.selected_row_id)
        return _label or ""

    @QtCore.Slot()
    def emit_new_node_selection(self) -> None:
        """
        Emit the signal of a new selection.
        """
        if self.selected_row_id >= 0:
            self.sig_node_selected.emit(self._row_node_ids[self.selected_row_id])

    def get_row_label(self, row_id: int) -> str:
        """
        Get the label of a given row.

        Parameters
        ----------
        row_id: int
            The id of the row for which to get the label.

        Returns
        -------
        str
            The label of the given row.
        """
        return self._row_labels.get(row_id, "")

    def update_node_descriptions(self, titles: dict[int, str]) -> None:
        """
        Update the available choices from the WorkflowResults.

        Parameters
        ----------
        titles: dict[int, str]
            The dictionary with node ids and their corresponding labels.
        """
        self.remove_all_rows()
        self._row_node_ids = {}
        self._row_labels = {}
        self.setRowCount(len(titles))
        for _i_row, (_node_id, _label) in enumerate(titles.items()):
            self._row_node_ids[_i_row] = _node_id
            self._row_labels[_i_row] = _label
            self.setItem(_i_row, 0, QtWidgets.QTableWidgetItem(_label))
        self.setVisible(True)
        self.setFixedHeight(self.table_display_height)
