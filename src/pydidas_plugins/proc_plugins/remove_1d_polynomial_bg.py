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
Module with the Remove1dPolynomialBackground Plugin which can be used to
subtract a polynomial background from a 1-d dataset, e.g. integrated
diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Remove1dPolynomialBackground"]

from typing import Union

import numpy as np
from numpy.polynomial import Polynomial

from pydidas.core import Dataset, Parameter, ParameterCollection, get_generic_parameter
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.plugins import ProcPlugin


DEFAULT_PARAMS_FOR_REMOVE1dPOLYBG = ParameterCollection(
    get_generic_parameter("process_data_dim"),
    Parameter(
        "threshold_low",
        float,
        None,
        allow_None=True,
        name="Lower threshold",
        tooltip=(
            "The lower threshold. Any values in the corrected"
            " dataset smaller than the threshold will be set "
            "to the threshold value."
        ),
    ),
    Parameter(
        "fit_order",
        int,
        3,
        name="Polynomial fit order",
        tooltip=(
            "The polynomial order for the fit. This value "
            "should typically not exceed 3 or 4."
        ),
    ),
    Parameter(
        "include_limits",
        int,
        0,
        choices=[True, False],
        name="Always fit endpoints",
        tooltip=(
            "Flag to force the inclusion of both endpoints "
            "in the initial points for the fit."
        ),
    ),
    Parameter(
        "kernel_width",
        int,
        5,
        name="Averaging width",
        tooltip=(
            "The width of the averaging kernel (which is only "
            "applied to the data for fitting)."
        ),
    ),
)


class Remove1dPolynomialBackground(ProcPlugin):
    """
    Subtract a polynomial background from a 1-dimensional profile.

    This plugin uses a multi-tiered approach to remove the background.
    The background is calculated using the following approach:
    First, the data is smoothed by an averaging filter to remove noise.
    Second, local minima in the smoothed dataset are extracted and a
    polynomial background is fitted to these local minima. All local minima
    which are higher by more than 20% with respect to a linear fit between
    their neighboring local minima are discarded.
    Third, the residual between the background and the smoothed data is
    calculated and the x-positions of all local minima of the residual are
    used in conjunction with their data values to fit a final background.
    """

    plugin_name = "Remove 1D polynomial background"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = DEFAULT_PARAMS_FOR_REMOVE1dPOLYBG

    output_data_label = "Background-corrected data"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thresh = None
        self._fit_order = 3
        self._include_limits = False
        self._kernel = np.ones(5) / 5
        self._klim_low = 2
        self._klim_high = -2
        self._local_minina_threshold = 1.2
        self.__input_data = None
        self.__results = None
        self._details = {}
        self.__kwargs = {}

    @property
    def detailed_results(self) -> dict:
        """
        Get the detailed results for the Remove1dPolynomialBackground plugin.

        Returns
        -------
        dict
            The dictionary with detailed results.
        """
        return self._details

    def pre_execute(self):
        """
        Set-up the fit and store required values.
        """
        self._thresh = self.get_param_value("threshold_low")
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None
        self._fit_order = self.get_param_value("fit_order")
        self._include_limits = self.get_param_value("include_limits")

        _kernel = self.get_param_value("kernel_width")
        if _kernel > 0:
            self._kernel = np.ones(_kernel) / _kernel
            self._klim_low = _kernel // 2
            self._klim_high = _kernel - 1 - _kernel // 2
        else:
            self._kernel = None

    @process_1d_with_multi_input_dims
    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Fit and remove a polynomial background to the data.

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The 1-dimensional data.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The new
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self.__input_data = data
        self.__kwargs = kwargs

        if self._kernel is not None:
            _raw = data.copy()
            data[self._klim_low : -self._klim_high] = np.convolve(
                data, self._kernel, mode="valid"
            )
        _x = np.arange(data.size)
        # find and fit the local minima
        local_min = (
            np.where(
                (data[1:-1] < np.roll(data, 1)[1:-1])
                & (data[1:-1] < np.roll(data, -1)[1:-1])
            )[0]
            + 1
        )
        local_min = self.__filter_local_minima_by_offset(local_min, data, 1.2)

        if self._include_limits:
            local_min = np.insert(local_min, 0, 0)
            local_min = np.insert(local_min, local_min.size, data.size - 1)

        _p_prelim = Polynomial.fit(local_min, data[local_min], self._fit_order)

        # calculate the residual and fit residual's local minima
        _res = (data - _p_prelim(_x)) / data
        _local_res_min = (
            np.where(
                (_res[1:-1] < np.roll(_res, 1)[1:-1])
                & (_res[1:-1] < np.roll(_res, -1)[1:-1])
            )[0]
            + 1
        )
        _tmpindices = np.where(_res[_local_res_min] <= 0.002)[0]
        _local_res_min = _local_res_min[_tmpindices]

        _p_final = Polynomial.fit(_local_res_min, data[_local_res_min], self._fit_order)

        if self._kernel is not None:
            data = _raw
        data = data - _p_final(_x)
        if self._thresh is not None:
            data[:] = np.where(data < self._thresh, self._thresh, data)

        self.__background = Dataset(
            _p_final(_x),
            axis_labels=data.axis_labels,
            axis_ranges=data.axis_ranges,
            axis_units=data.axis_units,
            data_label=data.data_label,
            data_unit=data.data_unit,
        )

        self.__results = data
        if kwargs.get("store_details", False):
            self._details = {None: self._create_detailed_results()}
        return data, kwargs

    @staticmethod
    def __filter_local_minima_by_offset(
        xpos: np.ndarray, data: np.ndarray, offset: float
    ) -> np.ndarray:
        """
        Filter local minima from a list of positions.

        Minima are filtered by evaluating their offset from the linear
        connection between neighbouring local minima.

        Parameters
        ----------
        xpos : np.ndarray
            The x positions of the datapoints
        data : np.ndarray
            The data values for the points.
        offset : float
            The threshold value offset at which to discard local minima.

        Returns
        -------
        xpos : np.ndarray
            The updated and filtered x positions.
        """
        _index = 1
        while _index < xpos.size - 1:
            _dx = xpos[_index + 1] - xpos[_index - 1]
            _dy = data[xpos[_index + 1]] - data[xpos[_index - 1]]
            _ypos = (xpos[_index] - xpos[_index - 1]) / _dx * _dy + data[
                xpos[_index - 1]
            ]
            if data[xpos[_index]] >= offset * _ypos:
                xpos = np.delete(xpos, _index, 0)
            else:
                _index += 1
        return xpos

    def _create_detailed_results(self) -> dict:
        """
        Get the detailed results for the background removal.

        This method will return detailed information to display for the user. The return
        format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second, "plot_titles"
        gives a title for each subplot. Third, "plot_ylabels" gives a y axis label for
        each subplot. Fourth, "items" provides a list with the different items to be
        plotted. Each list entry must be a dictionary with the following keys: "plot"
        [to determine the plot number], "label" [for the legend label] and "data" with
        the actual data.

        Returns
        -------
        dict
            The dictionary with the detailed results in the format expected by pydidas.
        """
        if self.__input_data is None:
            raise ValueError("Cannot get detailed results without input data.")
        return {
            "n_plots": 2,
            "plot_titles": {
                0: "input data and background",
                1: "plugin results (corrected data)",
            },
            "plot_ylabels": {
                0: "intensity / a.u.",
                1: "intensity / a.u.",
            },
            "items": [
                {"plot": 0, "label": "input data", "data": self.__input_data},
                {"plot": 0, "label": "background", "data": self.__background},
                {"plot": 1, "label": "", "data": self.__results},
            ],
        }
