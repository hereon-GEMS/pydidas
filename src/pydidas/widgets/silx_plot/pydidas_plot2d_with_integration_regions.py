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
from pydidas.core.utils import (
    get_chi_from_x_and_y,
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
        _cx, _cy = self._config["beamcenter"]
        _intersects = ray_intersects_with_detector((_cx, _cy), chi, (_ny, _nx))
        if len(_intersects) == 0:
            return
        if len(_intersects) == 1:
            _intersects.insert(0, (_cx, _cy))
        self.addShape(
            np.array([p[0] for p in _intersects]),
            np.array([p[1] for p in _intersects]),
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
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _cx, _cy = self._config["beamcenter"]
        _center_on_det = 0 <= _cx <= _nx and 0 <= _cy <= _ny
        if radial is None and azimuthal is None:
            _xarr = np.array([0, 0, _nx, _nx])
            _yarr = np.array([0, _ny, _ny, 0])
        elif radial is not None:
            _xarr, _yarr = self._handle_radial_region(radial, azimuthal)
        else:
            _xarr, _yarr = self._handle_azimuthal_region(azimuthal)

        self.addShape(
            _xarr,
            _yarr,
            legend="roi",
            color=self._config["overlay_color"],
            linewidth=2.0,
        )
        self._config["roi_active"] = True

    def _handle_radial_region(
        self, radial: tuple[float, float], azimuthal: None | tuple[float, float]
    ):
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
        _xarr : np.ndarray
            The x coordinates of the radial integration region.
        _yarr : np.ndarray

        """
        _cx, _cy = self._config["beamcenter"]
        _phi = (
            np.linspace(0, 2 * np.pi, num=145)
            if azimuthal is None
            else np.linspace(azimuthal[0], azimuthal[1], num=145)
        )
        _xarr = _cx + np.concatenate(
            (
                radial[0] * np.cos(_phi),
                radial[1] * np.cos(_phi[::-1]),
                (radial[0] * np.cos(_phi[0]),),
            )
        )
        _yarr = _cy + np.concatenate(
            (
                radial[0] * np.sin(_phi),
                radial[1] * np.sin(_phi[::-1]),
                (radial[0] * np.sin(_phi[0]),),
            )
        )
        return _xarr, _yarr

    def _handle_azimuthal_region(
        self, azimuthal: tuple[float, float]
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Handle the azimuthal region drawing logic.

        Parameters
        ----------
        azimuthal : tuple[float, float]
            The azimuthal integration region as (azi_start, azi_end) in radians.

        Returns
        -------
        _xarr : np.ndarray
            The x coordinates of the azimuthal integration region.
        _yarr : np.ndarray
            The y coordinates of the azimuthal integration region.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _cx, _cy = self._config["beamcenter"]
        _center_on_det = 0 <= _cx <= _nx and 0 <= _cy <= _ny

        _intersects0 = ray_intersects_with_detector(
            (_cx, _cy), azimuthal[0], (_ny, _nx)
        )
        _intersects1 = ray_intersects_with_detector(
            (_cx, _cy), azimuthal[1], (_ny, _nx)
        )
        if _center_on_det:
            _xcorners, _ycorners = self._get_included_corners(
                _intersects0[0], _intersects1[0]
            )
            _xpoints = np.asarray([_cx] + _xcorners + [_cx])
            _ypoints = np.asarray([_cy] + _ycorners + [_cy])
            return _xpoints, _ypoints
        # center off detector
        if len(_intersects0) == 0 and len(_intersects1) == 0:
            # no intersections, i.e. either full detector or no point on
            # detector in roi
            _chi_det = get_chi_from_x_and_y(_nx / 2 - _cx, _ny / 2 - _cy)
            if azimuthal[0] < _chi_det < azimuthal[1]:
                _xpoints = [0, 0, _nx, _nx]
                _ypoints = [0, _ny, _ny, 0]
            else:
                self.remove_plot_items("roi")
                return np.array([]), np.array([])
        elif len(_intersects0) == 2 and len(_intersects1) == 2:
            _xpoints, _ypoints = self._get_included_corners(
                _intersects1[0], _intersects0[0]
            )
            _p2x, _p2y = self._get_included_corners(_intersects0[1], _intersects1[1])
            _xpoints.extend(_p2x)
            _ypoints.extend(_p2y)
        elif len(_intersects0) == 0 and len(_intersects1) == 2:
            _xpoints, _ypoints = self._get_included_corners(
                _intersects1[0], _intersects1[1]
            )
        elif len(_intersects0) == 2 and len(_intersects1) == 0:
            _xpoints, _ypoints = self._get_included_corners(
                _intersects0[1], _intersects0[0]
            )
        _xarr = np.asarray(_xpoints)
        _yarr = np.asarray(_ypoints)
        return _xarr, _yarr

    def _get_included_corners(
        self, startpoint: tuple[float, float], endpoint: tuple[float, float]
    ) -> tuple[list[int]]:
        """
        Get the corners on the detector outline between startpoint and endpoint.

        Starting at the startpoint, follow the detector outline in a positive rotation
        and tag all corner points which are covered before reaching the endpoint.
        This method also includes the start- and endpoint.

        Parameters
        ----------
        startpoint : tuple[float, float]
            The starting point (x, y)
        endpoint : tuple[float, float]
            The endpoint (x, y)

        Returns
        -------
        x_corners : list[int]
            The x-positions of the corner points.
        y_corners : list[int]
            The y-positions of the corner points.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _ex, _ey = endpoint
        _points = [startpoint]
        while True:
            if _points[-1][1] == 0 and _ey != 0:
                _points.append((_nx, 0))
            elif _points[-1][1] == 0:
                if _ex > _points[-1][0]:
                    break
                _points.append((_nx, 0))
            if _points[-1][0] == _nx and _ex != _nx:
                _points.append((_nx, _ny))
            elif _points[-1][0] == _nx:
                if _ey > _points[-1][1]:
                    break
                _points.append((_nx, _ny))
            if _points[-1][1] == _ny and _ey != _ny:
                _points.append((0, _ny))
            elif _points[-1][1] == _ny:
                if _ex < _points[-1][0]:
                    break
                _points.append((0, _ny))
            if _points[-1][0] == 0 and _ex != 0:
                _points.append((0, 0))
            elif _points[-1][0] == 0:
                if _ey < _points[-1][1]:
                    break
                _points.append((0, 0))
        _points.append((_ex, _ey))
        _c_x = [_p[0] for _p in _points]
        _c_y = [_p[1] for _p in _points]
        return _c_x, _c_y

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
