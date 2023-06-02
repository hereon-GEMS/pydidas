# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the BaseFitPlugin Plugin which holds generic methods for fitting plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseFitPlugin"]


from typing import List, Tuple

import numpy as np

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection

from ..core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from ..core.fitting import FitFuncMeta
from ..core.utils import process_1d_with_multi_input_dims
from .base_proc_plugin import ProcPlugin


class BaseFitPlugin(ProcPlugin):
    """
    Fit a single peak to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.
    """

    plugin_name = "Base fit plugin"
    basic_plugin = True
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = get_generic_param_collection(
        "process_data_dim",
        "fit_func",
        "fit_output",
        "fit_bg_order",
        "fit_lower_limit",
        "fit_upper_limit",
        "fit_sigma_threshold",
        "fit_min_peak_height",
    )
    input_data_dim = -1
    output_data_dim = 0
    new_dataset = True
    advanced_parameters = ["fit_sigma_threshold", "fit_min_peak_height"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fitter = None
        self._data = None
        self._data_x = None
        self._details = None
        self._fit_params = {}
        self._config = self._config | {
            "range_slice": None,
            "settings_updated_from_data": False,
            "data_x_hash": -1,
        }

    @property
    def detailed_results(self):
        """
        Get the detailed results for the FitSinglePeak plugin.

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
        self._fitter = FitFuncMeta.get_fitter(self.get_param_value("fit_func"))
        self._config["range_slice"] = None
        self._config["settings_updated_from_data"] = False
        self._config["min_peak_height"] = self.get_param_value("fit_min_peak_height")
        self._config["sigma_threshold"] = self.get_param_value("fit_sigma_threshold")
        self._config["bounds_low"] = self._fitter.param_bounds_low.copy()
        self._config["bounds_high"] = self._fitter.param_bounds_high.copy()
        self._config["param_labels"] = self._fitter.param_labels.copy()
        _bg_order = self.get_param_value("fit_bg_order")
        self.output_data_label = self.get_param_value("fit_output")
        self.output_data_unit = ""
        if _bg_order in [0, 1]:
            self._config["param_labels"].append("background_p0")
            self._config["bounds_low"].append(-np.inf)
            self._config["bounds_high"].append(np.inf)
        if _bg_order == 1:
            self._config["param_labels"].append("background_p1")
            self._config["bounds_low"].append(-np.inf)
            self._config["bounds_high"].append(np.inf)

    @process_1d_with_multi_input_dims
    def execute(self, data: Dataset, **kwargs: dict) -> Tuple[Dataset, dict]:
        """
        Perform a generic fit.

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
        raise NotImplementedError

    def prepare_input_data(self, data: Dataset):
        """
        Prepare and store the input data.

        Parameters
        ----------
        data : Dataset
            The input data.
        """
        self._data = data
        self._data_x = data.axis_ranges[0]
        self._crop_data_to_selected_range()
        if not self._config["settings_updated_from_data"]:
            self._update_settings_from_data()

    def _crop_data_to_selected_range(self):
        """
        Get the data in the range specified by the limits and store the selected
        x-range and data values.
        """
        _range = self._get_cropped_range()
        self._data_x = self._data_x[_range]
        self._data = self._data[_range]

    def _update_settings_from_data(self):
        """
        Output Plugin settings which depend on the input data.
        """
        if "center" in self._config["param_labels"]:
            _index = self._config["param_labels"].index("center")
            self._config["bounds_low"][_index] = np.amin(self._data_x)
            self._config["bounds_high"][_index] = np.amax(self._data_x)
        self.output_data_unit = self._data.axis_units[0]
        self.output_data_label = self.get_param_value("fit_output")
        self._config["settings_updated_from_data"] = True

    def _get_cropped_range(self):
        """
        Get the cropped index range corresponding to the selected data range.

        Returns
        -------
        range : np.ndarray
            The index range corresponding to the selected data ranges.
        """
        if (
            hash(self._data_x.tobytes()) != self._config["data_x_hash"]
            or self._config["range_slice"] is None
        ):
            _xlow = self.get_param_value("fit_lower_limit")
            _xhigh = self.get_param_value("fit_upper_limit")
            self._config["data_x_hash"] = hash(self._data_x.tobytes())
            _range_low = (
                np.where((self._data_x >= _xlow))[0]
                if _xlow is not None
                else np.arange(self._data_x.size)
            )
            _range_high = (
                np.where((self._data_x <= _xhigh))[0]
                if _xhigh is not None
                else np.arange(self._data_x.size)
            )
            _range = np.intersect1d(_range_low, _range_high)
            if _range.size < 5:
                raise UserConfigError(
                    "The data range for the fit is too small with less than 5 data "
                    "points. Please control the selected data range in the "
                    "FitSinglePeak plugin. The input data range is "
                    f"[{self._data_x[0]:.5f}, {self._data_x[-1]:.5f}]."
                )
            self._config["range_slice"] = slice(_range[0], _range[-1])
        return self._config["range_slice"]

    def check_min_peak_height(self) -> bool:
        """
        Check the minimum peak height and return the flag whether it is okay.

        Returns
        -------
        bool
            Flag whether the input data has a sufficiently large peak.
        """
        _min_peak = self._config["min_peak_height"]
        if _min_peak is not None:
            _tmp_y, bg_params = self._fitter.calculate_background_params(
                self._data_x, self._data, self.get_param_value("fit_bg_order")
            )
            if np.amax(_tmp_y) < _min_peak:
                self._details = {
                    None: self._create_details_for_invalid_peak(_tmp_y, bg_params)
                }
                return False
        return True

    def create_detailed_results(self, results: Dataset, start_fit_params: List) -> dict:
        """
        Create the detailed results for a single fit.

        This method will return detailed information to display for the user. The return
        format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second, "plot_titles"
        gives a title for each subplot. Third, "plot_ylabels" gives a y axis label for
        each subplot. Fourth, "items" provides  a list with the different items to be
        plotted. Each list entry must be a dictionary with the following keys: "plot"
        [to detemine the plot number], "label" [for the legend label] and "data" with
        the actual data.

        Parameters
        ----------
        results : pydidas.core.Dataset
            The Dataset with the regular results.
        start_fit_params : list
            The list with the starting fit params.

        Returns
        -------
        dict
            The dictionary with the detailed results in the format expected by pydidas.
        """
        if self._data is None:
            raise ValueError("Cannot get detailed results without input data.")
        _xfit = np.linspace(
            self._data_x[0], self._data_x[-1], num=(self._data_x.size - 1) * 10 + 1
        )
        _fit_param_vals = list(self._fit_params.values())
        _dset_kws = {
            "axis_ranges": [_xfit],
            "axis_labels": self._data.axis_labels,
            "axis_units": self._data.axis_units,
            "data_unit": self._data.data_unit,
        }
        _datafit = Dataset(self._fitter.function(_fit_param_vals, _xfit), **_dset_kws)
        _startfit = Dataset(self._fitter.function(start_fit_params, _xfit), **_dset_kws)
        _residual = self._fitter.delta(_fit_param_vals, self._data_x, self._data)

        _details = {
            "n_plots": 3,
            "plot_titles": {0: "data and fit", 1: "residual", 2: "starting guess"},
            "plot_ylabels": {
                0: "intensity / a.u.",
                1: "intensity / a.u.",
                2: "intensity / a.u.",
            },
            "metadata": "\n".join(
                f"{_key}: {results.metadata[_key]}"
                for _key in ["fit_func", "fit_params", "fit_residual_std"]
            ),
            "items": [
                {"plot": 0, "label": "input data", "data": self._data},
                {"plot": 0, "label": "fitted_data", "data": _datafit},
                {"plot": 1, "label": "residual", "data": _residual},
                {"plot": 2, "label": "input data", "data": self._data},
                {"plot": 2, "label": "starting guess", "data": _startfit},
            ],
        }
        if self.get_param_value("fit_bg_order") is not None:
            _bg_poly = [self._fit_params["background_p0"]]
            if "background_p1" in self._fit_params:
                _bg_poly.insert(0, self._fit_params["background_p1"])
            _bg = Dataset(np.polyval(_bg_poly, _xfit), **_dset_kws)
            _details["items"].append({"plot": 0, "label": "background", "data": _bg})
        return _details

    def _create_details_for_invalid_peak(self, bg_corrected_data, bg_params):
        """
        Create the details for an invalid peak.

        Parameters
        ----------
        bg_corrected_data : np.ndarray
            The background-corrected data.
        bg_params : list
            The parameters to calculate the background level.

        Returns
        -------
        dict
            The invalid results.
        """
        if len(bg_params) == 0:
            return {
                "n_plots": 1,
                "plot_titles": {0: "data"},
                "plot_ylabels": {0: "intensity / a.u."},
                "metadata": "",
                "items": [{"plot": 0, "label": "input data", "data": self._data}],
            }
        _bg = Dataset(
            np.zeros(self._data_x.size) + bg_params[0], **self._data.property_dict
        )
        if len(bg_params) == 2:
            _bg += self._data_x * bg_params[1]
        return {
            "n_plots": 2,
            "plot_titles": {0: "data and background", 1: "background-corrected data"},
            "plot_ylabels": {0: "intensity / a.u.", 1: "intensity / a.u."},
            "metadata": "",
            "items": [
                {"plot": 0, "label": "input data", "data": self._data},
                {"plot": 0, "label": "background", "data": _bg},
                {
                    "plot": 1,
                    "label": "background-corrected data",
                    "data": bg_corrected_data,
                },
            ],
        }
