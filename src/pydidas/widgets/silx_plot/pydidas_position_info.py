# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PydidasPositionInfo class used to display image data coordinates in
different coordinate systems.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPositionInfo"]


from typing import Literal

import numpy as np
from qtpy import QtCore
from silx.gui.plot.tools import PositionInfo

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import UserConfigError
from pydidas.core.utils import get_chi_from_x_and_y


AX_LABELS = {
    "cartesian": ("x", "px", "y", "px"),
    "r_chi": ("r", "mm", "&#x3C7;", "deg"),
    "q_chi": ("q", "nm^-1", "&#x3C7;", "deg"),
    "2theta_chi": ("2&#x3B8;", "deg", "&#x3C7;", "deg"),
}


class PydidasPositionInfo(PositionInfo):
    """
    A customized silx.gui.plot.PositionInfo which allows to use coordinate
    transformations to display polar coordinates.

    Parameters
    ----------
    **kwargs : dict
        Supported keyword arguments are:

            converters : Union[list[tuple[str, Callable]], None], optional
                The converters for changing the image coordinates. Takes a
                list of 2-tuples with name to display and conversion function from
                (x, y) coordinates. The default is None.
            parent : Union[QWidget, None], optional
                The parent widget. The default is None.
            plot : Union[QWidget, None], optional
                The associated plot instance. The default is None
    """

    def __init__(self, **kwargs: dict):
        PositionInfo.__init__(
            self,
            plot=kwargs.get("plot", None),
            converters=kwargs.get("converters", None),
            parent=kwargs.get("parent", None),
        )
        self._EXP = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        self._EXP.sig_params_changed.connect(self.update_exp_setup_params)
        self._x_widget = self.layout().itemAt(0).widget()
        self._y_widget = self.layout().itemAt(2).widget()
        self._cs_name = "cartesian"
        self._cs_x_unit = "px"
        self._cs_y_unit = "px"
        self._beam_center = (0, 0, 0.1)
        self._pixelsize = (100e-6, 100e-6)
        self.update_coordinate_labels()
        self.update_exp_setup_params()

    @QtCore.Slot(str)
    def new_coordinate_system(
        self, cs_name: Literal["cartesian", "r_chi", "q_chi", "2theta_chi"]
    ):
        """
        Receive the signal that a new coordinate system has been selected and
        update the internal reference.

        Parameters
        ----------
        cs_name : Literal["cartesian", "r_chi", "q_chi", "2theta_chi"]
            The name of the new coordinate system.
        """
        self._cs_name = cs_name
        self._cs_x_unit = AX_LABELS[cs_name][1]
        self._cs_y_unit = AX_LABELS[cs_name][3]
        self.update_coordinate_labels()

    def update_coordinate_labels(self):
        """
        Update the position info widget coordinate labels based on the stored units.
        """
        _x_text = AX_LABELS[self._cs_name][0] + f" [{self._cs_x_unit}]"
        _y_text = AX_LABELS[self._cs_name][2] + f" [{self._cs_y_unit}]"
        self._x_widget.setText(f"<b>{_x_text}:</b>")
        self._y_widget.setText(f"<b>{_y_text}:</b>")

    def update_coordinate_units(self, x_unit: str, y_unit: str):
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
        Update beamcenter and detector distance from the DiffractionExperiment.
        """
        try:
            _f2dgeo = self._EXP.as_fit2d_geometry_values()
        except UserConfigError:
            self._plotRef().enable_cs_transform(False)
            return
        self._pixelsize = (
            self._EXP.get_param_value("detector_pxsizex") * 1e-6,
            self._EXP.get_param_value("detector_pxsizey") * 1e-6,
        )
        self._beam_center = (
            _f2dgeo["center_y"],
            _f2dgeo["center_x"],
            _f2dgeo["det_dist"] * 1e-3,
        )

    def _plotEvent(self, event: dict):
        """
        Handle events from the Plot.

        Parameters
        ----------
        event : dict
            The silx plot event dictionary.
        """
        if event["event"] == "mouseMoved":
            _x, _y = event["x"], event["y"]
            _method = getattr(self, f"pixel_to_cs_{self._cs_name}")
            _coord1, _coord2 = _method(_x, _y)
            _x_pix, _y_pix = event["xpixel"], event["ypixel"]
            self._updateStatusBar(_coord1, _coord2, _x_pix, _y_pix)

    def pixel_to_cs_cartesian(self, x_pix: float, y_pix: float) -> tuple[float, float]:
        """
        Convert a position in pixels to a position in cartesian data coordinates.

        Parameters
        ----------
        x_pix : float
            The pixel x coordinate.
        y_pix : float
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the cartesian x,y coordinates.
        """
        return (x_pix, y_pix)

    def pixel_to_cs_r_chi(self, x_pix: float, y_pix: float) -> tuple[float, float]:
        """
        Convert a position in pixels to a position in radial r, chi coordinates.

        Parameters
        ----------
        x_pix : float
            The pixel x coordinate.
        y_pix : float
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar r, chi coordinates.
        """
        _x_rel = (x_pix - self._beam_center[1]) * self._pixelsize[0]
        _y_rel = (y_pix - self._beam_center[0]) * self._pixelsize[1]
        _r = ((_x_rel) ** 2 + (_y_rel) ** 2) ** 0.5 * 1e3
        _chi = get_chi_from_x_and_y(_x_rel, _y_rel) * 180 / np.pi
        return (_r, _chi)

    def pixel_to_cs_2theta_chi(self, x_pix: float, y_pix: float) -> tuple[float, float]:
        """
        Convert a position in pixels to a position in 2-theta, chi data coordinates.

        Parameters
        ----------
        x_pix : float
            The pixel x coordinate.
        y_pix : float
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar 2-theta, chi coordinates.
        """
        _x_rel = (x_pix - self._beam_center[1]) * self._pixelsize[0]
        _y_rel = (y_pix - self._beam_center[0]) * self._pixelsize[1]
        _r = (_x_rel**2 + _y_rel**2) ** 0.5
        _2theta = np.arctan(_r / self._beam_center[2]) * 180 / np.pi
        _chi = get_chi_from_x_and_y(_x_rel, _y_rel) * 180 / np.pi
        return (_2theta, _chi)

    def pixel_to_cs_q_chi(self, x_pix: float, y_pix: float) -> tuple[float, float]:
        """
        Convert a position in pixels to a position in data coordinates.

        Parameters
        ----------
        x_pix : float
            The pixel x coordinate.
        y_pix : float
            The pixel y coordinate.

        Returns
        -------
        tuple
            The tuple with the polar q, chi coordinates.
        """
        _lambda = self._EXP.get_param_value("xray_wavelength") * 1e-10
        _2theta, _chi = self.pixel_to_cs_2theta_chi(x_pix, y_pix)
        _q = (4 * np.pi / _lambda) * np.sin(_2theta * np.pi / 180 / 2) * 1e-9
        return (_q, _chi)
