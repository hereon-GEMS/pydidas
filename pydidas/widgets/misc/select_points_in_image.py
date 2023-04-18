# This file is part of ...
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
# along with ... If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SelectPointsInImage class which allows to select points
in an image, for example to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SelectPointsInImage"]

from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot.items import Marker

from ...core import Parameter
from ...core.constants import (
    ALIGN_CENTER,
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    PYDIDAS_COLORS,
    STANDARD_FONT_SIZE,
)
from ...core.utils import SignalBlocker
from ...data_io import import_data
from ...widgets.factory import CreateWidgetsMixIn
from ...widgets.parameter_config import ParameterWidgetsMixIn
from ...widgets.silx_plot import PydidasPlot2D


class SelectPointsInImage(QtWidgets.QWidget, CreateWidgetsMixIn, ParameterWidgetsMixIn):
    """
    A widget which allows to select points in a given image.
    """

    container_width = 200

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        self._markers = {}
        self._image = None
        self.marker_color = Parameter(
            "marker_color",
            str,
            "orange",
            name="Marker color",
            choices=list(PYDIDAS_COLORS.keys()),
            tooltip="Set the display color for the markers of selected points.",
        )

        self.create_empty_widget(
            "left_container", fixedWidth=self.container_width, minimumHeight=400
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(0, 1, 1, 1))
        self.add_any_widget(
            "plot",
            PydidasPlot2D(cs_transform=False),
            minimumWidth=600,
            minimumHeight=600,
            gridPos=(0, 2, 1, 1),
        )
        self.create_label(
            "label_title",
            "Select points in image:",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=self.container_width,
            bold=True,
            parent_widget=self._widgets["left_container"],
        )
        self.create_line("line_top", parent_widget=self._widgets["left_container"])
        self.create_param_widget(
            self.marker_color,
            **(
                DEFAULT_TWO_LINE_PARAM_CONFIG
                | dict(parent_widget=self._widgets["left_container"])
            ),
        )
        self.create_line("line_points", parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_title",
            "Selected points",
            fontsize=STANDARD_FONT_SIZE,
            fixedWidth=self.container_width,
            underline=True,
            parent_widget=self._widgets["left_container"],
        )
        self.add_any_widget(
            "table",
            QtWidgets.QTableWidget(),
            parent_widget=self._widgets["left_container"],
            columnCount=1,
            rowCount=0,
            fixedWidth=self.container_width,
            horizontalHeaderLabels=[["(x, y) position"]],
            verticalScrollBarPolicy=QtCore.Qt.ScrollBarAlwaysOn,
            editTriggers=QtWidgets.QTableWidget.NoEditTriggers,
        )
        self._widgets["table"].horizontalHeader().resizeSection(0, 180)
        self._widgets["table"].setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.create_button(
            "but_delete_selected_points",
            "Delete selected points",
            fixedWidth=self.container_width,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )
        self._widgets["but_delete_selected_points"].clicked.connect(
            self._remove_selected_points
        )
        self._widgets["plot"].sigPlotSignal.connect(self._process_plot_signal)
        self.param_widgets["marker_color"].io_edited.connect(self._update_markers)
        self._widgets["table"].selectionModel().selectionChanged.connect(
            self.__new_markers_selected
        )

    @property
    def new_marker_index(self):
        """
        Get the index for a new marker.

        Returns
        -------
        int
            The index for the next marker.
        """
        _curr_markers = set(self._markers.values())
        if _curr_markers == set():
            return 0
        return max(set(self._markers.values())) + 1

    def open_image(self, filename, **kwargs):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        """
        self._image = import_data(filename, **kwargs)
        _path = Path(filename)
        self._widgets["plot"].plot_pydidas_dataset(self._image, title=_path.name)

    @QtCore.Slot(dict)
    def _process_plot_signal(self, event_dict):
        """
        Process events from the plot and filter and process mouse clicks.

        Parameters
        ----------
        event_dict : dict
            The silx event dictionary.
        """
        if (
            event_dict["event"] == "mouseClicked"
            and event_dict.get("button", "None") == "left"
        ):
            _color = PYDIDAS_COLORS[self.marker_color.value]
            _x = np.round(event_dict["x"], decimals=3)
            _y = np.round(event_dict["y"], decimals=3)
            if (_x, _y) in self._markers:
                return
            _index = self.new_marker_index
            self._widgets["plot"].addMarker(
                _x, _y, legend=f"marker_{_index}", color=_color, symbol="x"
            )
            self._markers[(_x, _y)] = _index
            self.__add_point_to_table(_x, _y)

    def __add_point_to_table(self, xpos, ypos):
        """
        Add a newly selected point to the table.

        Parameters
        ----------
        xpos : float
            The x position.
        ypos : float
            The y position
        """
        _row = self._widgets["table"].rowCount()
        self._widgets["table"].setRowCount(_row + 1)
        _widget = QtWidgets.QTableWidgetItem(f"({xpos:.3f}, {ypos:.3f})")
        _widget.setTextAlignment(ALIGN_CENTER)
        self._widgets["table"].setItem(_row, 0, _widget)

    @QtCore.Slot(str)
    def _update_markers(self, color):
        """
        Update the markers with a new color.

        Parameters
        ----------
        color : str
            The new color name.
        """
        _colorcode = PYDIDAS_COLORS[color]
        _items = self._widgets["plot"].getItems()
        for _item in _items:
            if isinstance(_item, Marker):
                _item.setColor(_colorcode)

    @QtCore.Slot()
    def __new_markers_selected(self):
        """
        Process the signal that new markers have been selected.
        """
        _selected_markers = self._get_indices_of_selected_points()
        for _id in self._markers.values():
            _marker = self._widgets["plot"]._getItem("marker", f"marker_{_id}")
            _symbol = "o" if _id in _selected_markers else "x"
            _marker.setSymbol(_symbol)

    def _get_indices_of_selected_points(self):
        """
        Get the indices of the selected points.

        Returns
        -------
        list
            The list of the indices of the selected points.
        """
        _points = self._get_selected_points()
        return [self._markers[_pos] for _pos in _points]

    def _get_selected_points(self):
        """
        Get the selected points.

        Returns
        -------
        list
            List of the (x, y) position tuples.
        """
        _indices = self._widgets["table"].selectedIndexes()
        _selected_points = []
        for _index_item in _indices:
            _data = _index_item.data().strip("()").split(",")
            _pos = (float(_data[0]), float(_data[1]))
            _selected_points.append(_pos)
        return _selected_points

    @QtCore.Slot()
    def _remove_selected_points(self):
        """
        Remove the selected points.
        """
        _selected_markers = self._get_indices_of_selected_points()
        _rows_to_remove = self._get_rows_of_selected_points()
        _new_row_count = self._widgets["table"].rowCount() - len(_selected_markers)
        for _point in self._get_selected_points():
            del self._markers[_point]
        for _id in _selected_markers:
            self._widgets["plot"].removeMarker(f"marker_{_id}")
        with SignalBlocker(self._widgets["table"].selectionModel()):
            for _row in _rows_to_remove:
                self._widgets["table"].removeRow(_row)
        self._widgets["table"].setRowCount(_new_row_count)

    def _get_rows_of_selected_points(self):
        """
        Get the row numbers of the selected points, sorted in inverse order.

        Returns
        -------
        list
            The list with the row numbers of the selection.
        """
        _rows = [_item.row() for _item in self._widgets["table"].selectedIndexes()]
        _rows.sort(reverse=True)
        return _rows

    def get_selected_points(self):
        """
        Get the selected points as two arrays for x- and y-coordinates.

        Returns
        -------
        x_positions : np.ndarray
            The x values of the selected points.
        y_positions : np.ndarray
            The y values of the selected points.
        """
        _n = len(self._markers)
        _x = np.zeros((_n))
        _y = np.zeros((_n))
        for _index, (_xpos, _ypos) in enumerate(self._markers):
            _x[_index] = _xpos
            _y[_index] = _ypos
        return _x, _y
