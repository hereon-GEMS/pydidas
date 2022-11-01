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
Module with the RemoveOutliers Plugin which can be used to remove outliers of
a defined width.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["RemoveOutliers"]

import warnings

import numpy as np

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.core import get_generic_param_collection, Parameter
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.plugins import ProcPlugin


class RemoveOutliers(ProcPlugin):
    """
    Remove outlier points from a 1D dataset.
    """

    plugin_name = "Remove Outliers"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = get_generic_param_collection("process_data_dim")
    default_params.add_params(
        Parameter(
            "kernel_width",
            int,
            2,
            name="Kernel width",
            tooltip=(
                "The width of the search kernel (i.e. the maximum "
                "width of outliers which can be detected)."
            ),
        ),
        Parameter(
            "outlier_threshold",
            float,
            1,
            name="Relative outlier threshold",
            tooltip=(
                "The threshold for outliers. Any points which "
                "differ more than the threshold from the background"
                " will be removed."
            ),
        ),
    )
    input_data_dim = -1
    output_data_dim = -1
    output_data_label = "data without outliers"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None
        self._details = None

    @property
    def detailed_results(self):
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
        Set up the required functions and fit variable labels.
        """

    @process_1d_with_multi_input_dims
    def execute(self, data, **kwargs):
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
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._input_data = data.copy()
        _width = self.get_param_value("kernel_width")
        _threshold = self.get_param_value("outlier_threshold")
        _data_p = np.roll(data, _width)
        _data_m = np.roll(data, -_width)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _data_p_norm = ((data - _data_p) / data)[_width:-_width]
            _data_m_norm = ((data - _data_m) / data)[_width:-_width]
            _low_outliers_same_sign = np.where(
                (_data_p_norm <= -_threshold) & (_data_m_norm <= -_threshold)
            )[0]
            _data_p_norm_p = ((data - _data_p) / _data_p)[_width:-_width]
            _data_m_norm_m = ((data - _data_m) / _data_m)[_width:-_width]
            _high_outliers_same_sign = np.where(
                (_data_p_norm_p >= _threshold) & (_data_m_norm_m >= _threshold)
            )[0]
            _high_outliers_opposize_sign = np.where(
                (_data_p_norm_p <= -_threshold) & (_data_m_norm_m <= -_threshold)
            )[0]
        _outliers = (
            np.concatenate(
                (
                    _high_outliers_same_sign,
                    _high_outliers_opposize_sign,
                    _low_outliers_same_sign,
                )
            )
            + _width
        )
        data[_outliers] = (_data_p[_outliers] + _data_m[_outliers]) / 2
        self._results = data
        self._details = {None: self._create_detailed_results()}
        return data, kwargs

    def _create_detailed_results(self):
        """
        Get the detailed results for the outlier removal.

        This method will return detailed information to display for the user. The return
        format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second, "plot_titles"
        gives a title for each subplot. Third, "plot_ylabels" gives a y axis label for
        each subplot. Fourth, "items" provides  a list with the different items to be
        plotted. Each list entry must be a dictionary with the following keys: "plot"
        [to detemine the plot number], "label" [for the legend label] and "data" with
        the actual data.

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
                0: "outlier correction",
            },
            "plot_ylabels": {
                0: "intensity / a.u.",
            },
            "items": [
                {"plot": 0, "label": "input data", "data": self._input_data},
                {"plot": 0, "label": "corrected data", "data": self._results},
            ],
        }
