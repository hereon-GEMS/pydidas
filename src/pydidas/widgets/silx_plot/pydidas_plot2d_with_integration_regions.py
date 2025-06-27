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
#
# ruff: noqa: C901

"""
Module with the PydidasPlot2DwithIntegrationRegions class which extends the
PydidasPlot2D with functionality to draw integration regions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot2DwithIntegrationRegions"]


from typing import Tuple, Union

import numpy as np
from qtpy import QtCore

from pydidas.core.constants import PYDIDAS_COLORS
from pydidas.core.math import (
    Point,
    PointFromPolar,
    PointList,
    ray_intersects_with_detector,
)
from pydidas.widgets.silx_plot.pydidas_plot2d import PydidasPlot2D


cos_phi = np.cos(np.linspace(0, 2 * np.pi, num=145))
sin_phi = np.sin(np.linspace(0, 2 * np.pi, num=145))


class PydidasPlot2DwithIntegrationRegions(PydidasPlot2D):
    """
    An extended PydidasPlot2D which allows to show integration regions.
    """

    sig_new_point_selected = QtCore.Signal(float, float)

    def __init__(self, **kwargs: dict):
        PydidasPlot2D.__init__(self, **kwargs)
        self._config["overlay_color"] = kwargs.get(
            "overlay_color", PYDIDAS_COLORS["orange"]
        )
        self._config["roi_active"] = False
        self._process_exp_update()
        self.sigPlotSignal.connect(self._process_plot_signal)
        self._config["diffraction_exp"].sig_params_changed.connect(
            self._process_exp_update
        )

    @property
    def det_corner_points(self) -> PointList:
        """
        Get a list of the detector corner points.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _points = PointList()
        _points.append(Point(0, 0))
        _points.append(Point(0, _ny))
        _points.append(Point(_nx, _ny))
        _points.append(Point(_nx, 0))
        return _points

    @QtCore.Slot()
    def _process_exp_update(self):
        """
        Process updates of the DiffractionExperiment.
        """
        self._config["beamcenter"] = self._config["diffraction_exp"].beamcenter

    def set_marker_color(self, color: str):
        """
        Set the new marker color.

        Parameters
        ----------
        color : str
            The marker color name.
        """
        self._config["overlay_color"] = PYDIDAS_COLORS[color]

    def draw_circle(
        self,
        radius: float,
        legend: str,
        center: Union[None, Tuple[float, float]] = None,
    ):
        """
        Draw a circle with the given radius and store it as the given legend.

        Parameters
        ----------
        radius : float
            The circle radius in pixels.
        legend : str
            The shape's legend for referencing it in the plot.
        center : Union[None, Tuple[float, float]], optional
            The center of the circle. If None, this defaults to the
            DiffractionExperiment beamcenter. The default is None.
        """
        _cx, _cy = self._config["beamcenter"] if center is None else center
        self.addShape(
            radius * cos_phi + _cx,
            radius * sin_phi + _cy,
            legend=legend,
            color=self._config["overlay_color"],
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )

    def draw_line_from_beamcenter(self, chi: float, legend: str):
        """
        Draw a line from the beamcenter in the direction given by the angle chi.

        Parameters
        ----------
        chi : float
            The pointing angle, given in rad.
        legend : str
            The reference legend entry for this line.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _center = Point(self._config["beamcenter"])
        _intersects = ray_intersects_with_detector(_center, chi, (_ny, _nx))
        if len(_intersects) == 0:
            return
        if len(_intersects) == 1:
            _intersects.insert(0, _center)
        self.addShape(
            _intersects.xarr,
            _intersects.yarr,
            legend=legend,
            shape="polylines",
            color=self._config["overlay_color"],
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )

    def draw_integration_region(
        self,
        radial: tuple[float, float] | None,
        azimuthal: tuple[float, float] | None,
    ):
        """
        Draw the given integration region.

        Parameters
        ----------
        radial : tuple[float, float] | None
            The radial integration region. Use None for the full detector or a tuple
            with (r_inner, r_outer) in pixels to select a region.
        azimuthal : tuple[float, float] | None
            The azimuthal integration region. Use None for the full detector or a tuple
            with (azi_start, azi_end) in radians for a region.
        """
        if isinstance(azimuthal, tuple):
            if np.mod(azimuthal, 2 * np.pi).std() < 1e-6:
                azimuthal = None
        if radial is None and azimuthal is None:
            _points = self.det_corner_points
        elif radial is not None:
            _points = self._handle_radial_region(radial, azimuthal)
        else:
            _points = self._handle_azimuthal_region(azimuthal)
        self.addShape(
            _points.xarr,
            _points.yarr,
            legend="roi",
            color=self._config["overlay_color"],
            linewidth=2.0,
        )
        self._config["roi_active"] = True

    def _handle_radial_region(
        self, radial: tuple[float, float], azimuthal: None | tuple[float, float]
    ) -> PointList:
        """
        Handle the radial region drawing logic.

        Parameters
        ----------
        radial : tuple[float, float]
            The radial integration region as (r_inner, r_outer) in pixels.
        azimuthal : None | tuple[float, float]
            The azimuthal integration region as (azi_start, azi_end) in radians or
            None for the full detector.

        Returns
        -------
        points : PointList
            The coordinates of the radial integration region.
        """
        _center = Point(self._config["beamcenter"])
        _phi = (
            np.linspace(0, 2 * np.pi, num=145)
            if azimuthal is None
            else np.linspace(azimuthal[0], azimuthal[1], num=145)
        )
        _points = PointList()
        for _p in _phi:
            _points.append(_center + PointFromPolar(radial[0], _p))
        for _p in _phi[::-1]:
            _points.append(_center + PointFromPolar(radial[1], _p))
        _points.append(_center + PointFromPolar(radial[0], _phi[0]))
        return _points

    def _handle_azimuthal_region(self, azimuthal: tuple[float, float]) -> PointList:
        """
        Handle the azimuthal region drawing logic.

        Parameters
        ----------
        azimuthal : tuple[float, float]
            The azimuthal integration region as (azi_start, azi_end) in radians.

        Returns
        -------
        points : PointList
            A list of Point objects representing the corners of the azimuthal
            integration region on the detector.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _center = Point(self._config["beamcenter"])
        _center_on_det = 0 <= _center.x <= _nx and 0 <= _center.y <= _ny

        _intersects0 = ray_intersects_with_detector(_center, azimuthal[0], (_ny, _nx))
        _intersects1 = ray_intersects_with_detector(_center, azimuthal[1], (_ny, _nx))
        if _center_on_det:
            _points = self._get_outline(_intersects0[0], _intersects1[0])
            _points.insert(0, _center)
            _points.append(_center)
            return _points
        # center off detector
        _points = PointList()
        if len(_intersects0) == 0 and len(_intersects1) == 0:
            # no intersections, i.e. either full detector or no point on
            # detector in roi
            _chi_det = (Point(_nx / 2, _ny / 2) - _center).chi
            if azimuthal[0] < _chi_det < azimuthal[1]:
                _points.extend(self.det_corner_points)
            else:
                self.remove_plot_items("roi")  # noqa E1101
        elif len(_intersects0) == 2 and len(_intersects1) == 2:
            _points = self._get_outline(_intersects1[0], _intersects0[0])
            _points2 = self._get_outline(_intersects0[1], _intersects1[1])
            _points.extend(_points2)
        elif len(_intersects0) == 0 and len(_intersects1) == 2:
            _points = self._get_outline(_intersects1[0], _intersects1[1])
        elif len(_intersects0) == 2 and len(_intersects1) == 0:
            _points = self._get_outline(_intersects0[1], _intersects0[0])
        return _points

    def _get_outline(self, startpoint: Point, endpoint: Point) -> PointList:
        """
        Get the outline including the corners between startpoint and endpoint.

        Starting at the startpoint, follow the detector outline in a positive rotation
        and tag all corner points which are covered before reaching the endpoint.
        This method also includes the start- and endpoint.

        Parameters
        ----------
        startpoint : Point
            The starting point (x, y)
        endpoint : Point
            The endpoint (x, y)

        Returns
        -------
        PointList
            A list of Point objects representing the corner points between the start
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _points = PointList([startpoint])
        while True:
            if _points[-1].y == 0:
                if endpoint.x > _points[-1].x and endpoint.y == 0:
                    break
                _points.append(Point(_nx, 0))
            if _points[-1].x == _nx:
                if endpoint.y > _points[-1].y and endpoint.x == _nx:
                    break
                _points.append(Point(_nx, _ny))
            if _points[-1].y == _ny:
                if endpoint.x < _points[-1].x and endpoint.y == _ny:
                    break
                _points.append(Point(0, _ny))
            if _points[-1].x == 0:
                if endpoint.y < _points[-1].y and endpoint.x == 0:
                    break
                _points.append(Point(0, 0))
        _points.append(endpoint)
        return _points

    @QtCore.Slot(dict)
    def _process_plot_signal(self, event_dict: dict):
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
            _x = np.round(event_dict["x"], decimals=3)
            _y = np.round(event_dict["y"], decimals=3)
            self.sig_new_point_selected.emit(_x, _y)
