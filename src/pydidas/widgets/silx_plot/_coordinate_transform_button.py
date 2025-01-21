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
Module with the CoordinateTransformButton to change the image coordinate system.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CoordinateTransformButton"]


from functools import partial
from typing import Literal

from qtpy import QtCore, QtWidgets
from silx.gui.plot.PlotToolButtons import PlotToolButton

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import UserConfigError
from pydidas.core.constants import ASCII_TO_UNI
from pydidas.resources import icons


THETA = ASCII_TO_UNI["theta"]
CHI = ASCII_TO_UNI["chi"]
DIFFRACTION_EXP = DiffractionExperimentContext()


class CoordinateTransformButton(PlotToolButton):
    """
    Tool button to change the coordinate system in 2d plots to use radial geometries.
    """

    STATE = None
    sig_new_coordinate_system = QtCore.Signal(str)

    def __init__(self, parent=None, plot=None):
        if self.STATE is None:
            self.__set_state()
        PlotToolButton.__init__(self, parent=parent, plot=plot)
        self.__current_cs = "None"
        self.__define_actions_and_create_menu()

    def __set_state(self):
        """
        Set the state variables for all required actions.
        """
        self.STATE = {}

        self.STATE["cartesian", "icon"] = icons.get_pydidas_qt_icon(
            "silx_coordinates_xy_cartesian.png"
        )
        self.STATE["cartesian", "state"] = "Cartesian x/y coordinates"
        self.STATE["cartesian", "action"] = "Use cartesian x / y coordinates [px]"

        self.STATE["r_chi", "icon"] = icons.get_pydidas_qt_icon(
            "silx_coordinates_r_chi.png"
        )
        self.STATE["r_chi", "state"] = f"Polar r / {CHI} coordinates"
        self.STATE["r_chi", "action"] = f"Use polar r / {CHI} coordinates [mm, deg]"

        self.STATE["2theta_chi", "icon"] = icons.get_pydidas_qt_icon(
            "silx_coordinates_2theta_chi.png"
        )
        self.STATE["2theta_chi", "state"] = f"Polar 2{THETA} / {CHI} coordinates"
        self.STATE["2theta_chi", "action"] = (
            f"Use polar 2{THETA} / {CHI} coordinates [deg, deg]"
        )

        self.STATE["q_chi", "icon"] = icons.get_pydidas_qt_icon(
            "silx_coordinates_q_chi.png"
        )
        self.STATE["q_chi", "state"] = f"Polar q / {CHI} coordinates"
        self.STATE["q_chi", "action"] = f"Use polar q / {CHI} coordinates [nm^-1, deg]"

    def __define_actions_and_create_menu(self):
        """
        Define the required actions and create the button menu.
        """
        cartesian_action = self._create_action("cartesian")
        cartesian_action.triggered.connect(partial(self.set_coordinates, "cartesian"))
        cartesian_action.setIconVisibleInMenu(True)

        r_chi_action = self._create_action("r_chi")
        r_chi_action.triggered.connect(partial(self.set_coordinates, "r_chi"))
        r_chi_action.setIconVisibleInMenu(True)

        theta_chi_action = self._create_action("2theta_chi")
        theta_chi_action.triggered.connect(partial(self.set_coordinates, "2theta_chi"))
        theta_chi_action.setIconVisibleInMenu(True)

        q_chi_action = self._create_action("q_chi")
        q_chi_action.triggered.connect(partial(self.set_coordinates, "q_chi"))
        q_chi_action.setIconVisibleInMenu(True)

        menu = QtWidgets.QMenu(self)
        menu.addAction(cartesian_action)
        menu.addAction(r_chi_action)
        menu.addAction(theta_chi_action)
        menu.addAction(q_chi_action)

        self.setMenu(menu)
        self.set_coordinates("cartesian")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    def _create_action(self, coordinate_system: str) -> QtWidgets.QAction:
        _icon = self.STATE[coordinate_system, "icon"]
        _text = self.STATE[coordinate_system, "action"]
        return QtWidgets.QAction(_icon, _text, self)

    @QtCore.Slot()
    def set_coordinates(
        self, cs_name: Literal["cartesian", "r_chi", "2theta_chi", "q_chi"]
    ):
        """
        Set the coordinate system associated with the given name.

        Parameters
        ----------
        cs_name : Literal["cartesian", "r_chi", "2theta_chi", "q_chi"]
            The descriptive name of the coordinate system.
        """
        if cs_name != self.__current_cs:
            self.setIcon(self.STATE[cs_name, "icon"])
            self.setToolTip(self.STATE[cs_name, "state"])
            self.sig_new_coordinate_system.emit(cs_name)
            self.__current_cs = cs_name

    @QtCore.Slot()
    def check_detector_is_set(self, silent: bool = False):
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
            DIFFRACTION_EXP.get_param_value("detector_npixx") < 1
            or DIFFRACTION_EXP.get_param_value("detector_npixy") < 1
            or DIFFRACTION_EXP.get_param_value("detector_pxsizex") <= 0
            or DIFFRACTION_EXP.get_param_value("detector_pxsizey") <= 0
        ):
            self.set_coordinates("cartesian")
            if not silent:
                raise UserConfigError(
                    "The detector is not defined. Cannot convert pixel positions to "
                    "angular values. Please set the detector in the 'Experimental "
                    "Setup' tab and try again."
                )
