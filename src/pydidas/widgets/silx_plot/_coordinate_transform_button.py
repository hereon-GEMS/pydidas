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
from typing import TYPE_CHECKING, Any, Literal

from qtpy import QtCore, QtWidgets
from silx.gui.plot.PlotToolButtons import PlotToolButton

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core.constants import ASCII_TO_UNI
from pydidas.resources.pydidas_icons import create_pydidas_icon


if TYPE_CHECKING:
    from pydidas.widgets.silx_plot.pydidas_plot2d import PydidasPlot2D


THETA = ASCII_TO_UNI["theta"]
CHI = ASCII_TO_UNI["chi"]


class CoordinateTransformButton(PlotToolButton):
    """
    Tool button to change the coordinate system in 2d plots to use radial geometries.
    """

    CS_CONFIG = {
        ("cartesian", "icon"): create_pydidas_icon("silx_coordinates_xy_cartesian.png"),
        ("cartesian", "state"): "Cartesian x/y coordinates",
        ("cartesian", "action"): "Use cartesian x / y coordinates [px]",
        ("r_chi", "icon"): create_pydidas_icon("silx_coordinates_r_chi.png"),
        ("r_chi", "state"): f"Polar r / {CHI} coordinates",
        ("r_chi", "action"): f"Use polar r / {CHI} coordinates [mm, deg]",
        ("2theta_chi", "icon"): create_pydidas_icon("silx_coordinates_2theta_chi.png"),
        ("2theta_chi", "state"): f"Polar 2{THETA} / {CHI} coordinates",
        ("2theta_chi", "action"): f"Use polar 2{THETA} / {CHI} coordinates [deg, deg]",
        ("q_chi", "icon"): create_pydidas_icon("silx_coordinates_q_chi.png"),
        ("q_chi", "state"): f"Polar q / {CHI} coordinates",
        ("q_chi", "action"): f"Use polar q / {CHI} coordinates [nm^-1, deg]",
    }
    sig_new_coordinate_system = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        plot: "PydidasPlot2D | None" = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the CoordinateTransformButton.

        Parameters
        ----------
        parent : QtWidgets.QWidget or None, optional
            The parent widget. The default is None.
        plot : PydidasPlot2D or None, optional
            The plot instance. The default is None.
        **kwargs : Any
            Keyword arguments. Supported keywords are:

            diffraction_exp : DiffractionExperimentContext, optional
                The diffraction experiment context.
        """
        PlotToolButton.__init__(self, parent=parent, plot=plot)
        self.__diff_exp = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        self.__current_cs = ""
        self._data_shape = (-1, -1)
        self._data_linear = True
        self.__define_actions_and_create_menu()
        self.__diff_exp.sig_params_changed.connect(self._check_and_enable_button)  # type: ignore[attr-defined]

    def __define_actions_and_create_menu(self) -> None:
        """Define the required actions and create the button menu."""
        _menu = QtWidgets.QMenu(self)
        for _key in ["cartesian", "r_chi", "2theta_chi", "q_chi"]:
            self._create_action(_menu, _key)
        self.setMenu(_menu)
        self.set_coordinates("cartesian")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    def _create_action(self, menu: QtWidgets.QMenu, coordinate_system: str) -> None:
        """
        Create the action for the given coordinate system.

        Parameters
        ----------
        menu : QtWidgets.QMenu
            The menu to add the action to.
        coordinate_system : str
            The name of the coordinate system.
        """
        _icon = self.CS_CONFIG[coordinate_system, "icon"]
        _text = self.CS_CONFIG[coordinate_system, "action"]
        _action = QtWidgets.QAction(_icon, _text, self)
        _action.triggered.connect(partial(self.set_coordinates, coordinate_system))  # type: ignore[attr-defined]
        _action.setIconVisibleInMenu(True)
        menu.addAction(_action)

    @QtCore.Slot()
    def set_coordinates(
        self, cs_name: Literal["cartesian", "r_chi", "2theta_chi", "q_chi"]
    ) -> None:
        """
        Set the coordinate system associated with the given name.

        Parameters
        ----------
        cs_name : Literal["cartesian", "r_chi", "2theta_chi", "q_chi"]
            The descriptive name of the coordinate system.
        """
        if cs_name != self.__current_cs:
            self.setIcon(self.CS_CONFIG[cs_name, "icon"])
            self.setToolTip(self.CS_CONFIG[cs_name, "state"])
            self.sig_new_coordinate_system.emit(cs_name)  # type: ignore[attr-defined]
            self.__current_cs = cs_name

    @QtCore.Slot()
    def _check_and_enable_button(self) -> None:
        """Check and enable the button if the data shape matches the detector."""
        self.setEnabled(
            self.__diff_exp.detector_is_valid
            and self._data_linear
            and self._data_shape == self.__diff_exp.det_shape
        )
        if not self.isEnabled():
            self.set_coordinates("cartesian")

    @QtCore.Slot(int, int)
    def set_raw_data_size(self, height: int, width: int) -> None:
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
        self._check_and_enable_button()

    @QtCore.Slot(bool)
    def set_data_linearity(self, linear: bool) -> None:
        """
        Slot to receive the new data linearity.

        Parameters
        ----------
        linear : bool
            The new data linearity.
        """
        self._data_linear = linear
        self._check_and_enable_button()
