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
The SinSquareChiAnalysis plugin combines all required tools for the analysis of
sin^2(chi) data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Deployment"
__all__ = ["SinSquareChiAnalysis"]

from numbers import Real
from typing import Any, Callable

import numpy as np
import scipy
from matplotlib import pyplot as plt
from qtpy import QtCore, QtWidgets

from pydidas_plugins.residual_stress_plugins.sin_2chi_grouping import Sin_2chiGrouping
from pydidas_plugins.residual_stress_plugins.sin_square_chi_grouping import (
    SinSquareChiGrouping,
)

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import (
    Dataset,
    ParameterCollection,
    get_generic_param_collection,
)
from pydidas.core.constants import (
    PROC_PLUGIN,
    PROC_PLUGIN_STRESS_STRAIN,
    PYDIDAS_COLORS,
)
from pydidas.core.utils.scattering_geometry import convert_integration_result
from pydidas.plugins import OutputPlugin, ProcPlugin
from pydidas.widgets.plugin_config_widgets import GenericPluginConfigWidget


_VALID_DATA_AXIS_1_LABELS = ("2theta", "d-spacing", "Q", "r")
_VALID_UNITS = ("nm", "A", "nm^-1", "A^-1", "deg", "rad", "mm")

_PARAM_KEY_ORDER = [
    "keep_results",
    "label",
    "output_type",
    "sin_square_chi_low_fit_limit",
    "sin_square_chi_high_fit_limit",
    "output_export_images_flag",
    "directory_path",
    "enable_overwrite",
    "output_fname_digits",
    "output_index_offset",
]
_COLORS = {
    "d_mean": PYDIDAS_COLORS["orange"],
    "d_pos": PYDIDAS_COLORS["cyan"],
    "d_neg": PYDIDAS_COLORS["cyan"],
    "lower fit limit": PYDIDAS_COLORS["gray"],
    "upper fit limit": PYDIDAS_COLORS["gray"],
    "fit": PYDIDAS_COLORS["blue"],
    "data vs sin(2*chi)": PYDIDAS_COLORS["orange"],
}


def _sin_2chi_fit_func(c, x):
    return c * x


def _filter_nan_from_1d_dataset(data: Dataset) -> tuple[np.ndarray, np.ndarray]:
    """
    Filter NaN values from a 1D dataset and return the filtered x and y values.

    Parameters
    ----------
    data : Dataset
        The input dataset to filter.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        The filtered x and y values.
    """
    _nan_filter = ~np.isnan(data).view(np.ndarray)
    data = data[_nan_filter]
    _x = data.axis_ranges[0]
    return _x, data


