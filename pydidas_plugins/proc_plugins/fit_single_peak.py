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
Module with the FitSinglePeak Plugin which can be used to fit a single peak
in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitSinglePeak"]

import numpy as np
from scipy.optimize import least_squares

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED

from pydidas.core import (
    get_generic_param_collection,
    Dataset,
    UserConfigError,
    Parameter,
)
from pydidas.core.utils import (
    process_1d_with_multi_input_dims,
    calculate_result_shape_for_multi_input_dims,
)
from pydidas.core.fitting import FitFuncMeta
from pydidas.plugins import ProcPlugin


class FitSinglePeak(ProcPlugin):
    """
    Fit a single peak to a data
    """

    plugin_name = "Fit single peak"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = get_generic_param_collection(
        "process_data_dim",
        "fit_func",
        "fit_bg_order",
        "fit_lower_limit",
        "fit_upper_limit",
    )
    default_params.add_param(
        Parameter(
            "output",
            str,
            "Peak position",
            choices=[
                "Peak position",
                "Peak area",
                "Fit normalized standard deviation",
                "Peak area and position",
                "Peak area, position and norm. std",
            ],
            name="Output",
            tooltip=(
                "The output of the fitting plugin. The plugin can either return"
                " the peak area or the peak position, or both. Alternatively, "
                "The input data, the fitted data and the residual can be returned"
                " as well. Note that the fit parameters are always stored in the "
                "metadata."
            ),
        ),
    )
    default_params.add_params(
        get_generic_param_collection("fit_sigma_threshold", "fit_min_peak_height")
    )
    input_data_dim = -1
    output_data_dim = 0
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params["fit_func"].choices = list(FitFuncMeta.registry.keys())
        self._fitter = None
        self._data = None
        self._data_x = None
        self._details = None
        self._fit_params = {}
        self._config = self._config | {
            "range_slice": None,
            "settings_updated_from_data": False,
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
        self.output_data_label = self.get_param_value("output")
        self.output_data_unit = ""
        self._config["range_slice"] = None
        self._config["settings_updated_from_data"] = False
        self._config["min_peak"] = self.get_param_value("fit_min_peak_height")
        self._config["bounds_low"] = self._fitter.param_bounds_low.copy()
        self._config["bounds_high"] = self._fitter.param_bounds_high.copy()
        self._config["param_labels"] = self._fitter.param_labels.copy()
        _bg_order = self.get_param_value("fit_bg_order")
        if _bg_order in [0, 1]:
            self._config["param_labels"].append("background_p0")
            self._config["bounds_low"].append(-np.inf)
            self._config["bounds_high"].append(np.inf)
        if _bg_order == 1:
            self._config["param_labels"].append("background_p1")
            self._config["bounds_low"].append(-np.inf)
            self._config["bounds_high"].append(np.inf)

    @process_1d_with_multi_input_dims
    def execute(self, data, **kwargs):
        """
        Fit a peak to the data.

        Note that the results includes the original data, the fitted data and
        the residual and that the fit Parameters are included in the kwarg
        metadata.

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
        self._data = data
        self._data_x = data.axis_ranges[0]
        if self._config["min_peak"] is not None and self._config["min_peak"] < np.amax(
            data
        ):
            _results = self._create_result_dataset(valid=False)
            return _results, kwargs
        self._update_settings_from_data()
        self._crop_data_to_selected_range()
        _startguess = self._calc_param_start_guess()
        _res = least_squares(
            self._fitter.delta,
            _startguess,
            args=(self._data_x, self._data.array),
            bounds=(self._config["bounds_low"], self._config["bounds_high"]),
        )
        self._fit_params = dict(zip(self._config["param_labels"], _res.x))
        _results = self._create_result_dataset()
        kwargs["fit_params"] = self._fit_params
        kwargs["fit_func"] = self._fitter.function.__name__
        self._details = {None: self._create_detailed_results(_results, _startguess)}
        return _results, kwargs

    def _update_settings_from_data(self):
        """
        Output Plugin settings which depend on the input data.
        """
        if self._config["settings_updated_from_data"]:
            return
        if "center" in self._config["param_labels"]:
            _index = self._config["param_labels"].index("center")
            self._config["bounds_low"][_index] = np.amin(self._data_x)
            self._config["bounds_high"][_index] = np.amax(self._data_x)
        if self.get_param_value("output") == "Peak position":
            self.output_data_unit = self._data.axis_units[0]
        elif self.get_param_value("output") == "Peak area":
            _pos_unit = self._data.axis_units[0]
            _val_unit = self._data.data_unit
            self.output_data_unit = f"({_pos_unit} * {_val_unit})"
        self._config["settings_updated_from_data"] = True

    def _crop_data_to_selected_range(self):
        """
        Get the data in the range specified by the limits and store the selected
        x-range and data values.
        """
        _range = self._get_cropped_range()
        if _range.size < 5:
            raise UserConfigError(
                "The data range for the fit is too small with less than 5 data points."
            )
        self._data_x = self._data_x[_range]
        self._data = self._data[_range]

    def _get_cropped_range(self):
        """
        Get the cropped index range corresponding to the selected data range.

        Returns
        -------
        range : np.ndarray
            The index range corresponding to the selected data ranges.
        """
        if self._config["range_slice"] is not None:
            return self._config["range_slice"]
        _xlow = self.get_param_value("fit_lower_limit")
        _xhigh = self.get_param_value("fit_upper_limit")
        _range = np.where((self._data_x >= _xlow) & (self._data_x <= _xhigh))[0]
        self._config["range_slice"] = _range
        return _range

    def _calc_param_start_guess(self):
        """
        Calculate the fit starting Parameters based on the x-range and the data.

        Returns
        -------
        startguess : list
            The list with the starting guess for the

        """
        _startguess = self._fitter.guess_fit_start_params(self._data_x, self._data)
        _bg_order = self.get_param_value("fit_bg_order")
        if _bg_order in [0, 1]:
            _startguess.append(np.amin(self._data))
        if _bg_order == 1:
            _startguess.append(0)
        return _startguess

    def _create_result_dataset(self, valid=True):
        """
        Create a new Dataset from the original data and the data fit including
        all the old metadata.

        Note that this method does not update the new metadata with the fit
        parameters. The new dataset includes a second dimensions with entries
        for the raw data, the data fit and the residual.

        Parameters
        ----------
        valid : bool, optional
            Flat to confirm the results are valid. The default is True.

        Returns
        -------
        new_data : pydidas.core.Dataset
            The new dataset.
        """
        _output = self.get_param_value("output")
        if valid:
            _datafit = self._fitter.function(
                list(self._fit_params.values()), self._data_x
            )
            _residual = abs(np.std(self._data - _datafit) / np.mean(self._data))
            if _output == "Peak area":
                _new_data = [self._fit_params["amplitude"]]
            elif _output == "Peak position":
                _new_data = [self._fit_params["center"]]
            elif _output == "Peak area and position":
                _new_data = [self._fit_params["amplitude"], self._fit_params["center"]]
            elif _output == "Fit normalized standard deviation":
                _new_data = [_residual]
            elif _output == "Peak area, position and norm. std":
                _new_data = [
                    self._fit_params["amplitude"],
                    self._fit_params["center"],
                    _residual,
                ]
        if (
            not valid
            or _residual >= self.get_param_value("fit_sigma_threshold")
            or not self._data_x[0] <= self._fit_params["center"] <= self._data_x[-1]
        ):
            _new_data = self._config["result_shape"][0] * [np.nan]
        _result_dataset = Dataset(
            _new_data,
            data_label=_output,
            data_unit="a.u.",
            axis_labels=[_output],
            axis_units=[self._data.axis_units[0]],
        )
        _new_metadata = {
            "fit_func": self._fitter.func_name,
            "fit_params": self._fit_params,
            "fit_residual_std": _residual,
        }
        _result_dataset.metadata = self._data.metadata | _new_metadata
        return _result_dataset

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        _output = self.get_param_value("output")
        self.output_data_label = _output
        self.output_data_unit = "a.u."
        if _output in [
            "Peak area",
            "Peak position",
            "Fit normalized standard deviation",
        ]:
            self._config["result_shape"] = (1,)
        elif _output == "Peak area and position":
            self._config["result_shape"] = (2,)
        elif _output == "Peak area, position and norm. std":
            self._config["result_shape"] = (3,)
        else:
            raise ValueError("No result shape defined for the selected input")

    def _create_detailed_results(self, results, start_fit_params):
        """
        Create the detailed results for the single peak fitting.

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
        _datafit = Dataset(
            self._fitter.function(list(self._fit_params.values()), _xfit),
            axis_ranges=[_xfit],
            axis_labels=self._data.axis_labels,
            axis_units=self._data.axis_units,
            data_unit=self._data.data_unit,
        )

        _startfit = Dataset(
            self._fitter.function(start_fit_params, _xfit),
            axis_ranges=[_xfit],
            axis_labels=self._data.axis_labels,
            axis_units=self._data.axis_units,
            data_unit=self._data.data_unit,
        )

        _residual = self._fitter.delta(
            list(self._fit_params.values()), self._data_x, self._data
        )
        _meta = "\n".join(
            f"{_key}: {results.metadata[_key]}"
            for _key in ["fit_func", "fit_params", "fit_residual_std"]
        )
        _details = {
            "n_plots": 3,
            "plot_titles": {0: "data and fit", 1: "residual", 2: "starting guess"},
            "plot_ylabels": {
                0: "intensity / a.u.",
                1: "intensity / a.u.",
                2: "intensity / a.u.",
            },
            "metadata": _meta,
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
            _bg = Dataset(
                np.polyval(_bg_poly, self._data_x),
                axis_ranges=[self._data_x],
                axis_labels=self._data.axis_labels,
                axis_units=self._data.axis_units,
                data_unit=self._data.data_unit,
            )
            _details["items"].append({"plot": 0, "label": "background", "data": _bg})
        return _details
