# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the SpecialPlotTypesButton to change the plot type of data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SpecialPlotTypesButton"]


from functools import partial
from typing import TYPE_CHECKING, Callable, Literal

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot.PlotToolButtons import PlotToolButton

from pydidas.resources import icons


if TYPE_CHECKING:
    from pydidas.widgets.silx_plot.pydidas_plot1d import PydidasPlot1D


class SpecialPlotTypesButton(PlotToolButton):
    """
    Tool button to change the plot type of the original data.

    This allows to display the data in different representations, e.g.
    a Kratky plot for SAXS data.
    """

    PLOT_TYPE = {
        ("generic", "icon"): icons.create_pydidas_icon("silx_plot_type_generic.png"),
        ("generic", "state"): "Generic f(x) = y",
        ("generic", "action"): "Plot generic data",
        ("kratky", "icon"): icons.create_pydidas_icon("silx_plot_type_kratky.png"),
        ("kratky", "state"): "Kratky plot f(x) = y * x^2",
        ("kratky", "action"): "Use Kratky plot f(x) = y * x^2",
    }
    sig_new_plot_type = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        plot: "PydidasPlot1D | None" = None,
    ) -> None:
        """
        Initialize the SpecialPlotTypesButton.

        Parameters
        ----------
        parent : QtWidgets.QWidget or None, optional
            The parent widget. The default is None.
        plot : PydidasPlot1D or None, optional
            The plot instance. The default is None.
        """
        PlotToolButton.__init__(self, parent=parent, plot=plot)
        self.__define_actions_and_create_menu()
        self._current_yfunc = self.func_generic
        self._current_ylabel = self.label_generic

    def __define_actions_and_create_menu(self) -> None:
        """Define the required actions and create the button menu."""
        menu = QtWidgets.QMenu(self)

        for _key in ["generic", "kratky"]:
            _action = QtWidgets.QAction(
                self.PLOT_TYPE[_key, "icon"], self.PLOT_TYPE[_key, "action"], self
            )
            _action.triggered.connect(partial(self.set_plot_type, _key))  # type: ignore[attr-defined]
            _action.setIconVisibleInMenu(True)
            menu.addAction(_action)

        self.setMenu(menu)
        self.set_plot_type("generic")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    @QtCore.Slot()
    def set_plot_type(self, plot_type: Literal["generic", "kratky"]) -> None:
        """
        Set the coordinate system associated with the given name.

        Parameters
        ----------
        plot_type: Literal["generic", "kratky"]
            The descriptive name of the plot type.
        """
        self.setIcon(self.PLOT_TYPE[plot_type, "icon"])
        self.setToolTip(self.PLOT_TYPE[plot_type, "state"])
        self._current_yfunc = getattr(self, f"func_{plot_type}")
        self._current_ylabel = getattr(self, f"label_{plot_type}")
        self.sig_new_plot_type.emit(plot_type)  # type: ignore[attr-defined]

    @staticmethod
    def func_generic(x: np.ndarray, y: np.ndarray) -> np.ndarray:  # noqa ARG001
        """
        The generic function which returns the identity for y.

        Parameters
        ----------
        x : np.ndarray
            The input x data.
        y : np.ndarray
            The input y data.

        Returns
        -------
        np.ndarray
            The return value.
        """
        return y

    @staticmethod
    def label_generic(xlabel: str, xunit: str, ylabel: str, yunit: str) -> str:  # noqa ARG001
        """
        Get the generic y label.

        Parameters
        ----------
        xlabel : str
            The original x label.
        xunit : str
            The original x unit name.
        ylabel : str
            The original y label.
        yunit : str
            The original y unit name.

        Returns
        -------
        str
            The new y label.
        """
        return ylabel + (" / " + yunit if yunit else "")

    @staticmethod
    def func_kratky(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        The Kratky function.

        Parameters
        ----------
        x : np.ndarray
            The input x data.
        y : np.ndarray
            The input y data.

        Returns
        -------
        np.ndarray
            The return value.
        """
        return y * x**2

    @staticmethod
    def label_kratky(xlabel: str, xunit: str, ylabel: str, yunit: str) -> str:
        """
        Get the y label for Kratky data.

        Parameters
        ----------
        xlabel : str
            The original x label.
        xunit : str
            The original x unit name.
        ylabel : str
            The original y label.
        yunit : str
            The original y unit name.

        Returns
        -------
        str
            The new y label.
        """
        _label = ylabel
        if xlabel:
            _label = f"{_label} * {xlabel}^2" if _label else f"{xlabel}^2"
        _unit = yunit
        if xunit:
            _unit += f"{_unit} * {xunit}^2" if _unit else f"{xunit}^2"
        return _label + (f" / ({_unit})" if len(_unit) > 0 else "")

    @property
    def plot_yfunc(self) -> Callable:
        """
        Return the function for mapping the input data to the plot type.

        Returns
        -------
        Callable
            The function which maps the input date to the chosen output.
        """
        return self._current_yfunc

    @property
    def plot_ylabel(self) -> Callable:
        """
        Return the function for mapping the input data to the plot type.

        Returns
        -------
        Callable
            The function which maps the input date to the chosen output.
        """
        return self._current_ylabel