class SinSquareChiAnalysis(ProcPlugin, OutputPlugin):
    """
    Analyzes the d-spacing values of a dataset using the sin^2(chi) method.

    NOTE: This plugin uses approximations in the high-energy X-ray regime. Using
    chi instead of psi for the sin^2(psi) method is an approximation in the
    high-energy X-ray regime. Psi is the angle between the scattering vector Q
    and the sample normal. The geometry of the experiment requires that the sample
    normal is parallel to the z-axis, i.e. the incoming beam is parallel to the
    sample surface.

    This plugin is designed to work with datasets containing d-spacing values
    (or 2theta values) and chi values. It performs the following steps:

        1. (only if required) convert 2theta to the desired output type

        2. Group the values for chi positions with similar sin^2(chi) values

        3. Additionally, group the d-spacing values according to the slopes
           in sin(2*chi)

        4. Fit the grouped values with a linear function.

        The output array has the following elements:
        - [0]: slope of the sin^2(chi) fit
        - [1]: slope error
        - [2]: intercept of the sin^2(chi) fit
        - [3]: intercept error
        - [4]: slope of the sin(2*chi) fit
        - [5]: slope error

    Optionally, this plugin also allows exporting images of the fits for
    each data point.

    NOTE: This plugin currently only allows chi to be given in degrees.
    """

    plugin_name = "sin^2(chi) analysis"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = -1
    output_data_dim = 1
    new_dataset = True
    generic_params = OutputPlugin.generic_params.copy()
    default_params = get_generic_param_collection(
        "output_type",
        "sin_square_chi_low_fit_limit",
        "sin_square_chi_high_fit_limit",
        "output_export_images_flag",
    )
    has_unique_parameter_config_widget = True
    advanced_parameters = OutputPlugin.advanced_parameters + [
        "sin_square_chi_low_fit_limit",
        "sin_square_chi_high_fit_limit",
    ]

    def __init__(self, *args: tuple, **kwargs: Any) -> None:
        self._EXP = kwargs.pop("diffraction_exp", DiffractionExperimentContext())
        self._SCAN = kwargs.pop("scan", ScanContext())
        OutputPlugin.__init__(self, *args, **kwargs)
        self._plugin_group_in_sin_square_chi = SinSquareChiGrouping()
        self._plugin_group_in_sin_2_chi = Sin_2chiGrouping()
        self._converter: Callable | None = None
        # re-order the parameters to allow a better presentation in the GUI
        self.params = ParameterCollection(
            *(self.params[_key] for _key in _PARAM_KEY_ORDER)
        )
        self.params["keep_results"].update_value_and_choices(1, [1])
        self._fit_slice: slice | None = None
        self._details: dict = {}
        self._figure: plt.Figure | None = None

    @property
    def detailed_results(self) -> dict:
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
        Prepare the plugin for execution.
        """
        if self.get_param_value("output_export_images_flag"):
            OutputPlugin.pre_execute(self)
        self._config["flag_conversion_set_up"] = False
        self._config["flag_input_data_check"] = False
        self._converter = None
        self._details = {}
        self._figure = None
        self._fit_slice: slice | None = None
        _xlow = self.get_param_value("sin_square_chi_low_fit_limit")
        _xhigh = self.get_param_value("sin_square_chi_high_fit_limit")
        if _xlow >= _xhigh:
            self.raise_UserConfigError(
                "The lower limit must be smaller than the upper limit to fit the "
                "sin^2(chi) data."
            )

    def execute(self, data: Dataset, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Execute the plugin.

        Parameters
        ----------
        data : Dataset
            The input data to be processed.
        **kwargs : Any
            Any calling keyword arguments.

        Returns
        -------
        tuple[Dataset, dict]
            The processed data and additional information.
        """
        if not self._config["flag_input_data_check"]:
            self._check_input_data(data)
        _sin_square_chi_data, _sin_2chi_data = self._regroup_data_w_sin_chi(data)
        _fit_sin_square_res = self._fit_sin_square_chi_data(_sin_square_chi_data)
        _fit_sin_2chi_res = self._fit_sin_2chi_data(_sin_2chi_data)
        _results = Dataset(
            np.append(_fit_sin_square_res, _fit_sin_2chi_res),
            data_label=f"fitted coefficients ({_sin_square_chi_data.data_label})",
            data_unit=_sin_square_chi_data.data_unit,
            axis_labels=["Fitted parameters (see Plugin docstring)"],
            metadata={
                "point #0": "fitted sin^2(chi) slope",
                "point #1": "slope error",
                "point #2": "fitted intercept",
                "point #3": "intercept error",
                "point #4": "fitted sin(2*chi) slope",
                "point #5": "slope error",
            },
        )
        kwargs["sin_2chi_data"] = _sin_2chi_data
        kwargs["sin_square_chi_data"] = _sin_square_chi_data
        kwargs["sin_square_chi_analysis_fits"] = _results
        _flag_export = self.get_param_value(
            "output_export_images_flag"
        ) and not kwargs.get("test", False)
        if _flag_export or kwargs.get("store_details", False):
            self.create_detailed_results(
                _sin_square_chi_data,
                _sin_2chi_data,
                _fit_sin_square_res,
                _fit_sin_2chi_res,
            )
        if _flag_export:
            self._config["global_index"] = kwargs.get("global_index", None)
            self._write_results()
        return _results, kwargs

    def _regroup_data_w_sin_chi(self, data: Dataset) -> tuple[Dataset, Dataset]:
        """
        Regroup the data with sin^2(chi) and sin(2*chi).
        """
        _sin_square_chi_data, _ = self._plugin_group_in_sin_square_chi.execute(data)
        if not self._config["flag_conversion_set_up"]:
            self._set_up_converter(_sin_square_chi_data)
        _sin_square_chi_data = self._converter(
            _sin_square_chi_data,
            *self._config["converter_args"],
        )
        _sin_2chi_data, _ = self._plugin_group_in_sin_2_chi.execute(
            _sin_square_chi_data
        )
        return _sin_square_chi_data, _sin_2chi_data

    def _check_input_data(self, data: Dataset):
        """
        Run basic checks on the input data.

        This method checks the dimensionality and whether the input data
        can be understood as fitted data.

        Parameters
        ----------
        data : Dataset
            The input data to be checked.
        """
        if data.ndim != 2:
            self.raise_UserConfigError(
                "The input data must be two-dimensional array "
                "(from a FitSinglePeak plugin)."
            )
        if data.axis_labels[0] != "chi" or "position" not in data.data_label:
            self.raise_UserConfigError(
                "The data does not appear to be a valid 2D integration result. "
                "The first axis must be `chi` and the second axis must be either of "
                + ", ".join(f"`{_item}`" for _item in _VALID_DATA_AXIS_1_LABELS)
                + "."
            )
        self._config["flag_input_data_check"] = True

    def _set_up_converter(self, input_data: Dataset):
        """
        Set up the conversion method based on the input data.
        """
        if self.get_param_value("output_type") == "Same as input":
            self._converter = self._converter_identity
            self._config["converter_args"] = ()
            self.output_data_label = f"fitted coefficients ({input_data.data_label})"
            self.output_data_unit = input_data.data_unit
        else:
            _input_type = input_data.data_label + " / " + input_data.data_unit
            _output = self.get_param_value("output_type")
            self._converter = convert_integration_result
            self._config["converter_args"] = (
                _input_type,
                _output,
                self._EXP.xray_wavelength_in_m,
                self._EXP.detector_dist_in_m,
            )
            _data_label, self.output_data_unit = _output.split(" / ")
            self.output_data_label = f"fitted coefficients ({_data_label})"
        self._config["flag_conversion_set_up"] = True

    @staticmethod
    def _converter_identity(data: Dataset, *args: tuple) -> Dataset:
        """Identity conversion function."""
        return data

    def _fit_sin_square_chi_data(self, data: Dataset) -> np.ndarray[Real]:
        """
        Fit the sin^2(chi) data with a linear function.

        Parameters
        ----------
        data : Dataset
            The input data to be fitted. This data must be the output
            of the SinSquareChiGrouping plugin.

        Returns
        -------
        np.ndarray[Real, ...]
            The fitted parameters and their errors. The array elements are:

            [0]: slope
            [1]: slope error
            [2]: intercept
            [3]: intercept error
        """
        if self._fit_slice is None:
            self._calculate_fit_slice(data[2])
        _x, _y = _filter_nan_from_1d_dataset(data[2, self._fit_slice])
        if _y.size < 2:
            return np.array([np.nan, np.nan, np.nan, np.nan])
        # Note: np.polynomial.Polynomial.fit does not (as of 2.1.1) support
        # covariance matrix calculation, so we use np.polyfit instead.
        # TODO: check if this is still the case in future numpy releases
        if _y.size <= 4:
            _p = np.polyfit(_x, _y, 1)
            _p_errors = np.array((np.nan, np.nan))
        else:
            _p, _cov = np.polyfit(_x, _y, 1, cov=True)
            _p_errors = np.sqrt(np.diag(_cov))
        return np.vstack((_p, _p_errors)).T.reshape(-1)

    @staticmethod
    def _fit_sin_2chi_data(data: Dataset) -> np.ndarray[Real, Real]:
        """
        Fit the sin(2*chi) data with a linear function.

        The intercept is set to 0.

        Parameters
        ----------
        data : Dataset
            The input data to be fitted. This data must be the output
            of the Sin_2chiGrouping plugin.

        Returns
        -------
        np.ndarray[Real, Real]
            The fitted parameters and their errors. The array elements are:

            [0]: slope
            [1]: slope error
        """
        _x, _y = _filter_nan_from_1d_dataset(data[2])
        if _y.size == 0:
            return np.array([np.nan, np.nan])
        _popt, _pcov = scipy.optimize.curve_fit(_sin_2chi_fit_func, _x, _y)
        _perr = np.sqrt(np.diag(_pcov))
        return np.array([_popt[0], _perr[0]])

    def _calculate_fit_slice(self, data: Dataset) -> None:
        """
        Calculate the slice for the fit.
        """
        _x = data.axis_ranges[0]
        _xlow = self.get_param_value("sin_square_chi_low_fit_limit")
        _xhigh = self.get_param_value("sin_square_chi_high_fit_limit")
        _valid_indices = np.where((_x >= _xlow) & (_x <= _xhigh))[0]
        if _valid_indices.size == 0:
            self.raise_UserConfigError(
                "The fit limits crop the full data. Please adjust the limits."
            )
        self._fit_slice = slice(_valid_indices[0], _valid_indices[-1] + 1)

    def create_detailed_results(
        self,
        sin_square_chi_data: Dataset,
        sin_2chi_data: Dataset,
        fit_sin_square_res: np.ndarray,
        fit_sin_2chi_res: np.ndarray,
    ) -> None:
        """
        Create detailed results for inspection.

        Parameters
        ----------
        sin_square_chi_data : Dataset
            The input data for the sin^2(chi) analysis.
        sin_2chi_data : Dataset
            The input data for the sin(2*chi) analysis.
        fit_sin_square_res : np.ndarray[Real]
            The fitted parameters and their errors for the sin^2(chi) analysis.
        fit_sin_2chi_res : np.ndarray[Real, Real]
            The fitted parameters and their errors for the sin(2*chi) analysis.
        """
        _sin_square_chi_pos = sin_square_chi_data[0]
        _sin_square_chi_neg = sin_square_chi_data[1]
        _sin_square_chi_mean = sin_square_chi_data[2]
        _sin_square_fit = Dataset(
            np.polyval([fit_sin_square_res[0], fit_sin_square_res[2]], [0, 1]),
            axis_ranges=[[0, 1]],
        )
        _abs_min = np.nanmin([np.nanmin(sin_square_chi_data), min(_sin_square_fit)])
        if np.isnan(_abs_min):
            _abs_min = -0.005
        _abs_max = np.nanmax([np.nanmax(sin_square_chi_data), max(_sin_square_fit)])
        if np.isnan(_abs_max):
            _abs_max = 0.005
        _delta = _abs_max - _abs_min
        self._plot0_bounds_minmax = (_abs_min - 0.05 * _delta, _abs_max + 0.05 * _delta)
        _low_lims = Dataset(
            self._plot0_bounds_minmax,
            axis_ranges=[2 * [self.get_param_value("sin_square_chi_low_fit_limit")]],
        )
        _high_lims = Dataset(
            self._plot0_bounds_minmax,
            axis_ranges=[2 * [self.get_param_value("sin_square_chi_high_fit_limit")]],
        )
        _sin_2chi_fit = Dataset(
            np.polyval([fit_sin_2chi_res[0], 0], [0, 1]),
            axis_ranges=[[0, 1]],
        )
        _abs_min1 = np.nanmin(np.append(sin_2chi_data[2], _sin_2chi_fit))
        if np.isnan(_abs_min1):
            _abs_min1 = -0.005
        _abs_max1 = np.nanmax(np.append(sin_2chi_data[2], _sin_2chi_fit))
        if np.isnan(_abs_max1):
            _abs_max1 = 0.005
        _delta1 = _abs_max1 - _abs_min1
        self._plot1_bounds_minmax = (
            _abs_min1 - 0.05 * _delta1,
            _abs_max1 + 0.05 * _delta1,
        )
        _details = {
            "n_plots": 2,
            "plot_titles": {0: "sin^2(chi)", 1: "sin(2*chi)"},
            "plot_ylabels": {
                0: sin_square_chi_data.data_description,
                1: sin_2chi_data.data_description,
            },
            "metadata": (
                "fitted slope of sin^2(chi):\n"
                + f"    {fit_sin_square_res[0]:.4e} +/- {fit_sin_square_res[1]:.4e}\n\n"
                + "fitted intercept of sin^2(chi):\n"
                + f"    {fit_sin_square_res[2]:.4e} +/- {fit_sin_square_res[3]:.4e}\n\n"
                + "fitted slope of sin(2*chi):\n"
                + f"    {fit_sin_2chi_res[0]:.4e} +/- {fit_sin_2chi_res[1]:.4e}"
            ),
            "items": [
                {
                    "plot": 0,
                    "label": "d_mean",
                    "data": _sin_square_chi_mean,
                    "symbol": "o",
                },
                {"plot": 0, "label": "fit", "data": _sin_square_fit},
                {
                    "plot": 0,
                    "label": "lower fit limit",
                    "data": _low_lims,
                    "linestyle": "--",
                },
                {
                    "plot": 0,
                    "label": "upper fit limit",
                    "data": _high_lims,
                    "linestyle": "--",
                },
                {
                    "plot": 0,
                    "label": "d_pos",
                    "data": _sin_square_chi_pos,
                    "symbol": "o",
                    "linestyle": "--",
                },
                {
                    "plot": 0,
                    "label": "d_neg",
                    "data": _sin_square_chi_neg,
                    "symbol": "o",
                    "linestyle": "--",
                },
                {"plot": 1, "label": "fit", "data": _sin_2chi_fit},
                {
                    "plot": 1,
                    "label": "data vs sin(2*chi)",
                    "data": sin_2chi_data[2],
                    "symbol": "o",
                    "linewidth": 0,
                },
            ],
        }
        self._details = {None: _details}

    def _write_results(self) -> None:
        """Write the results to the output file."""
        if self._figure is None:
            self.__set_up_figure()
        else:
            self._ax1.cla()
            self._ax2.cla()
        for _item in reversed(self._details[None]["items"]):
            _ax = self._ax1 if _item["plot"] == 0 else self._ax2
            _linestyle, _linewidth, _label = self.__get_plot_args(_item)
            _ax.plot(
                _item["data"].axis_ranges[0],
                _item["data"],
                label=_label,
                linewidth=_linewidth,
                linestyle=_linestyle,
                marker=_item.get("symbol", ""),
                color=_COLORS[_item["label"]],
                markersize=8,
            )
        # highlight the fitted data points-.
        _data = self._details[None]["items"][0]["data"][self._fit_slice]
        self._ax1.plot(
            _data.axis_ranges[0],
            _data.array,
            label="fitted data points",
            linewidth=0,
            marker="o",
            markersize=18,
            markeredgecolor=PYDIDAS_COLORS["orange"],
            markeredgewidth=3,
            markerfacecolor="none",
        )
        self._ax1.legend(
            loc="upper right",
            ncols=2,
            numpoints=3,
            markerscale=0.75,
            labelspacing=0.6,
            handlelength=5,
            handleheight=1.8,
        )
        _indices = self._SCAN.get_index_position_in_scan(self._config["global_index"])
        self._figure.suptitle(
            f"Sin^2(chi) analysis for scan point #{self._config['global_index']} "
            + "\n(position in scan:"
            + " / ".join(str(i) for i in _indices)
            + ")"
        )
        _bound_high = (
            self._plot0_bounds_minmax[1] + 0.15 * np.diff(self._plot0_bounds_minmax)[0]
        )
        self._ax1.set_xlim([-0.02, 1.02])
        self._ax2.set_xlim([-0.02, 1.02])
        self._ax1.set_ylim([self._plot0_bounds_minmax[0], _bound_high])
        self._ax2.set_ylim(self._plot1_bounds_minmax)
        self._ax1.set_title(self._plot_config["title_0"])
        self._ax2.set_title(self._plot_config["title_1"])
        self._ax1.set_xlabel(self._plot_config["label_x0"])
        self._ax2.set_xlabel(self._plot_config["label_x1"])
        self._ax1.set_ylabel(self._plot_config["label_y0"])
        self._ax2.set_ylabel(self._plot_config["label_y1"])
        _fname = self.get_output_filename("png")
        self._figure.savefig(_fname)

    def __set_up_figure(self):
        """Set up the figure for plotting."""
        _plot_items = self._details[None]["items"]
        self._figure = plt.Figure(figsize=(15, 8), dpi=125)
        self._ax1, self._ax2 = self._figure.subplots(1, 2)
        self._plot_config = {
            "x_0": _plot_items[0]["data"].axis_ranges[0],
            "x_1": _plot_items[-1]["data"].axis_ranges[0],
            "label_x0": _plot_items[0]["data"].get_axis_description(0),
            "label_x1": _plot_items[-1]["data"].get_axis_description(0),
            "label_y0": _plot_items[0]["data"].data_description,
            "label_y1": _plot_items[-1]["data"].data_description,
            "title_0": self._details[None]["plot_titles"][0],
            "title_1": self._details[None]["plot_titles"][1],
        }

    @staticmethod
    def __get_plot_args(item: dict[str, Any]) -> tuple[str, str, str | None]:
        """
        Get the plot arguments for the given item.

        Parameters
        ----------
        item : dict[str, Any]
            The item dictionary containing item information.

        Returns
        -------
        tuple[str, str, str | None]
            The linestyle, linewidth, and label for the plot.
        """
        _linestyle = "-" if item["label"] == "fit" else "--"
        _linewidth = item.get("linewidth", 3 if item["label"] == "fit" else 2)
        if _linewidth == 0:
            _linestyle = None
        match item["label"]:
            case "lower fit limit":
                _label = "fitted region limits"
            case "fit":
                _label = "linear fit"
            case "d_pos":
                _label = "pos. / neg. branch"
            case "d_mean":
                _label = "mean " + item["data"].data_label
            case "data vs sin(2*chi)":
                _label = "data points"
            case _:
                _label = None
        return _linestyle, _linewidth, _label

    def get_parameter_config_widget(self) -> QtWidgets.QWidget:
        """
        Get the unique configuration widget associated with this Plugin.

        Returns
        -------
        QtWidgets.QWidget
            The unique ParameterConfig widget
        """
        return _SinSquareChiAnalysisConfigWidget


class _SinSquareChiAnalysisConfigWidget(GenericPluginConfigWidget):
    def finalize_init(self):
        """Show/hide the output parameters based on user selection."""
        self._toggle_output_parameters()
        self.param_widgets["output_export_images_flag"].io_edited.connect(
            self._toggle_output_parameters
        )

    @QtCore.Slot(str)
    def _toggle_output_parameters(self, show_flag: str | None = None) -> None:
        """
        Show or hide the output parameters based on the user selection.

        Parameters
        ----------
        show_flag : str | None
            The value of the output type parameter. If None, the value is taken from
            the plugin parameter.
        """
        if show_flag is None:
            _show = self.plugin.get_param_value("output_export_images_flag")
        else:
            _show = show_flag in ["True", "1", True, 1]
        self.param_composite_widgets["directory_path"].setVisible(_show)
        self.param_composite_widgets["enable_overwrite"].setVisible(_show)
