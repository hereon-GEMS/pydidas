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
Module with the RemoveOutliers Plugin which can be used to remove outliers of
a defined width.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RemoveOutliers"]


import numpy as np

from pydidas.core import Dataset, Parameter, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.plugins import ProcPlugin


_KERNEL_PARAM = Parameter(
    "kernel_width",
    int,
    2,
    name="Kernel width",
    tooltip=(
        "The width of the search kernel (i.e. the maximum "
        "width of outliers which can be detected)."
    ),
)
_OUTLIER_THRESH_PARAM = Parameter(
    "outlier_threshold",
    float,
    10,
    name="Outlier threshold",
    unit="a.u.",
    tooltip=(
        "The threshold for outliers. Any points which differ more than the "
        "threshold from the background (i.e. the surrounding data values) "
        "will be removed and replaced by average from the surroundings."
    ),
)


class RemoveOutliers(ProcPlugin):
    """
    Remove outlier points from a 1D dataset.

    This plugin detects any data points which differ by more than the threshold from
    its neighbors and replaces them with the surrounding average.
    """

    plugin_name = "Remove Outliers"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = get_generic_param_collection("process_data_dim")
    default_params.add_params(_KERNEL_PARAM, _OUTLIER_THRESH_PARAM)

    output_data_label = "data without outliers"
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
        self._config["index_offset"] = self.get_param_value("kernel_width") + 1
        self._config["threshold"] = self.get_param_value("outlier_threshold")
        self._config["width"] = self.get_param_value("kernel_width")

    @process_1d_with_multi_input_dims
    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Remove outliers from a 1d Dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._input_data = data
        self._create_derived_data()
        self._outliers = np.array(())
        self._find_and_store_high_outliers()
        self._find_and_store_low_outliers()
        _outliers_index_cropped = self._outliers.astype(int)
        _outliers_index_data = _outliers_index_cropped + self._config["index_offset"]
        data[_outliers_index_data] = self._config["ref_outer"][_outliers_index_cropped]

        self._results = data
        if kwargs.get("store_details", False):
            self._details = {None: self._create_detailed_results()}
        return data, kwargs

    def _create_derived_data(self):
        """
        Create the required derived data to identify outliers.
        """
        _width = self.get_param_value("kernel_width")
        _slice = slice(_width + 1, self._input_data.size - _width - 1)
        _cfg = self._config
        _data_offset = -np.amin(self._input_data) + 1
        _data = self._input_data + _data_offset

        _cfg["rolled_p"] = np.roll(_data, _width)[_slice]
        _cfg["rolled_pp"] = np.roll(_data, _width + 1)[_slice]
        _cfg["rolled_m"] = np.roll(_data, -_width)[_slice]
        _cfg["rolled_mm"] = np.roll(_data, -_width - 1)[_slice]
        _cfg["ref_outer"] = 0.5 * (_cfg["rolled_pp"] + _cfg["rolled_mm"]) - _data_offset
        _data = _data[_slice]
        _cfg["cropped_working_data"] = _data
        _cfg["ref_corrected_data"] = _data - _cfg["ref_outer"] - _data_offset

    def _find_and_store_high_outliers(self):
        """
        Identify the high data outliers and store their indices.
        """
        _cfg = self._config
        _outliers = np.where(
            (self._config["ref_corrected_data"] >= _cfg["threshold"])
            & (
                _cfg["cropped_working_data"]
                > _cfg["rolled_p"] + 0.3 * _cfg["threshold"]
            )
            & (
                _cfg["cropped_working_data"]
                > _cfg["rolled_m"] + 0.3 * _cfg["threshold"]
            )
        )[0]
        _outliers = self._filter_for_outliers_on_flank(_outliers, high_peak=True)
        self._outliers = np.unique(np.concatenate((self._outliers, _outliers)))

    def _find_and_store_low_outliers(self):
        """
        Identify the low data outliers and store their indices.
        """
        _cfg = self._config
        _outliers = np.where(
            (_cfg["ref_corrected_data"] <= -1 * _cfg["threshold"])
            & (
                _cfg["cropped_working_data"]
                < _cfg["rolled_p"] - 0.3 * _cfg["threshold"]
            )
            & (
                _cfg["cropped_working_data"]
                < _cfg["rolled_m"] - 0.3 * _cfg["threshold"]
            )
        )[0]
        _outliers = self._filter_for_outliers_on_flank(_outliers, high_peak=False)
        self._outliers = np.unique(np.concatenate((self._outliers, _outliers)))

    def _filter_for_outliers_on_flank(
        self, outliers: np.ndarray, high_peak: bool = True
    ) -> np.ndarray:
        """
        Filter for outlier points which are not true outliers but sit on the flank.

        Parameters
        ----------
        outliers : np.ndarray
            The array with outlier indices.
        high_peak : bool, optional
            Set the flag for high peak (or low peak) to use the correct comparator.

        Returns
        -------
        outliers : np.ndarray
            The filtered outlier index array.
        """
        _neighbor_indices = (
            np.where(
                self._config["ref_corrected_data"] >= 0.3 * self._config["threshold"]
            )[0]
            if high_peak
            else np.where(
                self._config["ref_corrected_data"] <= -0.3 * self._config["threshold"]
            )[0]
        )
        for _ in range(2):
            _neighbor_outliers = np.array(
                [
                    _index
                    for _index in _neighbor_indices
                    if _index - 1 in outliers or _index + 1 in outliers
                ]
            )
            outliers = np.unique(np.concatenate((outliers, _neighbor_outliers)))
        _neighbors = np.zeros(outliers.shape, dtype=np.int16)
        for _index, _outlier in enumerate(outliers):
            if _neighbors[_index] == 0:
                while _outlier + _neighbors[_index] in outliers:
                    _neighbors[_index] += 1
                _neighbors[_index : _index + _neighbors[_index]] = _neighbors[_index]
        outliers = outliers[np.where(_neighbors <= self._config["width"])[0]]
        return outliers

    def _create_detailed_results(self) -> dict:
        """
        Get the detailed results for the outlier removal.

        This method will return detailed information to display for the user. The return
        format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second, "plot_titles"
        gives a title for each subplot. Third, "plot_ylabels" gives a y-axis label for
        each subplot. Fourth, "items" provides a list with the different items to be
        plotted. Each list entry must be a dictionary with the following keys: "plot"
        [to determine the plot number], "label" [for the legend label] and "data" with
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
