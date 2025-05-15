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
        self.__current_cs = ""
        self._data_shape = (-1, -1)
        self._data_linear = True
        self.__define_actions_and_create_menu()
        DIFFRACTION_EXP.sig_params_changed.connect(self._check_enabled)

    def __set_state(self):
        """
        Set the state variables for all required actions.
        """
        self.STATE = {
            ("cartesian", "icon"): icons.get_pydidas_qt_icon(
                "silx_coordinates_xy_cartesian.png"
            ),
            ("cartesian", "state"): "Cartesian x/y coordinates",
            ("cartesian", "action"): "Use cartesian x / y coordinates [px]",
            ("r_chi", "icon"): icons.get_pydidas_qt_icon("silx_coordinates_r_chi.png"),
            ("r_chi", "state"): f"Polar r / {CHI} coordinates",
            ("r_chi", "action"): f"Use polar r / {CHI} coordinates [mm, deg]",
            ("2theta_chi", "icon"): icons.get_pydidas_qt_icon(
                "silx_coordinates_2theta_chi.png"
            ),
            ("2theta_chi", "state"): f"Polar 2{THETA} / {CHI} coordinates",
            ("2theta_chi", "action"): (
                f"Use polar 2{THETA} / {CHI} coordinates [deg, deg]"
            ),
            ("q_chi", "icon"): icons.get_pydidas_qt_icon("silx_coordinates_q_chi.png"),
            ("q_chi", "state"): f"Polar q / {CHI} coordinates",
            ("q_chi", "action"): f"Use polar q / {CHI} coordinates [nm^-1, deg]",
        }

    def __define_actions_and_create_menu(self):
        """
        Define the required actions and create the button menu.
        """
        menu = QtWidgets.QMenu(self)
        for _key in ["cartesian", "r_chi", "2theta_chi", "q_chi"]:
            _action = self._create_action(_key)
            menu.addAction(_action)
        self.setMenu(menu)
        self.set_coordinates("cartesian")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    def _create_action(self, coordinate_system: str) -> QtWidgets.QAction:
        """
        Create the action for the given coordinate system.

        Parameters
        ----------
        coordinate_system : str
            The name of the coordinate system.

        Returns
        -------
        QtWidgets.QAction
            The action for the coordinate system.
        """
        _icon = self.STATE[coordinate_system, "icon"]
        _text = self.STATE[coordinate_system, "action"]
        _action = QtWidgets.QAction(_icon, _text, self)
        _action.triggered.connect(partial(self.set_coordinates, coordinate_system))
        _action.setIconVisibleInMenu(True)
        return _action

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
    def _check_enabled(self):
        """Check the data shape against the detector geometry"""
        if (
            self.detector_valid
            and self._data_linear
            and self._data_shape
            == (
                DIFFRACTION_EXP.get_param_value("detector_npixy"),
                DIFFRACTION_EXP.get_param_value("detector_npixx"),
            )
        ):
            self.setEnabled(True)
            return
        self.set_coordinates("cartesian")
        self.setEnabled(False)

    @property
    def detector_valid(self) -> bool:
        """
        Check that the detector is valid.

        Returns
        -------
        bool
            Flag whether the detector has been set up correctly.
        """
        return (
            DIFFRACTION_EXP.get_param_value("detector_npixx") >= 1
            and DIFFRACTION_EXP.get_param_value("detector_npixy") >= 1
            and DIFFRACTION_EXP.get_param_value("detector_pxsizex") > 0
            and DIFFRACTION_EXP.get_param_value("detector_pxsizey") > 0
        )

    @QtCore.Slot(int, int)
    def set_raw_data_size(self, height: int, width: int):
        """
        Slot to receive the new raw data dimensions.

        Parameters
        ----------
        height : int
            The height of the new raw data.
        width : int
            The width of the new raw data.
        """
        self._data_shape = (height, width)
        self._check_enabled()

    @QtCore.Slot(bool)
    def set_data_linearity(self, linear: bool):
        """
        Slot to receive the new data linearity.

        Parameters
        ----------
        linear : bool
            The new data linearity.
        """
        self._data_linear = linear
        self._check_enabled()
