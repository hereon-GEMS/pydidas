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


from typing import Any

import numpy as np

from pydidas.core import Parameter, ParameterCollection, UserConfigError
from pydidas.widgets import WidgetWithParameterCollection


_GRID_CURVE_PLOT_PARAMS = ParameterCollection(
    Parameter(
        "num_horizontal_plots",
        int,
        4,
        name="Number of horizontal plots",
        tooltip="The number of plots to display in each row of the grid.",
        choices=[2, 3, 4, 5, 6],
    ),
    Parameter(
        "num_vertical_plots",
        int,
        3,
        name="Number of vertical plots",
        tooltip="The number of plots to display in each column of the grid.",
        choices=[2, 3, 4, 5, 6],
    ),
)


class GridCurvePlot(WidgetWithParameterCollection):
    """
    A widget to display curve plots in a grid layout.

    """

    default_params = _GRID_CURVE_PLOT_PARAMS

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}

    def clear(self):
        """
        Clear the datasets and reset the plot.
        """
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}
        self._update_plot()

    def set_datasets(self, **datasets: dict[str, np.ndarray | None]):
        """
        Set the datasets to be plotted in the grid.

        Parameters
        ----------
        **datasets : dict[str, np.ndarray]
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
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset '{dataset_key}' not found.")
        if not isinstance(scaling, tuple) or len(scaling) != 2:
            raise UserConfigError("Scaling must be a tuple of (min, max).")
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
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset '{dataset_key}' not found.")
        if not isinstance(scaling, tuple) or len(scaling) != 2:
            raise UserConfigError("Scaling must be a tuple of (min, max).")
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
