# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SetBeamcenterController class which handles selecting and fitting the
beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ManuallySetBeamcenterController"]


from typing import Iterable, Literal, Tuple

import numpy as np
from qtpy import QtCore
from silx.gui.plot.items import Marker, Shape

from ...core import UserConfigError
from ...core.constants import PYDIDAS_COLORS
from ...core.utils import (
    calc_points_on_ellipse,
    fit_circle_from_points,
    fit_detector_center_and_tilt_from_points,
)


class ManuallySetBeamcenterController(QtCore.QObject):
    """
    This class manages manually selecting and editing the beamcenter.

    This controller requires a PydidasPlot2D to pick up selected points and to draw the
    markers, as well as a master widget which controls the beamcenter Parameters and a
    PointPositionTableWidget to represent the points.

    Parameters
    ----------
    master : pydidas.widgets.framework.BaseFrame
        The master widget which displays the information.
    plot : pydidas.widgets.silx_plot.PydidasPlot2D
        The plot to draw markers etc.
    point_table : pydidas.widgets.misc.PointPositionTableWidget
        The table to store the selected points.
    """

    sig_selected_beamcenter = QtCore.Signal(float, float)

    def __init__(self, master, plot, point_table, **kwargs):
        QtCore.QObject.__init__(self)
        self._config = {
            "selection_active": kwargs.get("selection_active", True),
            "marker_color": kwargs.get("marker_color", "orange"),
            "beamcenter_set": False,
            "beamcenter_outline_points": None,
            "selected_points": [],
            "beamcenter_position": None,
        }
        self._points = []
        self._master = master
        self._plot = plot
        self._point_table = point_table
        self._plot.sigPlotSignal.connect(self._process_plot_signal)
        self._point_table.sig_new_selection.connect(self.__new_points_selected)
        self._point_table.sig_remove_points.connect(self.__remove_points_from_plot)
        self._master.param_widgets["beamcenter_x"].io_edited.connect(
            self._manual_beamcenter_update
        )
        self._master.param_widgets["beamcenter_y"].io_edited.connect(
            self._manual_beamcenter_update
        )

    @property
    def points(self) -> Tuple[np.ndarray, np.ndarray]:
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

    @property
    def beamcenter_is_set(self) -> bool:
        """
        Get the flag whether the beamcenter has been set.

        Returns
        -------
        bool :
            Flag whether the beamcenter has been set.
        """
        return self._config["beamcenter_set"]

    @property
    def selection_active(self) -> bool:
        """
        Get the flag whether the selection is active.

        Returns
        -------
        bool
            Selection active flag.
        """
        return self._config["selection_active"]

    @QtCore.Slot(str)
    def set_marker_color(self, color: str):
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
            self._plot.remove(legend="beamcenter", kind="marker")
        if "beamcenter_outline" in kind:
            self._plot.remove(legend="beamcenter_outline", kind="item")
        if "marker" in kind:
            for _point in self._points:
                self._plot.removeMarker(f"marker_{_point[0]}_{_point[1]}")

    def show_plot_items(
        self, *kind: Tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
    ):
        """
        Show the selected items in the plot.

        Parameters
        ----------
        *kind : Tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
            The kind of items to be removed.
        """
        kind = ["marker", "beamcenter", "beamcenter_outline"] if "all" in kind else kind
        if "beamcenter" in kind and self._config["beamcenter_position"] is not None:
            self._plot.addMarker(
                *self._config["beamcenter_position"],
                legend="beamcenter",
                color=PYDIDAS_COLORS[self._config["marker_color"]],
                symbol="+",
            )
        if (
            "beamcenter_outline" in kind
            and self._config["beamcenter_outline_points"] is not None
        ):
            self._plot_beamcenter_outline(self._config["beamcenter_outline_points"])
        if "marker" in kind:
            _color = PYDIDAS_COLORS[self._config["marker_color"]]
            for _point in self._points:
                _label = f"marker_{_point[0]}_{_point[1]}"
                _symbol = "o" if _point in self._config["selected_points"] else "x"
                self._plot.addMarker(
                    _point[0], _point[1], legend=_label, color=_color, symbol=_symbol
                )

    @QtCore.Slot(bool)
    def toggle_selection_active(self, active: bool):
        """
        Toggle the selection mode.

        Parameters
        ----------
        active : bool
            The new activation state.
        """
        self._config["selection_active"] = active
        self._point_table.setVisible(active)

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
            self._point_table.add_point_to_table(_x, _y)

    @QtCore.Slot()
    def set_beamcenter_from_point(self):
        """
        Set the beamcenter from a single point.
        """
        _x, _y = self.points
        if _x.size != 1:
            self._toggle_beamcenter_is_set(False)
            self.remove_plot_items("beamcenter")
            self.remove_plot_items("beamcenter_outline")
            raise UserConfigError(
                "Please select exactly one point in the image to set the beamcenter "
                "directly."
            )
        self._set_beamcenter_marker((_x[0], _y[0]))
        self.remove_plot_items("beamcenter_outline")
        self._master.set_param_value_and_widget("beamcenter_x", _x[0])
        self._master.set_param_value_and_widget("beamcenter_y", _y[0])

    def _set_beamcenter_marker(self, position: Tuple[float, float]):
        """
        Mark the beamcenter with a marker.

        Parameters
        ----------
        position : Tuple[float, float]
            The (x, y) position of the beamcenter.
        """
        _color = PYDIDAS_COLORS[self._config["marker_color"]]
        self._config["beamcenter_position"] = position
        self._plot.addMarker(*position, legend="beamcenter", color=_color, symbol="+")
        self._toggle_beamcenter_is_set(True)

    @QtCore.Slot()
    def fit_beamcenter_with_circle(self):
        """
        Fit the beamcenter through a circle.
        """
        _x, _y = self.points
        if _x.size < 3:
            self._toggle_beamcenter_is_set(False)
            self.remove_plot_items("beamcenter")
            self.remove_plot_items("beamcenter_outline")
            raise UserConfigError(
                "Please select at least three points to fit a circle for beamcenter "
                "determination."
            )
        _cx, _cy, _r = fit_circle_from_points(_x, _y)
        self._set_beamcenter_marker((_cx, _cy))
        self._master.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self._master.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        self._toggle_beamcenter_is_set(True)
        _theta = np.linspace(0, 2 * np.pi, num=73, endpoint=True)
        _x = np.cos(_theta) * _r + _cx
        _y = np.sin(_theta) * _r + _cy
        self._plot_beamcenter_outline((_x, _y))

    @QtCore.Slot()
    def fit_beamcenter_with_ellipse(self):
        """
        Fit the beamcenter through an ellipse.
        """
        _x, _y = self.points
        if _x.size < 5:
            self._toggle_beamcenter_is_set(False)
            self.remove_plot_items("beamcenter")
            self.remove_plot_items("beamcenter_outline")
            raise UserConfigError(
                "Please select at least five points to fit a fully-defined ellipse "
                "for beamcenter determination."
            )
        (
            _cx,
            _cy,
            _tilt,
            _tilt_plane,
            _coeffs,
        ) = fit_detector_center_and_tilt_from_points(_x, _y)
        self._set_beamcenter_marker((_cx, _cy))
        self._master.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self._master.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        _x, _y = calc_points_on_ellipse(_coeffs)
        self._plot_beamcenter_outline((_x, _y))

    def _toggle_beamcenter_is_set(self, is_set: bool):
        """
        Toggle the visibility of the Parameter widgets for the results.

        Parameters
        ----------
        is_set : bool
            The new visibility.
        """
        for _name in ["beamcenter_x", "beamcenter_y"]:
            self._master.param_composite_widgets[_name].setVisible(is_set)
        self._config["beamcenter_set"] = is_set

    @QtCore.Slot(object)
    def __new_points_selected(self, points: Iterable[str]):
        """
        Process the signal that new points have been selected.

        Parameters
        ----------
        points : Iterable[str]
            An iterable (tuple, list) with the string names of the points.
        """
        self._config["selected_points"] = points
        for _point in self._points:
            _label = f"marker_{_point[0]}_{_point[1]}"
            _marker = self._plot._getItem("marker", _label)
            _symbol = "o" if _point in points else "x"
            _marker.setSymbol(_symbol)

    @QtCore.Slot(object)
    def __remove_points_from_plot(self, points: Iterable[str]):
        """
        Remove the selected points from the plot.

        Parameters
        ----------
        points : Iterable[str]
            An iterable (tuple, list) with the string names of the points.
        """
        for _point in points:
            self._points.remove(_point)
            self._plot.removeMarker(f"marker_{_point[0]}_{_point[1]}")

    @QtCore.Slot(str)
    def _manual_beamcenter_update(self, pos: str):
        """
        Process a manual update of the beamcenter x/y Parameter.

        Parameters
        ----------
        pos : str
            The new beamcenter pos value.
        """
        _x = self._master.get_param_value("beamcenter_x")
        _y = self._master.get_param_value("beamcenter_y")
        self._config["beamcenter_position"] = (_x, _y)
        if self.selection_active:
            self._set_beamcenter_marker((_x, _y))
            self.remove_plot_items("beamcenter_outline")

    def _plot_beamcenter_outline(self, points: Tuple[Tuple, Tuple]):
        """
        Plot an outline from the beamcenter fit defined through the points.

        The outline can, for example, be a fitted circle or ellipse. The points must be
        given as a 2-tuple.

        Parameters
        ----------
        points : Tuple[Tuple, Tuple]
            The points for the outline in form of a tuple with x- and y- point
            positions.
        """
        _color = PYDIDAS_COLORS[self._config["marker_color"]]
        self._config["beamcenter_outline_points"] = points
        self._plot.addShape(
            points[0],
            points[1],
            legend="beamcenter_outline",
            color=_color,
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )
