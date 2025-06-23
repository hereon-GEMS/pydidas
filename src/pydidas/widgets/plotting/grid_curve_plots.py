# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the GridCurvePlot which allows to plot a number of curves on a grid.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GridCurvePlot"]

from itertools import product
from typing import Any, Union

import numpy as np

from pydidas.contexts import Scan
from pydidas.core import Parameter, ParameterCollection, UserConfigError
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets import WidgetWithParameterCollection


class GridCurvePlot(WidgetWithParameterCollection):
    """
    A widget to display curve plots in a grid layout.
    """
    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}
        self.__scan = Scan()
        self.__n_hor = 4
        self.__n_vert = 3
        self.create_empty_widget("config_top", parent_widget=self)
        self.create_empty_widget("grid", parent_widget=self)
        self.create_empty_widget("config_bottom", parent_widget=self)

    @property
    def nplots(self) -> int:
        """Get the total number of plots in the grid."""
        return self.__n_hor * self.__n_vert

    def __check_key_and_scaling(self, dataset_key: Any, scaling: Any) -> None:
        """
        Check if the dataset key and scaling are valid.

        Parameters
        ----------
        dataset_key : Any
            The key of the dataset to check.
        scaling : Any
            The scaling to check.

        Raises
        ------
        UserConfigError
            If the dataset key is not a string
            or the scaling is not a tuple of two floats.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset '{dataset_key}' not found.")
        if not isinstance(scaling, tuple) or len(scaling) != 2:
            raise UserConfigError("Scaling must be a tuple of (min, max).")



    def clear(self):
        """
        Clear the datasets and reset the plot.
        """
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}
        self._update_plot()

    def set_scan(self, scan: Scan):
        """
        Set the scan context for the plot.

        Parameters
        ----------
        scan : Scan
            The Scan instance to set as the context for the plot.
        """
        if not isinstance(scan, Scan):
            raise UserConfigError("Provided scan is not a valid Scan instance.")
        self.__scan.update_from_scan(scan)
        self._update_plot()

    def set_datasets(self, **datasets: np.ndarray | None):
        """
        Set the datasets to be plotted in the grid.

        Parameters
        ----------
        **datasets : np.ndarray | None
            The datasets to be plotted.
        """
        if not datasets:
            raise UserConfigError("No datasets provided for plotting.")
        self._datasets = datasets
        self._update_plot()

    def set_xscaling(self, dataset_key: str, scaling: tuple[float, float], update_plot: bool = True):
        """
        Set the x-scaling for a specific dataset.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set the scaling for.
        scaling : tuple[float, float]
            The x-scaling as a tuple (min, max).
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        self.__check_key_and_scaling(dataset_key, scaling)
        self._xscaling[dataset_key] = scaling
        if update_plot:
            self._update_plot()

    def set_yscaling(self, dataset_key, scaling: tuple[float, float], update_plot: bool = True):
        """
        Set the y-scaling for a specific dataset.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set the scaling for.
        scaling : tuple[float, float]
            The y-scaling as a tuple (min, max).
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        self.__check_key_and_scaling(dataset_key, scaling)
        self._yscaling[dataset_key] = scaling
        if update_plot:
            self._update_plot()

    def set_y_autoscaling(self, dataset_key: str, update_plot: bool = True):
        """
        Set the y-axis scaling to use autoscaling.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set autoscaling for.
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset '{dataset_key}' not found.")
        self._yscaling[dataset_key] = (None, None)
        if update_plot:
            self._update_plot()

    def set_num_hor_plots(self, number: int):
        """
        Set the number of horizontal plots in the grid.

        Parameters
        ----------
        number : int
            The number of horizontal plots to set.
        """
        self.__n_hor = number
        self._update_grid_of_plots()

    def set_num_vert_plots(self, number: int):
        """
        Set the number of vertical plots in the grid.

        Parameters
        ----------
        number : int
            The number of vertical plots to set.
        """
        self.__n_vert = number
        self._update_grid_of_plots()

    def _update_grid_of_plots(self):
        """
        Update the grid of the plots based on the currently selected numbers.
        """
        _new_plot_indices = list(product(range(self.__n_vert), range(self.__n_hor)))
        _new_plot_keys = [f"plot_{_i}_{_j}" for _i, _j in _new_plot_indices]
        _plot_layout = self._widgets["grid"].layout()
        print("Updating grid of plots with keys:", _new_plot_keys)
        for _key in list(self._widgets):
            if _key.startswith("plot_") and _key not in _new_plot_keys:
               _widget = self._widgets.pop(_key)
               _plot_layout.removeWidget(_widget)
               _widget.deleteLater()
               _widget.setParent(None)
        for _key in _new_plot_keys:
            if _key in self._widgets:
                continue


    def _update_plot(self):
        """
        Update the plot with the current datasets and parameters.
        This method should be implemented to create the actual plot.
        """
        print("\nUpdating plot with datasets:")
        print(self._datasets.keys())
        print(
            "plotting",
            [
                (_key, _val.shape)
                for _key, _val in self._datasets.items()
                if _val is not None
            ],
        )
        print("X scaling:", self._xscaling)
        print("Y scaling:", self._yscaling)
