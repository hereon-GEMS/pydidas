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
Module with the RollingAverage1d Plugin which can be used to apply a rolling average
to input data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RollingAverage1d"]

import numpy as np

from pydidas.core import (
    Dataset,
    Parameter,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.plugins import ProcPlugin


_KERNEL_PARAM = Parameter(
    "kernel_width",
    int,
    3,
    name="Average num datapoints",
    tooltip=("The width of the averaging kernel in data points."),
)


class RollingAverage1d(ProcPlugin):
    """
    Remove outlier points from a 1D dataset.

    This plugin applies a rolling average to the input data. The width of the averaging
    kernel can be selected by the corresponding Parameter. All points are weighted with
    the same number.
    """

    plugin_name = "Rolling average (1d)"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = get_generic_param_collection("process_data_dim")
    default_params.add_params(_KERNEL_PARAM)

    output_data_label = "averaged data"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None
        self._details = {}

    @property
    def detailed_results(self) -> dict:
        """
        Get the detailed results for the RemoveOutliers plugin.

        Returns
        -------
        dict
            The dictionary with detailed results.
        """
        return self._details

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        self._config["index_offset"] = self.get_param_value("kernel_width") // 2 + 1
        self._config["width"] = self.get_param_value("kernel_width")
        if self._config["width"] < 1:
            raise UserConfigError("The averaging kernel must be at least of size 2.")
        self._kernel = np.ones(self._config["width"]) / self._config["width"]

    @process_1d_with_multi_input_dims
    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Crop 1D data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _new_data : pydidas.core.Dataset
            The averaged profile.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._input_data = data
        _new_data = Dataset(
            np.convolve(data, self._kernel, mode="same"), **data.property_dict
        )
        _offset = self._config["index_offset"]
        _new_data[:_offset] = data[:_offset]
        _new_data[-_offset:] = data[-_offset:]
        self._results = _new_data
        if kwargs.get("store_details", False):
            self._details = {None: self._create_detailed_results()}
        return _new_data, kwargs

    def _create_detailed_results(self):
        """
        Get the detailed results for the rolling average.

        Returns
        -------
        dict
            The dictionary with the detailed results in the format expected by pydidas.
        """
        if self._input_data is None:
            raise ValueError("Cannot get detailed results without input data.")
        return {
            "n_plots": 1,
            "plot_titles": {
                0: "rolling average",
            },
            "plot_ylabels": {
                0: "intensity / a.u.",
            },
            "items": [
                {"plot": 0, "label": "input data", "data": self._input_data},
                {"plot": 0, "label": "corrected data", "data": self._results},
            ],
        }
