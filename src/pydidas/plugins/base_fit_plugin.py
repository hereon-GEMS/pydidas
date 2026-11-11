# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseFitPlugin"]


import itertools
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
from scipy.optimize import least_squares

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.fit_func_base import FitFuncBase
from pydidas.core.utils.decorators import create_multi_dim_result_dataset
from pydidas.core.utils.iterable_utils import (
    insert_item_in_tuple,
    remove_item_at_index_from_iterable,
)
from pydidas.plugins.base_proc_plugin import ProcPlugin


if TYPE_CHECKING:
    from pydidas.widgets.plugin_config_widgets import GenericPluginConfigWidget


def _format_fit_metadata(metadata: dict[str, Any]) -> str:
    """
    Format the fit metadata as text to be displayed with the plots.

    Parameters
    ----------
    metadata : dict[str, Any]
        The metadata of the fit results.

    Returns
    -------
    str
        The formatted text.
    """
    _param_lines = "\n    ".join(
        f"{_key}: {_value:.6f}," for _key, _value in metadata["fit_params"].items()
    )
    return (
        f"fit_func: {metadata['fit_func']}\n"
        f"fit_residual_std: {metadata['fit_residual_std']:.6f}\n"
        "fit params: {\n    " + _param_lines + "\n}"
    )


