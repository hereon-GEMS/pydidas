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
Module with the PydidasPositionInfo class used to display image data coordinates in
different coordinate systems.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPositionInfo"]

import numpy as np
from qtpy import QtCore
from silx.gui.plot.tools import PositionInfo

from ...core.utils import pyfai_rot_matrix, get_chi_from_x_and_y
from ...experiment import SetupExperiment


EXP_SETUP = SetupExperiment()


AX_LABELS = {
    "cartesian": ("x", "px", "y", "px"),
    "r_chi": ("r", "px", "&#x3C7;", "deg"),
    "q_chi": ("q", "nm^-1", "&#x3C7;", "deg"),
    "2theta_chi": ("2&#x3B8;", "deg", "&#x3C7;", "deg"),
}


class PydidasPositionInfo(PositionInfo):
    """
    A customized silx.gui.plot.PositionInfo which allows to use coordinate
    transformations to display polar coordinates.
    """

    def __init__(self, parent=None, plot=None, converters=None):
        PositionInfo.__init__(self, parent, plot, converters)
        self._x_widget = self.layout().itemAt(0).widget()
        self._y_widget = self.layout().itemAt(2).widget()
        self._cs_name = "cartesian"
        self._cs_x_unit = "px"
        self._cs_y_unit = "px"
        self._beam_center = (0, 0, 0.1)
        self._pixelsize = (100e-6, 100e-6)
        self.update_coordinate_labels()

    @QtCore.Slot(str)
    def new_coordinate_system(self, cs_name):
        """
        Receive the signal that a new coordinate system has been selected and
        update the interal reference.

        Parameters
        ----------
        cs_name : str
            The name of the new coordinate system.
        """
        self._cs_name = cs_name
        self._cs_x_unit = AX_LABELS[cs_name][1]
        self._cs_y_unit = AX_LABELS[cs_name][3]
        self.update_coordinate_labels()

    def update_coordinate_labels(self):
        """
        Update the position info widget coordinate labels based on the coordinate
        system.

        Parameters
        ----------
        xlabel : str
            The label for the first (generic "x") coordinate.
        ylabel : str
            The label for the second (generic "y") coordinate.
        """
        _x_text = AX_LABELS[self._cs_name][0] + f" [{self._cs_x_unit}]"
        _y_text = AX_LABELS[self._cs_name][2] + f" [{self._cs_y_unit}]"
        self._x_widget.setText(f"<b>{_x_text}:</b>")
        self._y_widget.setText(f"<b>{_y_text}:</b>")

    def update_coordinate_units(self, x_unit, y_unit):
        """
        Update the coordinate units in the PositionInfo widget.

        Parameters
        ----------
        x_unit : str
            The unit for the x-axis data.
        y_unit : str
            The unit for the y-axis data.
        """
        self._cs_x_unit = x_unit
        self._cs_y_unit = y_unit
        self.update_coordinate_labels()

    @QtCore.Slot()
    def update_exp_setup_params(self):
        """
        Get the beam center in image coordinates.

        Returns
        -------
        tuple
            The beam center in a tuple (y, x)
        """
        _theta = [EXP_SETUP.get_param_value(f"detector_rot{dim}") for dim in [1, 2, 3]]
        _y0 = EXP_SETUP.get_param_value("detector_poni1")
        _x0 = EXP_SETUP.get_param_value("detector_poni2")
        _z0 = EXP_SETUP.get_param_value("detector_dist")
        _rot = pyfai_rot_matrix(*_theta)
        # the center is found by *subtracting* the rotation of the 0-position with
        # respect to the poni (because pyFAI geometry moves the detector)
        _beam_center = np.array([_y0, _x0, 0]) - np.dot(_rot, np.array([0, 0, _z0]))
        _beam_center *= abs(_z0 / _beam_center[2])
        self._beam_center = (_beam_center[0], _beam_center[1], _z0)
        self._pixelsize = (
            EXP_SETUP.get_param_value("detector_pxsizex") * 1e-6,
            EXP_SETUP.get_param_value("detector_pxsizey") * 1e-6,
        )

    def _plotEvent(self, event):
        """Handle events from the Plot.

        :param dict event: Plot event
        """
        if event["event"] == "mouseMoved":
            _x, _y = event["x"], event["y"]
            _method = getattr(self, f"pixel_to_cs_{self._cs_name}")
            _coord1, _coord2 = _method(_x, _y)
            _x_pix, _y_pix = event["xpixel"], event["ypixel"]
            self._updateStatusBar(_coord1, _coord2, _x_pix, _y_pix)

    def pixel_to_cs_cartesian(self, x_pix, y_pix):
        """
        Convert a position in pixels to a position in cartesian data coordinates.

        Parameters
        ----------
        x_pix : int
            The pixel x coordinate.
        y_pix : int
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the cartesian x,y coordinates.
        """
        return (x_pix, y_pix)

    def pixel_to_cs_r_chi(self, x_pix, y_pix):
        """
        Convert a position in pixels to a position in radial r, chi coordinates.

        Parameters
        ----------
        x_pix : int
            The pixel x coordinate.
        y_pix : int
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar r, chi coordinates.
        """
        _x_rel = x_pix * self._pixelsize[0] - self._beam_center[1]
        _y_rel = y_pix * self._pixelsize[1] - self._beam_center[0]
        _r = (
            (_x_rel / self._pixelsize[0]) ** 2 + (_y_rel / self._pixelsize[1]) ** 2
        ) ** 0.5
        _chi = get_chi_from_x_and_y(_x_rel, _y_rel)
        return (_r, _chi)

    def pixel_to_cs_2theta_chi(self, x_pix, y_pix):
        """
        Convert a position in pixels to a position in 2-theta, chi data coordinates.

        Parameters
        ----------
        x_pix : int
            The pixel x coordinate.
        y_pix : int
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar 2-theta, chi coordinates.
        """
        _x_rel = x_pix * self._pixelsize[0] - self._beam_center[1]
        _y_rel = y_pix * self._pixelsize[1] - self._beam_center[0]
        _r = (_x_rel**2 + _y_rel**2) ** 0.5
        _2theta = np.arctan(_r / self._beam_center[2]) * 180 / np.pi
        _chi = get_chi_from_x_and_y(_x_rel, _y_rel)
        return (_2theta, _chi)

    def pixel_to_cs_q_chi(self, x_pix, y_pix):
        """
        Convert a position in pixels to a position in data coordinates.

        Parameters
        ----------
        x_pix : int
            The pixel x coordinate.
        y_pix : int
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar q, chi coordinates.
        """
        _lambda = EXP_SETUP.get_param_value("xray_wavelength") * 1e-10
        _2theta, _chi = self.pixel_to_cs_2theta_chi(x_pix, y_pix)
        _q = (4 * np.pi / _lambda) * np.sin(_2theta * np.pi / 180 / 2) * 1e-9
        return (_q, _chi)
