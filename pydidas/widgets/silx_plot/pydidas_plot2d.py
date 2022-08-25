# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with silx actions for PlotWindows.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlot2D"]

import numpy as np
from qtpy import QtCore
from silx.gui.plot import Plot2D

from ...experiment import SetupExperiment
from .silx_actions import ChangeCanvasToData, ExpandCanvas, CropHistogramOutliers
from .coordinate_transform_button import CoordinateTransformButton


EXP_SETUP = SetupExperiment()


class PydidasPlot2D(Plot2D):
    """
    A customized silx.gui.plot.Plot2D with an additional features to limit the figure
    canvas to the data limits.
    """

    def __init__(self, parent=None, backend=None):
        Plot2D.__init__(self, parent, backend)

        self.changeCanvasToDataAction = self.group.addAction(
            ChangeCanvasToData(self, parent=self)
        )
        self.changeCanvasToDataAction.setVisible(True)
        self.addAction(self.changeCanvasToDataAction)
        self._toolbar.insertAction(self.colormapAction, self.changeCanvasToDataAction)

        self.expandCanvasAction = self.group.addAction(ExpandCanvas(self, parent=self))
        self.expandCanvasAction.setVisible(True)
        self.addAction(self.expandCanvasAction)
        self._toolbar.insertAction(self.colormapAction, self.expandCanvasAction)

        self.cropHistOutliersAction = self.group.addAction(
            CropHistogramOutliers(self, parent=self)
        )
        self.cropHistOutliersAction.setVisible(True)
        self.addAction(self.cropHistOutliersAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.cropHistOutliersAction
        )

        self.cs_transform = CoordinateTransformButton(parent=self, plot=self)
        self._toolbar.addWidget(self.cs_transform)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._beam_center = (0, 0, 0.1)
        self._pixelsize = (100e-6, 100e-6)

    def pixelToData_cartesian(self, x, y, axis="left", check=False):
        """
        Convert a position in pixels to a position in data coordinates.

        For the full docstring, please refer to the silx.gui.plot.PlotWidget.pixelToData
        method docstring.
        """
        assert axis in ("left", "right")

        if x is None:
            x = self.width() // 2
        if y is None:
            y = self.height() // 2

        if check:
            left, top, width, height = self.getPlotBoundsInPixels()
            if not (left <= x <= left + width and top <= y <= top + height):
                return None

        return self._backend.pixelToData(x, y, axis)

    def pixelToData_r_chi(self, x, y, axis="left", check=False):
        """
        Convert a position in pixels to a position in radial r, chi coordinates.

        For the full docstring, please refer to the silx.gui.plot.PlotWidget.pixelToData
        method docstring.
        """
        _px = self.pixelToData_cartesian(x, y, axis, check)
        if _px is None:
            return None
        _x_rel = _px[0] * self._pixelsize[0] - self._beam_center[1]
        _y_rel = _px[1] * self._pixelsize[1] - self._beam_center[0]
        _r = (
            (_x_rel / self._pixelsize[0]) ** 2 + (_y_rel / self._pixelsize[1]) ** 2
        ) ** 0.5
        _chi = self._get_chi_from_x_and_y(_x_rel, _y_rel)
        return (_r, _chi)

    def pixelToData_2theta_chi(self, x, y, axis="left", check=False):
        """
        Convert a position in pixels to a position in 2-theta, chi data coordinates.

        For the full docstring, please refer to the silx.gui.plot.PlotWidget.pixelToData
        method docstring.
        """
        _px = self.pixelToData_cartesian(x, y, axis, check)
        if _px is None:
            return None
        _x_rel = _px[0] * self._pixelsize[0] - self._beam_center[1]
        _y_rel = _px[1] * self._pixelsize[1] - self._beam_center[0]
        _r = (_x_rel**2 + _y_rel**2) ** 0.5
        _2theta = np.arctan(_r / self._beam_center[2]) * 180 / np.pi
        _chi = self._get_chi_from_x_and_y(_x_rel, _y_rel)
        return (_2theta, _chi)

    def pixelToData_q_chi(self, x, y, axis="left", check=False):
        """
        Convert a position in pixels to a position in data coordinates.

        For the full docstring, please refer to the silx.gui.plot.PlotWidget.pixelToData
        method docstring.
        """
        _lambda = EXP_SETUP.get_param_value("xray_wavelength") * 1e-10
        _2theta_chi = self.pixelToData_2theta_chi(x, y, axis, check)
        if _2theta_chi is None:
            return None
        _2theta, _chi = _2theta_chi
        _q = (4 * np.pi / _lambda) * np.sin(_2theta * np.pi / 180 / 2) * 1e-9
        return (_q, _chi)

    def _get_absolute_r(self, x_pix, y_pix):
        """
        Get the absolute polar r coordinate, based on the x and y pixel coordinates.

        Parameters
        ----------
        x_pix : float
            The x position in pixel.
        y_pix : float
            The y position in pixel.

        Returns
        -------
        float
        The absolute polar r variable [in m].
        """
        self._pixelsize = (
            EXP_SETUP.get_param_value("detector_pxsizex") * 1e-6,
            EXP_SETUP.get_param_value("detector_pxsizey") * 1e-6,
        )
        _x_rel = x_pix * self._pixelsize[0] - self._beam_center[1]
        _y_rel = y_pix * self._pixelsize[1] - self._beam_center[0]
        return (_x_rel**2 + _y_rel**2) ** 0.5

    def _get_chi_from_x_and_y(self, x, y):
        """
        Get the chi position in degree.

        Parameters
        ----------
        x : float
            The input value for the x coordinate.
        y : float
            The input value for the y coordinate.

        Returns
        -------
        float
            The chi value based on the input variables.
        """
        if x == 0 and y >= 0:
            _chi = 90
        elif x == 0 and y < 0:
            _chi = 270
        else:
            _chi = np.arctan(y / x) * 180 / np.pi
        if x < 0:
            _chi += 180
        return np.mod(_chi, 360)
