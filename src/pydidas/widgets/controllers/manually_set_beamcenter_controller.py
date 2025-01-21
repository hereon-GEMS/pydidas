# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SetBeamcenterController class which handles selecting and fitting the
beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ManuallySetBeamcenterController"]


from collections.abc import Iterable
from pathlib import Path
from typing import Literal, NewType, Union

import numpy as np
import pyFAI
from qtpy import QtCore, QtWidgets

from pydidas.core import UserConfigError
from pydidas.core.constants import PYDIDAS_COLORS
from pydidas.core.utils import (
    calc_points_on_ellipse,
    fit_circle_from_points,
    fit_detector_center_and_tilt_from_points,
)
from pydidas.data_io import import_data


BaseFrame = NewType("BaseFrame", QtWidgets.QWidget)
PydidasPlot2d = NewType("PydidasPlot2d", QtWidgets.QWidget)
PointsForBeamcenterWidget = NewType("PointsForBeamcenterWidget", QtWidgets.QWidget)


class ManuallySetBeamcenterController(QtCore.QObject):
    """
    This class manages manually selecting and editing the beamcenter.

    This controller requires a PydidasPlot2D to pick up selected points and to draw the
    markers, as well as a parent widget which controls the beamcenter Parameters and a
    PointPositionTableWidget to represent the points.

    Parameters
    ----------
    parent_frame : pydidas.widgets.framework.BaseFrame
        The parent widget which displays the information.
    plot : pydidas.widgets.silx_plot.PydidasPlot2D
        The plot to draw markers etc.
    point_table : pydidas.widgets.misc.PointsForBeamcenterWidget
        The table to store the selected points.
    """

    sig_selected_beamcenter = QtCore.Signal()

    def __init__(
        self,
        parent_frame: BaseFrame,
        plot: PydidasPlot2d,
        point_table: PointsForBeamcenterWidget,
        **kwargs: dict,
    ):
        QtCore.QObject.__init__(self)
        self._config = {
            "selection_active": kwargs.get("selection_active", True),
            "2click_selection": True,
            "wait_for_2nd_click": False,
            "overlay_color": kwargs.get("overlay_color", PYDIDAS_COLORS["orange"]),
            "beamcenter_set": False,
            "beamcenter_outline_points": None,
            "selected_points": [],
            "beamcenter_position": None,
        }
        self._points = []
        self._parent_frame = parent_frame
        self._plot = plot
        self._points_for_bc = point_table
        self._mask = None
        self._mask_hash = -1
        self._plot.sigPlotSignal.connect(self._process_plot_signal)
        self._points_for_bc.sig_new_selection.connect(self.__new_points_selected)
        self._points_for_bc.sig_remove_points.connect(self.__remove_points_from_plot)
        self._points_for_bc.param_widgets["overlay_color"].io_edited.connect(
            self.set_marker_color
        )
        self._points_for_bc.sig_2click_usage.connect(self.toggle_2click_selection)

        self._parent_frame.param_widgets["beamcenter_x"].io_edited.connect(
            self.manual_beamcenter_update
        )
        self._parent_frame.param_widgets["beamcenter_y"].io_edited.connect(
            self.manual_beamcenter_update
        )

    @property
    def points(self) -> tuple[np.ndarray, np.ndarray]:
        """
        The points marked in the image.

        Returns
        -------
        x_positions : np.ndarray
            The x values of the selected points.
        y_positions : np.ndarray
            The y values of the selected points.
        """
        return self._get_points_as_arrays(self._points)

    @property
    def selected_points(self) -> tuple[np.ndarray, np.ndarray]:
        """
        The currently selected points in the image.

        Returns
        -------
        x_positions : np.ndarray
            The x values of the selected points.
        y_positions : np.ndarray
            The y values of the selected points.
        """
        return self._get_points_as_arrays(self._config["selected_points"])

    def _get_points_as_arrays(self, points: list[tuple[float, float]]):
        """
        Get the given list of points as arrays.

        Parameters
        ----------
        points : list[tuple[float, float]]
            The points to be processed.

        Returns
        -------
        np.ndarray, np.ndarray :
            The x and y positions of the selected points.
        """
        _x = np.zeros((len(points)))
        _y = np.zeros((len(points)))
        for _index, (_xpos, _ypos) in enumerate(points):
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
        self._config["overlay_color"] = PYDIDAS_COLORS[color]
        _marker_keys = [f"marker_{_point[0]}_{_point[1]}" for _point in self._points]
        _marker_keys.append("beamcenter")
        for _key in _marker_keys:
            _item = self._plot._getItem("marker", legend=_key)
            if _item is not None:
                _item.setColor(self._config["overlay_color"])
        _item = self._plot._getItem("item", legend="beamcenter_outline")
        if _item is not None:
            _item.setColor(self._config["overlay_color"])

    def remove_plot_items(
        self, *kind: tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
    ):
        """
        Remove the selected items from the plot.

        Parameters
        ----------
        *kind : tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
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
        self, *kind: tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
    ):
        """
        Show the selected items in the plot.

        Parameters
        ----------
        *kind : tuple[Literal["all", "marker", "beamcenter", "beamcenter_outline"]]
            The kind of items to be removed.
        """
        kind = ["marker", "beamcenter", "beamcenter_outline"] if "all" in kind else kind
        if "beamcenter" in kind and self._config["beamcenter_position"] is not None:
            self._plot.addMarker(
                *self._config["beamcenter_position"],
                legend="beamcenter",
                color=self._config["overlay_color"],
                symbol="d",
            )
        if (
            "beamcenter_outline" in kind
            and self._config["beamcenter_outline_points"] is not None
        ):
            self._plot_beamcenter_outline(*self._config["beamcenter_outline_points"])
        if "marker" in kind:
            for _point in self._points:
                _label = f"marker_{_point[0]}_{_point[1]}"
                _symbol = "o" if _point in self._config["selected_points"] else "x"
                self._plot.addMarker(
                    *_point,
                    legend=_label,
                    color=self._config["overlay_color"],
                    symbol=_symbol,
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
        self._points_for_bc.setVisible(active)

    @QtCore.Slot(bool)
    def toggle_2click_selection(self, use_2_clicks: bool):
        """
        Toggle the 2-click selection for points.

        Parameters
        ----------
        use_2_clicks : bool
            Flag to activate/deactivate 2-point selection.
        """
        self._config["2click_selection"] = use_2_clicks
        if self._config["wait_for_2nd_click"]:
            self._plot.resetZoom()
            self._plot.getImage().getColormap().setVRange(
                *self._config["2click_cmap_limits"]
            )
        self._config["wait_for_2nd_click"] = False

    @QtCore.Slot(dict)
    def _process_plot_signal(self, event_dict):
        """
        Process events from the plot and filter and process mouse clicks.

        Parameters
        ----------
        event_dict : dict
            The silx event dictionary.
        """
        if not (
            event_dict["event"] == "mouseClicked"
            and event_dict.get("button", "None") == "left"
            and self._config["selection_active"]
        ):
            return
        _x = np.round(event_dict["x"], decimals=3)
        _y = np.round(event_dict["y"], decimals=3)
        if self._config["2click_selection"] and not self._config["wait_for_2nd_click"]:
            self.__process_click_one_of_two(_x, _y)
            return
        if self._config["2click_selection"] and self._config["wait_for_2nd_click"]:
            self.__process_click_two_of_two()
        if (_x, _y) in self._points:
            return
        _color = self._config["overlay_color"]
        self._plot.addMarker(
            _x, _y, legend=f"marker_{_x}_{_y}", color=_color, symbol="x"
        )
        self._points.append((_x, _y))
        self._points_for_bc.add_point_to_table(_x, _y)

    def __process_click_one_of_two(self, x: float, y: float):
        """
        Process the first click for the two-click selection.

        Parameters
        ----------
        x : float
            The x-coordinate of the click.
        y : float
            The y-coordinate of the click.
        """
        _cmap = self._plot.getImage().getColormap()
        self._config["2click_xlimits"] = self._plot.getGraphXLimits()
        self._config["2click_ylimits"] = self._plot.getGraphYLimits()
        self._config["2click_cmap_limits"] = _cmap.getVRange()

        _delta = 50

        _data = self._plot.getImage().getData(copy=False)
        _x0 = int(np.round(max(0, x - _delta)))
        _x1 = int(np.round(min(_data.shape[1], x + _delta)))
        _y0 = int(np.round(max(0, y - _delta)))
        _y1 = int(np.round(min(_data.shape[0], y + _delta)))

        _data = _data[_y0:_y1, _x0:_x1]
        if self._mask is not None:
            _data = np.ma.masked_array(_data, mask=self._mask[_y0:_y1, _x0:_x1])

        self._plot.setLimits(_x0, _x1, _y0, _y1)
        _cmap.setVRange(np.amin(_data), np.amax(_data))
        self._config["wait_for_2nd_click"] = True

    def __process_click_two_of_two(self):
        """
        Process the second click in the two-click selection.
        """
        self._plot.setLimits(
            *self._config["2click_xlimits"], *self._config["2click_ylimits"]
        )
        self._config["wait_for_2nd_click"] = False
        self._plot.getImage().getColormap().setVRange(
            *self._config["2click_cmap_limits"]
        )

    @QtCore.Slot()
    def set_beamcenter_from_point(self):
        """
        Set the beamcenter from a single point.
        """
        _x, _y = self.selected_points
        if _x.size != 1 and len(self._points) == 1:
            _x, _y = self.points
        if _x.size != 1:
            raise UserConfigError(
                "Please select exactly one point in the image to set the beamcenter "
                "directly."
            )
        self._set_beamcenter_marker((_x[0], _y[0]))
        self.remove_plot_items("beamcenter_outline")
        self._parent_frame.set_param_value_and_widget("beamcenter_x", _x[0])
        self._parent_frame.set_param_value_and_widget("beamcenter_y", _y[0])
        self.sig_selected_beamcenter.emit()

    def _set_beamcenter_marker(self, position: tuple[float, float]):
        """
        Mark the beamcenter with a marker.

        Parameters
        ----------
        position : tuple[float, float]
            The (x, y) position of the beamcenter.
        """
        _color = self._config["overlay_color"]
        self._config["beamcenter_position"] = position
        self._plot.addMarker(*position, legend="beamcenter", color=_color, symbol="d")
        self._toggle_beamcenter_is_set(True)

    @QtCore.Slot()
    def fit_beamcenter_with_circle(self):
        """
        Fit the beamcenter through a circle.
        """
        _x, _y = self.points
        if _x.size < 3:
            raise UserConfigError(
                "Please select at least three points to fit a circle for beamcenter "
                "determination."
            )
        _cx, _cy, _r = fit_circle_from_points(_x, _y)
        self._set_beamcenter_marker((_cx, _cy))
        self._parent_frame.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self._parent_frame.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        self._toggle_beamcenter_is_set(True)
        _theta = np.linspace(0, 2 * np.pi, num=73, endpoint=True)
        _x = np.cos(_theta) * _r + _cx
        _y = np.sin(_theta) * _r + _cy
        self._plot_beamcenter_outline(_x, _y)
        self.sig_selected_beamcenter.emit()

    @QtCore.Slot()
    def fit_beamcenter_with_ellipse(self):
        """
        Fit the beamcenter through an ellipse.
        """
        _x, _y = self.points
        if _x.size < 5:
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
        self._parent_frame.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self._parent_frame.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        _x, _y = calc_points_on_ellipse(_coeffs)
        self._plot_beamcenter_outline(_x, _y)
        self.sig_selected_beamcenter.emit()

    def set_mask_file(self, mask: Union[None, Path]):
        """
        Set the mask file.

        Parameters
        ----------
        mask : Union[None, Path]
            The path to the mask file or None to skip masking.
        """
        if mask is None:
            self._mask = None
            self._mask_hash = -1
            return
        if mask.is_file():
            if hash(mask) == self._mask_hash:
                return
            self._mask = import_data(mask)
            self._mask_hash = hash(mask)

    def set_new_detector_with_mask(self, detector_name: str):
        """
        Process the input of a new detector to select the generic mask.

        Parameters
        ----------
        detector_name : str
            The name of the detector.
        """
        self._mask = pyFAI.detector_factory(detector_name).mask
        self._mask_hash = hash("detector-name::" + detector_name)

    def _toggle_beamcenter_is_set(self, is_set: bool):
        """
        Toggle the visibility of the Parameter widgets for the results.

        Parameters
        ----------
        is_set : bool
            The new visibility.
        """
        for _name in ["beamcenter_x", "beamcenter_y"]:
            self._parent_frame.param_composite_widgets[_name].setVisible(is_set)
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
            if _point in self._config["selected_points"]:
                _index = self._config["selected_points"].index(_point)
                self._config["selected_points"].pop(_index)

    @QtCore.Slot(str)
    def manual_beamcenter_update(self, *arg):
        """
        Process a manual update of the beamcenter x/y Parameter.
        """
        _x = self._parent_frame.get_param_value("beamcenter_x")
        _y = self._parent_frame.get_param_value("beamcenter_y")
        self._config["beamcenter_position"] = (_x, _y)
        if self.selection_active:
            self._set_beamcenter_marker((_x, _y))
            self.remove_plot_items("beamcenter_outline")

    def _plot_beamcenter_outline(
        self, xpoints: tuple[float, ...], ypoints: tuple[float, ...]
    ):
        """
        Plot an outline from the beamcenter fit defined through the points.

        The outline can, for example, be a fitted circle or ellipse. The points must be
        given as a 2-tuple.

        Parameters
        ----------
        xpoints : tuple[float, ...]
            The x positions of the points for the outline in form of a tuple.
        ypoints : tuple[float, ...]
            The y positions of the points for the outline in form of a tuple.
        """
        self._config["beamcenter_outline_points"] = (xpoints, ypoints)
        self._plot.addShape(
            xpoints,
            ypoints,
            legend="beamcenter_outline",
            color=self._config["overlay_color"],
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )
