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

from qtpy import QtCore, QtWidgets
from silx.gui.plot.PlotToolButtons import PlotToolButton

from .utilities import get_pydidas_qt_icon


class CoordinateTransformButton(PlotToolButton):
    """
    Tool button to change the coordinate system in 2d plots to use radial geometries.
    """

    STATE = None

    def __init__(self, parent=None, plot=None):
        if self.STATE is None:
            self.STATE = {}

            self.STATE["cartesian", "icon"] = get_pydidas_qt_icon(
                "silx_coordinates_xy_cartesian.png"
            )
            self.STATE["cartesian", "state"] = "Cartesian x/y coordinates"
            self.STATE["cartesian", "action"] = "Use cartesian x / y coordinates [px]"

            self.STATE["r_theta", "icon"] = get_pydidas_qt_icon(
                "silx_coordinates_r_theta.png"
            )
            self.STATE["r_theta", "state"] = "Polar r/theta coordinates"
            self.STATE[
                "r_theta", "action"
            ] = "Use polar r / theta coordinates [px, deg]"

            self.STATE["q_theta", "icon"] = get_pydidas_qt_icon(
                "silx_coordinates_q_theta.png"
            )
            self.STATE["q_theta", "state"] = "Polar q/theta coordinates"
            self.STATE[
                "q_theta", "action"
            ] = "Use polar q / theta coordinates [nm^-1, deg]"

        super(CoordinateTransformButton, self).__init__(parent=parent, plot=plot)

        cartesian_action = self._create_action("cartesian")
        cartesian_action.triggered.connect(self.set_coordinates_xy)
        cartesian_action.setIconVisibleInMenu(True)

        r_theta_action = self._create_action("r_theta")
        r_theta_action.triggered.connect(self.set_coordinates_r_theta)
        r_theta_action.setIconVisibleInMenu(True)

        q_theta_action = self._create_action("q_theta")
        q_theta_action.triggered.connect(self.set_coordinates_q_theta)
        q_theta_action.setIconVisibleInMenu(True)

        menu = QtWidgets.QMenu(self)
        menu.addAction(cartesian_action)
        menu.addAction(r_theta_action)
        menu.addAction(q_theta_action)

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

    @QtCore.Slot()
    def set_coordinates_r_theta(self):
        self._update_icon("r_theta")

    @QtCore.Slot()
    def set_coordinates_q_theta(self):
        self._update_icon("q_theta")

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