def _create_individual_peak_items(
    fitter: type[FitFuncBase],
    fit_param_vals: tuple[float, ...],
    x: np.ndarray,
    dataset_kwargs: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Create the plot items for the individual peaks of the fit.

    Parameters
    ----------
    fitter : type[FitFuncBase]
        The fit function.
    fit_param_vals : tuple[float, ...]
        The fitted parameter values.
    x : np.ndarray
        The x values at which to calculate the peak profiles.
    dataset_kwargs : dict[str, Any]
        The keyword arguments for the Dataset creation.

    Returns
    -------
    list[dict[str, Any]]
        The plot items for the individual peaks.
    """
    _n_pp = fitter.num_peak_params
    return [
        {
            "plot": 1,
            "label": f"peak {_i}",
            "data": Dataset(
                fitter.func(fit_param_vals[_i * _n_pp : (_i + 1) * _n_pp], x),
                **dataset_kwargs,
            ),
            "linewidth": 2.5,
        }
        for _i in range(fitter.num_peaks)
    ]


def _create_background_item(
    fit_params: dict[str, float], x_reduced: np.ndarray, dataset_kwargs: dict[str, Any]
) -> dict[str, Any]:
    """
    Create the plot item for the fitted background.

    Parameters
    ----------
    fit_params : dict[str, float]
        The fitted parameters, including the background parameters.
    x_reduced : np.ndarray
        The x values for the background line, typically the two end points.
    dataset_kwargs : dict[str, Any]
        The keyword arguments for the Dataset creation.

    Returns
    -------
    dict[str, Any]
        The plot item for the background.
    """
    _bg_poly = [fit_params["background_p0"]]
    if "background_p1" in fit_params:
        _bg_poly.insert(0, fit_params["background_p1"])
    _bg = Dataset(
        np.polyval(_bg_poly, x_reduced),
        **(dataset_kwargs | {"axis_ranges": [x_reduced]}),
    )
    return {"plot": 0, "label": "background", "data": _bg, "linestyle": "--"}


def _create_fit_details(
    fitter: type[FitFuncBase],
    data: Dataset,
    data_x: np.ndarray,
    fit_params: dict[str, float],
    start_fit_params: tuple[float, ...],
    metadata: dict[str, Any],
    has_background: bool,
) -> dict[str, Any]:
    """
    Create the detailed results dictionary for a successful fit.

    Parameters
    ----------
    fitter : type[FitFuncBase]
        The fit function.
    data : Dataset
        The (cropped) input data.
    data_x : np.ndarray
        The (cropped) x values of the data.
    fit_params : dict[str, float]
        The fitted parameters.
    start_fit_params : tuple[float, ...]
        The starting values of the fit parameters.
    metadata : dict[str, Any]
        The metadata of the fit results.
    has_background : bool
        Flag whether the fit includes a background.

    Returns
    -------
    dict[str, Any]
        The detailed results in the format expected by pydidas.
    """
    _x_fit = np.linspace(data_x[0], data_x[-1], num=(data_x.size - 1) * 10 + 1)
    _x_reduced = np.array([np.amin(_x_fit), np.amax(_x_fit)])
    _fit_param_vals = tuple(fit_params.values())
    _dset_kws = {
        "axis_ranges": [_x_fit],
        "axis_labels": data.axis_labels,
        "axis_units": data.axis_units,
        "data_unit": data.data_unit,
    }
    _fit_final = Dataset(fitter.profile(_fit_param_vals, _x_fit), **_dset_kws)
    _fit_start = Dataset(fitter.profile(start_fit_params, _x_fit), **_dset_kws)
    _bg_data = fitter.calculate_background(_fit_param_vals, data_x)
    _items = [
        {
            "plot": 0,
            "label": "input data",
            "data": data,
            "symbol": "o",
            "linewidth": 0,
        },
        {"plot": 0, "label": "fitted_data", "data": _fit_final, "linewidth": 2.5},
        {
            "plot": 1,
            "label": "input data",
            "data": data - _bg_data,
            "symbol": "o",
            "linewidth": 0,
        },
        *_create_individual_peak_items(fitter, _fit_param_vals, _x_fit, _dset_kws),
        {
            "plot": 2,
            "label": "reference",
            "data": Dataset([0, 0], axis_ranges=[_x_reduced]),
            "linestyle": "--",
        },
        {
            "plot": 2,
            "label": "residual",
            "data": fitter.delta(_fit_param_vals, data_x, data),
            "symbol": "o",
            "linewidth": 0,
        },
        {"plot": 3, "label": "input data", "data": data},
        {"plot": 3, "label": "starting guess", "data": _fit_start},
    ]
    if has_background:
        _items.append(_create_background_item(fit_params, _x_reduced, _dset_kws))
    return {
        "n_plots": 4,
        "plot_titles": {
            0: "data and fit",
            1: "individual fits",
            2: "residual",
            3: "starting guess",
        },
        "plot_ylabels": {
            0: "intensity / a.u.",
            1: "intensity (background-corrected) / a.u.",
            2: "intensity / a.u.",
            3: "intensity / a.u.",
        },
        "metadata": _format_fit_metadata(metadata),
        "items": _items,
    }


def create_invalid_peak_details(
    data: Dataset,
    data_x: np.ndarray,
    bg_corrected_data: Dataset,
    bg_params: tuple[float, ...],
) -> dict[str, Any]:
    """
    Create the detailed results dictionary for an invalid peak.

    Parameters
    ----------
    data : Dataset
        The (cropped) input data.
    data_x : np.ndarray
        The (cropped) x values of the data.
    bg_corrected_data : Dataset
        The background-corrected data.
    bg_params : tuple[float, ...]
        The estimated background parameters. An empty tuple means that no
        background was estimated.

    Returns
    -------
    dict[str, Any]
        The detailed results in the format expected by pydidas.
    """
    if len(bg_params) == 0:
        return {
            "n_plots": 1,
            "plot_titles": {0: "data"},
            "plot_ylabels": {0: "intensity / a.u."},
            "metadata": "",
            "items": [{"plot": 0, "label": "input data", "data": data}],
        }
    _bg = Dataset(np.zeros(data_x.size) + bg_params[0], **data.property_dict)
    if len(bg_params) == 2:
        _bg += data_x * bg_params[1]
    return {
        "n_plots": 2,
        "plot_titles": {0: "data and background", 1: "background-corrected data"},
        "plot_ylabels": {0: "intensity / a.u.", 1: "intensity / a.u."},
        "metadata": "",
        "items": [
            {
                "plot": 0,
                "label": "input data",
                "data": data,
                "linewidth": 0,
                "symbol": "o",
            },
            {"plot": 0, "label": "background", "data": _bg},
            {
                "plot": 1,
                "label": "background-corrected data",
                "data": bg_corrected_data,
            },
        ],
    }


class BaseFitPlugin(ProcPlugin):
    """
    Fit a single peak to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.
    """

    plugin_name = "Base fit plugin"
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = get_generic_param_collection(
        "process_data_dim",
        "fit_func",
        "fit_output",
        "fit_bg_order",
        "fit_lower_limit",
        "fit_upper_limit",
        "fit_use_latest_as_start_guess",
        "fit_move_range_with_results",
        "fit_sigma_threshold",
        "fit_min_peak_height",
    )
    input_data_dim = -1
    output_data_dim = -1
    num_peaks = 1
    new_dataset = True
    advanced_parameters: ClassVar[list[str]] = [
        "fit_use_latest_as_start_guess",
        "fit_move_range_with_results",
        "fit_sigma_threshold",
        "fit_min_peak_height",
    ]
    has_unique_parameter_config_widget = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._fitter = None
        self._data = None
        self._data_x = None
        self._details = {}
        self._run_data = {}
        self._fit_params = {}
        self._fit_presets = {}
        self.config.update(
            range_slice=None,
            settings_updated_from_data=False,
            data_x_hash=-1,
            indices=None,
        )

    @property
    def detailed_results(self) -> dict[str | None, dict[str, Any]]:
        """
        Get the detailed results for the FitSinglePeak plugin.

        Returns
        -------
        dict[str | None, dict[str, Any]]
            The dictionary with detailed results.
        """
        return self._details

    @property
    def fit_outputs(self) -> list[str]:
        """
        Get the selected outputs for the fit.

        Returns
        -------
        list[str]
            The list with the selected outputs.
        """
        return [item.strip() for item in self.get_param_value("fit_output").split(";")]

    def pre_execute(self) -> None:
        """Set up the required functions and fit variable labels."""
        self._fitter = FitFuncMeta.get_fitter(self.get_param_value("fit_func"))
        self._fit_params = {}
        self._fit_results = {}
        self.config.indices = None
        self.config.range_slice = None
        self.config.settings_updated_from_data = False
        self.config["min_peak_height"] = self.get_param_value("fit_min_peak_height")
        self.config["sigma_threshold"] = self.get_param_value("fit_sigma_threshold")
        self.config["result_shape"] = (self.num_peaks, len(self.fit_outputs))
        for _key in ["param_bounds_low", "param_bounds_high", "param_labels"]:
            self.config[_key] = getattr(self._fitter, _key).copy()
        _bg_order = self.get_param_value("fit_bg_order")
        self.output_data_label = self.get_param_value("fit_output")
        self.output_data_unit = ""
        if _bg_order in [0, 1]:
            self.config["param_labels"].append("background_p0")
            self.config.param_bounds_low.append(-np.inf)
            self.config.param_bounds_high.append(np.inf)
        if _bg_order == 1:
            self.config["param_labels"].append("background_p1")
            self.config.param_bounds_low.append(-np.inf)
            self.config.param_bounds_high.append(np.inf)
        self._update_fit_param_bounds()
        self._create_fit_start_param_dict()

    def execute(self, data: Dataset, **kwargs: Any) -> tuple[Dataset, dict[str, Any]]:
        """
        Fit a peak to the data.

        Note that the results includes the original data, the fitted data and
        the residual and that the fit Parameters are included in the kwarg
        metadata.

        Parameters
        ----------
        data : Dataset
            The input Dataset
        **kwargs : Any
            Any calling keyword arguments.

        Returns
        -------
        data : Dataset
            The fit results as a Dataset.
        kwargs : dict[str, Any]
            Any calling kwargs, appended by any changes in the function.
        """
        self._initialize_execution_run(data)
        _global_results = None
        _use_latest_start_guess = self.get_param_value("fit_use_latest_as_start_guess")
        for _slice_indices in self.config.indices:
            _curr_data = data[_slice_indices]
            self.prepare_input_data(_curr_data)
            _detail_identifier = (
                None
                if _slice_indices == slice(None)
                else data.get_description_of_point(_slice_indices)
            )
            if _use_latest_start_guess and _detail_identifier in self._fit_results:
                kwargs["start_guess"] = tuple(
                    self._fit_results[_detail_identifier].values()
                )
            _curr_results, _details, kwargs = self._fit_spectrum(**kwargs)
            if kwargs.get("store_details", False):
                self._details[_detail_identifier] = _details
            self._fit_results[_detail_identifier] = self._fit_params
            if self.config.dim_to_process is None:
                return _curr_results, kwargs
            if _global_results is None:
                _global_results = create_multi_dim_result_dataset(
                    self.config.dim_to_process, data, _curr_results
                )
            _output_indices = (
                _slice_indices[: self.config.dim_to_process]
                + (slice(None),) * _curr_results.ndim
                + _slice_indices[self.config.dim_to_process + 1 :]
            )
            _global_results[_output_indices] = _curr_results
        if self.get_param_value("fit_move_range_with_results"):
            self._update_fit_range_from_results()
        return _global_results, kwargs

    def _initialize_execution_run(self, data: Dataset) -> None:
        """
        Initialize the execution run for the current dataset.

        Parameters
        ----------
        data : Dataset
            The input Dataset.
        """
        self._details = {}
        if self.config.get("indices") is None:
            if data.ndim == 1:
                self.config.indices = (slice(None),)
                self.config.dim_to_process = None
                return
            self.config.dim_to_process = np.mod(
                self.get_param_value("process_data_dim"), data.ndim
            )
            _results_shape = remove_item_at_index_from_iterable(
                data.shape, self.config.dim_to_process
            )
            _indices_to_process = [np.arange(_s) for _s in _results_shape]
            self.config.indices = tuple(
                insert_item_in_tuple(_i, self.config.dim_to_process, slice(None))
                for _i in tuple(itertools.product(*_indices_to_process))
            )

    def _fit_spectrum(
        self, **kwargs: Any
    ) -> tuple[Dataset, dict[str | None, Any] | None, dict[str, Any]]:
        """
        Fit a spectrum to the data.

        Parameters
        ----------
        **kwargs : Any
            Any calling keyword arguments.

        Returns
        -------
        data : Dataset
            The fit results as a Dataset.
        details : dict[str | None, Any] | None
            The detailed results for the fit.
        kwargs : dict[str, Any]
            Any calling kwargs, appended by any changes in the function.
        """
        _store_details = kwargs.get("store_details", False)
        if not self._check_min_peak_height():
            _details = (
                self._create_details_for_invalid_peak() if _store_details else None
            )
            return self.create_result_dataset(valid=False), _details, kwargs
        if kwargs.get("start_guess") is not None:
            _startguess = kwargs.get("start_guess")
        else:
            _startguess = self._fitter.guess_fit_start_params(
                self._data_x,
                self._data,
                bg_order=self.get_param_value("fit_bg_order"),
                bounds=(self.config.param_bounds_low, self.config.param_bounds_high),
                **self._fit_presets,
            )
        _res = least_squares(
            self._fitter.delta,
            _startguess,
            args=(self._data_x, self._data.array),
            bounds=(self.config.param_bounds_low, self.config.param_bounds_high),
        )
        _res_c = self._fitter.sort_fitted_peaks_by_position(tuple(_res.x))
        self._fit_params = dict(zip(self.config["param_labels"], _res_c))
        kwargs = kwargs | {
            "fit_params": self._fit_params,
            "fit_func": self._fitter.name,
            "fitted_axis_label": self._data.axis_labels[0],
            "fitted_axis_unit": self._data.axis_units[0],
        }
        _results = self.create_result_dataset()
        _details = (
            self.create_detailed_results(_results, _startguess)
            if _store_details
            else None
        )
        return _results, _details, kwargs

    def create_result_dataset(self, valid: bool = True) -> Dataset:
        """
        Create new Dataset for detailed results from the original data and the fit.

        Note that this method does not update the new metadata with the fit
        parameters. The new dataset includes a second dimensions with entries
        for the raw data, the data fit and the residual.

        Parameters
        ----------
        valid : bool, optional
            Flag to confirm the results are valid. The default is True.

        Returns
        -------
        new_data : Dataset
            The new dataset with the output data as defined by the
            fit_output parameter.
        """
        _fit_results = np.full(self.config["result_shape"], np.nan)
        _residual = np.nan
        if valid and self._check_center_positions():
            _fit_pvals = tuple(self._fit_params.values())
            _fit_final = self._fitter.profile(_fit_pvals, self._data_x)
            _residual = abs(np.std(self._data - _fit_final) / np.mean(self._data))
            if _residual <= self.config["sigma_threshold"]:
                _fit_results = self._write_valid_results(_fit_results, _fit_final)
        if self.num_peaks == 1:
            _fit_results = _fit_results.squeeze(axis=0)
        _axis_labels = (["Peak number"] if self.num_peaks > 1 else []) + [
            "; ".join([f"{i}: {_key}" for i, _key in enumerate(self.fit_outputs)])
        ]
        _result_dataset = Dataset(
            _fit_results,
            data_label=self.output_data_label,
            data_unit="",
            axis_labels=_axis_labels,
            axis_units=[""] * _fit_results.ndim,
        )
        _result_dataset.metadata = self._data.metadata | {
            "fit_func": self._fitter.name,
            "fit_params": self._fit_params,
            "fit_residual_std": _residual,
            "fitted_axis_label": self._data.axis_labels[0],
            "fitted_axis_unit": self._data.axis_units[0],
        }
        return _result_dataset

    def prepare_input_data(self, data: Dataset) -> None:
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
        if not self.config.settings_updated_from_data:
            self._update_node_output_labels()
            self._update_peak_bounds_from_data()
            self.config.settings_updated_from_data = True

    def create_detailed_results(
        self, results: Dataset, start_fit_params: tuple[float, ...]
    ) -> dict[str, Any]:
        """
        Create the detailed results for a single fit.

        This method will return detailed information to display for the user.
        The return format is a dictionary with four keys:
        First, "n_plots" which determines the number of plots. Second,
        "plot_titles" gives a title for each subplot. Third, "plot_ylabels"
        gives a y-axis label for each subplot. Fourth, "items" provides a
        list with the different items to be plotted. Each list entry must be
        a dictionary with the following keys:

            "plot" : int
                Key to determine the plot number.
            "label" : str
                For the legend label.
            "data":  Dataset
                The actual data to be plotted.

        Parameters
        ----------
        results : Dataset
            The Dataset with the regular results.
        start_fit_params : tuple[float, ...]
            The list with the starting fit params.

        Returns
        -------
        dict[str, Any]
            The dictionary with the detailed results in the format
            expected by pydidas.
        """
        if self._data is None:
            raise ValueError("Cannot get detailed results without input data.")
        return _create_fit_details(
            self._fitter,
            self._data,
            self._data_x,
            self._fit_params,
            start_fit_params,
            results.metadata,
            self.get_param_value("fit_bg_order") is not None,
        )

    # raise TypeError("To do: Fix the start fit estimation for multiple peaks for Gauss / Lorentzian. Implement dynamic fitting ranges.")

    def get_parameter_config_widget(self) -> type["GenericPluginConfigWidget"]:
        """
        Get the unique configuration widget class associated with this Plugin.

        Returns
        -------
        type[GenericPluginConfigWidget]
            The unique ParameterConfig widget class.
        """
        from pydidas.widgets.plugin_config_widgets import FitPluginConfigWidget

        return FitPluginConfigWidget

    def _check_center_positions(self) -> bool:
        """
        Check the fitted center position.

        Returns
        -------
        bool
            Flag whether all centers are in the input x range.
        """
        return {True} == {
            self._data_x[0] <= self._fit_params[_key] <= self._data_x[-1]
            for _key in self._fit_params
            if _key.startswith("center")
        }

    def _write_valid_results(
        self, results: np.ndarray, fit_y: np.ndarray
    ) -> np.ndarray:
        """
        Write the valid results for the fit in the new data array.

        Parameters
        ----------
        results : np.ndarray
            The new data array.
        fit_y : np.ndarray
            The y values of the fitted function for the input x values.

        Returns
        -------
        np.ndarray
            The new data array with the results.
        """
        _fit_pvals = tuple(self._fit_params.values())
        for _i, _key in enumerate(self.fit_outputs):
            if _key in ["position", "amplitude", "area", "FWHM"]:
                _attr = getattr(self._fitter, _key.lower())
                results[slice(None), _i] = _attr(_fit_pvals)
            elif _key == "total count intensity":
                _dx = self._data.axis_ranges[0][1] - self._data.axis_ranges[0][0]
                results[slice(None), _i] = [
                    a / _dx for a in self._fitter.area(_fit_pvals)
                ]
            elif _key == "background at peak":
                results[slice(None), _i] = self._fitter.background_at_peak(_fit_pvals)
            elif _key == "reduced chi^2":
                _norm = np.sum(self._data)
                if _norm == 0:
                    results[slice(None), _i] = np.nan
                    continue
                _chi2 = np.sum((self._data - fit_y) ** 2) / _norm / len(_fit_pvals)
                results[slice(None), _i] = _chi2
            elif _key == "relative sigma / (sigma + gamma)":
                results[slice(None), _i] = self._fitter.relative_sigma(_fit_pvals)
        return results

    def _crop_data_to_selected_range(self) -> None:
        """Get the range specified by the limits and store the cropped data."""
        _x_hash = hash(self._data_x.tobytes())
        if _x_hash != self.config["data_x_hash"] or self.config.range_slice is None:
            self.config["data_x_hash"] = _x_hash
            _xlow = self.get_param_value("fit_lower_limit")
            _range_low = (
                np.where(self._data_x >= _xlow)[0]
                if _xlow is not None
                else np.arange(self._data_x.size)
            )
            _xhigh = self.get_param_value("fit_upper_limit")
            _range_high = (
                np.where(self._data_x <= _xhigh)[0]
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
            self.config.range_slice = slice(_range[0], _range[-1] + 1)
        self._data_x = self._data_x[self.config.range_slice]
        self._data = self._data[self.config.range_slice]

    def _update_node_output_labels(self) -> None:
        """Update the node output labels based on the settings and the input data."""
        _output = self.get_param_value("fit_output")
        self.output_data_unit = ""
        _output = _output.replace("position", f"position / {self._data.axis_units[0]}")
        _output = _output.replace("amplitude", "amplitude / cts")
        _output = _output.replace("area", f"area / (cts * {self._data.axis_units[0]})")
        _output = _output.replace("FWHM", f"FWHM / {self._data.axis_units[0]}")
        _output = _output.replace("background at peak", "background at peak / cts")
        _output = _output.replace(
            "total count intensity", "total count intensity / cts"
        )
        self.output_data_label = _output

    def _update_peak_bounds_from_data(self) -> None:
        """Update the bounds for the peaks' center from the data x ranges."""
        for _key in ["", "0", "1", "2", "3"]:
            _label = f"center{_key}"
            if _label not in self.config["param_labels"]:
                continue
            _index = self.config["param_labels"].index(_label)
            _xlow = np.amin(self._data_x)
            self.config.param_bounds_low[_index] = max(
                self.config.param_bounds_low[_index], _xlow
            )
            _xhigh = np.amax(self._data_x)
            self.config.param_bounds_high[_index] = min(
                self.config.param_bounds_high[_index], _xhigh
            )

    def _update_fit_range_from_results(self) -> None:
        """Update the fit range from the results of the last fit."""
        if None in (
            self.get_param_value("fit_upper_limit"),
            self.get_param_value("fit_lower_limit"),
        ):
            raise UserConfigError(
                "The fit range cannot be updated because the limits are not set."
            )
        if "delta_range" not in self.config:
            self.config.delta_range = self.get_param_value(
                "fit_upper_limit"
            ) - self.get_param_value("fit_lower_limit")
        _center_vals = []
        for _params in self._fit_results.values():
            _center_vals.extend(list(self._fitter.center(tuple(_params.values()))))
        _center = np.mean(_center_vals)
        _low = _center - self.config.delta_range / 2
        _high = _center + self.config.delta_range / 2
        self.set_param_value("fit_lower_limit", _low)
        self.set_param_value("fit_upper_limit", _high)
        self.config.range_slice = None

    def _update_fit_param_bounds(self) -> None:
        """Update the fitting bounds from Parameters."""
        for _key in self.params:
            if _key.startswith("fit_peak") and _key.endswith(("_xlow", "_xhigh")):
                _suffix = "low" if _key.endswith("_xlow") else "high"
                _index = _key[8 : -(len(_suffix) + 2)]
                _label = f"center{_index}"
                _index = self.config["param_labels"].index(_label)
                _value = self.get_param_value(_key)
                if _value is not None:
                    self.config[f"param_bounds_{_suffix}"][_index] = _value

    def _create_fit_start_param_dict(self) -> None:
        """Create a dictionary with preset fit starting values."""
        self._fit_presets = {}
        for _key in self.params:
            if _key.startswith("fit_peak") and _key.endswith("xstart"):
                _index = _key.removeprefix("fit_peak").removesuffix("xstart").strip("_")
                _val = self.get_param_value(_key)
                if _val is not None:
                    self._fit_presets[f"center{_index}_start"] = _val
            if _key.startswith("fit_peak") and _key.endswith("width"):
                _index = _key.removeprefix("fit_peak").removesuffix("width").strip("_")
                _val = self.get_param_value(_key)
                if _val is not None:
                    self._fit_presets[f"width{_index}_start"] = _val

    def _check_min_peak_height(self) -> bool:
        """
        Check the minimum peak height and return the flag whether it is okay.

        Returns
        -------
        bool
            Flag whether the input data has a sufficiently large peak.
        """
        _min_peak = self.config["min_peak_height"]
        if _min_peak is not None:
            _tmp_y, _bg_params = self._fitter.estimate_background_params(
                self._data_x, self._data, self.get_param_value("fit_bg_order")
            )
            self._run_data["bg_params"] = _bg_params
            self._run_data["bg_corrected_data"] = _tmp_y
            if np.amax(_tmp_y) < _min_peak:
                return False
        return True

    def _create_details_for_invalid_peak(self) -> dict[str, Any]:
        """
        Create the details for an invalid peak.

        Returns
        -------
        dict[str, Any]
            The invalid results.
        """
        return create_invalid_peak_details(
            self._data,
            self._data_x,
            self._run_data.get("bg_corrected_data", self._data),
            self._run_data.get("bg_params", ()),
        )


BaseFitPlugin.register_as_base_class()
