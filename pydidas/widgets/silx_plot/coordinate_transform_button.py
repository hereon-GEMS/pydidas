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
Module with the CoordinateTransformButton to change the image coordinate system.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["CoordinateTransformButton"]

import copy

import numpy as np
from numpy import sin, cos
from qtpy import QtCore, QtWidgets
from silx.gui.plot.PlotToolButtons import PlotToolButton

from ...core import UserConfigError
from ...core.constants import GREEK_ASCII_TO_UNI
from ...core.utils import pyfai_rot_matrix
from ...experiment import SetupExperiment, SetupExperimentIoMeta
from .utilities import get_pydidas_qt_icon

THETA = GREEK_ASCII_TO_UNI["theta"]
CHI = GREEK_ASCII_TO_UNI["chi"]
EXP_SETUP = SetupExperiment()


class CoordinateTransformButton(PlotToolButton):
    """
    Tool button to change the coordinate system in 2d plots to use radial geometries.
    """

    STATE = None

    def __init__(self, parent=None, plot=None):
        if self.STATE is None:
            self.__set_state()
        super(CoordinateTransformButton, self).__init__(parent=parent, plot=plot)
        self.__plot = plot
        self.__define_actions_and_create_menu()
        self.set_beam_center_from_exp_setup()
        self._pos_widget = plot.getPositionInfoWidget()

    def __set_state(self):
        """
        Set the state variables for all required actions.
        """
        self.STATE = {}

        self.STATE["cartesian", "icon"] = get_pydidas_qt_icon(
            "silx_coordinates_xy_cartesian.png"
        )
        self.STATE["cartesian", "state"] = "Cartesian x/y coordinates"
        self.STATE["cartesian", "action"] = "Use cartesian x / y coordinates [px]"

        self.STATE["r_chi", "icon"] = get_pydidas_qt_icon("silx_coordinates_r_chi.png")
        self.STATE["r_chi", "state"] = f"Polar r / {CHI} coordinates"
        self.STATE["r_chi", "action"] = f"Use polar r / {CHI} coordinates [px, deg]"

        self.STATE["q_chi", "icon"] = get_pydidas_qt_icon("silx_coordinates_q_chi.png")
        self.STATE["q_chi", "state"] = f"Polar q / {CHI} coordinates"
        self.STATE["q_chi", "action"] = f"Use polar q / {CHI} coordinates [nm^-1, deg]"

        self.STATE["2theta_chi", "icon"] = get_pydidas_qt_icon(
            "silx_coordinates_2theta_chi.png"
        )
        self.STATE["2theta_chi", "state"] = f"Polar 2{THETA} / {CHI} coordinates"
        self.STATE[
            "2theta_chi", "action"
        ] = f"Use polar 2{THETA} / {CHI} coordinates [deg, deg]"

    def __define_actions_and_create_menu(self):
        """
        Define the required actions and create the button menu.
        """
        cartesian_action = self._create_action("cartesian")
        cartesian_action.triggered.connect(self.set_coordinates_xy)
        cartesian_action.setIconVisibleInMenu(True)

        r_chi_action = self._create_action("r_chi")
        r_chi_action.triggered.connect(self.set_coordinates_r_chi)
        r_chi_action.setIconVisibleInMenu(True)

        q_chi_action = self._create_action("q_chi")
        q_chi_action.triggered.connect(self.set_coordinates_q_chi)
        q_chi_action.setIconVisibleInMenu(True)

        theta_chi_action = self._create_action("2theta_chi")
        theta_chi_action.triggered.connect(self.set_coordinates_2theta_chi)
        theta_chi_action.setIconVisibleInMenu(True)

        menu = QtWidgets.QMenu(self)
        menu.addAction(cartesian_action)
        menu.addAction(r_chi_action)
        menu.addAction(theta_chi_action)
        menu.addAction(q_chi_action)

        self.setMenu(menu)
        self._update_icon("cartesian")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    def _create_action(self, coordinate_system):
        _icon = self.STATE[coordinate_system, "icon"]
        _text = self.STATE[coordinate_system, "action"]
        return QtWidgets.QAction(_icon, _text, self)

    @QtCore.Slot()
    def set_coordinates_xy(self):
        self._update_icon("cartesian")
        self._update_pos_widget_labels("x [px]", "y [px]")
        self.__plot.pixelToData = self.__plot.pixelToData_cartesian

    @QtCore.Slot()
    def set_coordinates_r_chi(self):
        self._update_icon("r_chi")
        self._update_pos_widget_labels("r [px]", "&#x3C7; [deg]")
        self.__plot.pixelToData = self.__plot.pixelToData_r_chi

    @QtCore.Slot()
    def set_coordinates_q_chi(self):
        self.check_detector_is_set()
        self._update_icon("q_chi")
        self._update_pos_widget_labels("q [nm^-1]", "&#x3C7; [deg]")
        self.__plot.pixelToData = self.__plot.pixelToData_q_chi

    @QtCore.Slot()
    def set_coordinates_2theta_chi(self):
        self.check_detector_is_set()
        self._update_icon("2theta_chi")
        self._update_pos_widget_labels("2&#x3B8; [deg]", "&#x3C7; [deg]")
        self.__plot.pixelToData = self.__plot.pixelToData_2theta_chi

    def _update_icon(self, coordinate_system):
        """
        Update the Menu's icon and tooltip, based on the selected coordinate system.

        Parameters
        ----------
        coordinate_system : str
            The coordinate system descriptor.
        """
        self.setIcon(self.STATE[coordinate_system, "icon"])
        self.setToolTip(self.STATE[coordinate_system, "state"])

    def _update_pos_widget_labels(self, xlabel, ylabel):
        """
        Update the position info widget labels based on the coordinate system.

        Parameters
        ----------
        xlabel : str
            The label for the first (generic "x") coordinate.
        ylabel : str
            The label for the second (generic "y") coordinate.
        """
        _x_widget = self._pos_widget.layout().itemAt(0).widget()
        _y_widget = self._pos_widget.layout().itemAt(2).widget()
        _x_widget.setText(f"<b>{xlabel}:</b>")
        _y_widget.setText(f"<b>{ylabel}:</b>")

    @QtCore.Slot()
    def check_detector_is_set(self, silent=False):
        """
        Check that the detector is set to convert radii to q and 2 theta values.

        Parameters
        ----------
        silent : bool, optional
            Flag to suppress the exception and silently reset the coordinates to
            cartesian values.

        Returns
        -------
        bool
            Flag whether the detecor has been set up correctly.
        """
        if (
            EXP_SETUP.get_param_value("detector_npixx") < 1
            or EXP_SETUP.get_param_value("detector_npixy") < 1
            or EXP_SETUP.get_param_value("detector_pxsizex") <= 0
            or EXP_SETUP.get_param_value("detector_pxsizey") <= 0
        ):
            self.set_coordinates_xy()
            if not silent:
                raise UserConfigError(
                    "The detector is not defined. Cannot convert pixel positions to "
                    "angular values. Please set the detector in the 'Experimental "
                    "Setup' tab and try again."
                )

    @QtCore.Slot()
    def set_beam_center_from_exp_setup(self):
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
        self.__plot._beam_center = (_beam_center[0], _beam_center[1], _z0)
        self.__plot._pixelsize = (
            EXP_SETUP.get_param_value("detector_pxsizex") * 1e-6,
            EXP_SETUP.get_param_value("detector_pxsizey") * 1e-6,
        )
