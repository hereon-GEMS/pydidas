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
Module with the PointPositionTableWidget class is a table to select and display points
in a plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PointPositionTableWidget"]

from pathlib import Path
from typing import Literal, Tuple

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot.items import Marker, Shape

from ...core import Parameter
from ...core.constants import PYDIDAS_COLORS, STANDARD_FONT_SIZE
from ...data_io import import_data
from ..factory import CreateWidgetsMixIn
from ..parameter_config import ParameterWidgetsMixIn
from ..silx_plot import PydidasPlot2D
from .table_with_xy_positions import TableWithXYPositions


class PointPositionTableWidget(
    QtWidgets.QWidget, CreateWidgetsMixIn, ParameterWidgetsMixIn
):
    """
    A widget to display a list of points in an associated plot.
    """

    container_width = 220

    def __init__(self, plot, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        self._points = []
        self._plot = plot
        self._config = {
            "selection_active": kwargs.get("selection_active", True),
            "marker_color": kwargs.get("marker_color", "orange"),
        }
        self.add_any_widget(
            "table",
            TableWithXYPositions(),
            fixedWidth=self.container_width,
        )
        self.create_button(
            "but_delete_selected_points",
            "Delete selected points",
            fixedWidth=self.container_width,
            fixedHeight=25,
        )
        self._widgets["but_delete_selected_points"].clicked.connect(
            self._widgets["table"].remove_selected_points
        )
        self._plot.sigPlotSignal.connect(self._process_plot_signal)
        self._widgets["table"].sig_new_selection.connect(self.__new_points_selected)
        self._widgets["table"].sig_remove_points.connect(self.__remove_points_from_plot)

    @property
    def points(self):
        """
        The points selected in the image.

        Returns
        -------
        x_positions : np.ndarray
            The x values of the selected points.
        y_positions : np.ndarray
            The y values of the selected points.
        """
        _n = len(self._points)
        _x = np.zeros((_n))
        _y = np.zeros((_n))
        for _index, (_xpos, _ypos) in enumerate(self._points):
            _x[_index] = _xpos
            _y[_index] = _ypos
        return _x, _y
        return [_point for _point in self._points]

    @QtCore.Slot(bool)
    def toggle_selection_active(self, active: bool):
        """
        Toggle the selection

        Parameters
        ----------
        active : bool
            The new activation state.
        """
        self._config["selection_active"] = active

    @QtCore.Slot(object)
    def __remove_points_from_plot(self, points: Tuple):
        """
        Remove the selected points from the plot.

        Parameters
        ----------
        points : list
            List with tuples of the (x, y) position of the points.
        """
        for _point in points:
            self._points.remove(_point)
            self._plot.removeMarker(f"marker_{_point[0]}_{_point[1]}")

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
            and self._config["selection_active"]
        ):
            _color = PYDIDAS_COLORS[self._config["marker_color"]]
            _x = np.round(event_dict["x"], decimals=3)
            _y = np.round(event_dict["y"], decimals=3)
            if (_x, _y) in self._points:
                return
            self._plot.addMarker(
                _x, _y, legend=f"marker_{_x}_{_y}", color=_color, symbol="x"
            )
            self._points.append((_x, _y))
            self._widgets["table"].add_point_to_table(_x, _y)

    @QtCore.Slot(object)
    def __new_points_selected(self, points):
        """
        Process the signal that new points have been selected.
        """
        for _point in self._points:
            _label = f"marker_{_point[0]}_{_point[1]}"
            _marker = self._plot._getItem("marker", _label)
            _symbol = "o" if _point in points else "x"
            _marker.setSymbol(_symbol)

    @QtCore.Slot(str)
    def set_marker_color(self, color):
        """
        Set the marker color for the markers.

        Parameters
        ----------
        color : str
            The new color name.
        """
        _colorcode = PYDIDAS_COLORS[color]
        _items = self._plot.getItems()
        for _item in _items:
            if isinstance(_item, (Marker, Shape)):
                _name = _item.getName()
                if _name.startswith("marker_") or _name == "beamcenter":
                    _item.setColor(_colorcode)

    def set_beamcenter_marker(self, position):
        """
        Mark the beamcenter with a marker.
        """
        if position is None:
            self._plot.remove(legend="beamcenter", kind="marker")
            return
        _color = PYDIDAS_COLORS[self._config["marker_color"]]
        self._plot.addMarker(*position, legend="beamcenter", color=_color, symbol="+")

    def remove_plot_items(
        self, *kind: Tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
    ):
        """
        Remove the selected items from the plot.

        Parameters
        ----------
        *kind : Tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
            The kind of items to be removed.
        """
        kind = ["marker", "beamcenter", "beamcenter_outline"] if "all" in kind else kind
        if "beamcenter" in kind:
            self.set_beamcenter_marker(None)
        if "beamcenter_outline" in kind:
            self.show_beamcenter_outline(None)
        if "marker" in kind:
            for _point in self._points:
                self._plot.removeMarker(f"marker_{_point[0]}_{_point[1]}")

    def show_beamcenter_outline(self, points):
        """
        Show an outline defined through the points.

        The outline can, for example, be a fitted circle or ellipse. The points must be
        given as a 2-tuple or None to clear the outline.

        Parameters
        ----------
        points : Union[None, tuple]
            The points for the outline in form of a tuple with x- and y- point
            positions. If None, the outline is cleared from the plot.
        """
        if points is None:
            self._plot.remove(legend="beamcenter_outline", kind="item")
            return
        _color = PYDIDAS_COLORS[self._config["marker_color"]]
        self._plot.addShape(
            points[0],
            points[1],
            legend="beamcenter_outline",
            color=_color,
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )
