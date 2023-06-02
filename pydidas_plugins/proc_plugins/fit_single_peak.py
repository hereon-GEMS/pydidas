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
Module with the FitSinglePeak Plugin which can be used to fit a single peak in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitSinglePeak"]


import numpy as np
from scipy.optimize import least_squares

from pydidas.core import Dataset
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.utils import (
    calculate_result_shape_for_multi_input_dims,
    process_1d_with_multi_input_dims,
)
from pydidas.plugins import BaseFitPlugin


class FitSinglePeak(BaseFitPlugin):
    """
    Fit a single peak to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.
    """

    plugin_name = "Fit single peak"
    basic_plugin = False

    def __init__(self, *args, **kwargs):
        BaseFitPlugin.__init__(self, *args, **kwargs)
        self.params["fit_func"].choices = FitFuncMeta.get_fitter_names_with_num_peaks(1)

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        BaseFitPlugin.pre_execute(self)

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
        self.prepare_input_data(data)
        if not self.check_min_peak_height():
            return self.create_result_dataset(valid=False), kwargs

        _startguess = self._fitter.guess_fit_start_params(
            self._data_x, self._data, self.get_param_value("fit_bg_order")
        )
        _res = least_squares(
            self._fitter.delta,
            _startguess,
            args=(self._data_x, self._data.array),
            bounds=(self._config["bounds_low"], self._config["bounds_high"]),
        )
        self._fit_params = dict(zip(self._config["param_labels"], _res.x))
        _results = self.create_result_dataset()
        kwargs = kwargs | {
            "fit_params": self._fit_params,
            "fit_func": self._fitter.function.__name__,
        }
        self._details = {None: self.create_detailed_results(_results, _startguess)}
        return _results, kwargs

    def create_result_dataset(self, valid=True):
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
        _output = self.get_param_value("fit_output")
        _residual = np.nan
        if valid and not (
            self._data_x[0] <= self._fit_params["center"] <= self._data_x[-1]
        ):
            valid = False
        if valid:
            _fit_pvals = list(self._fit_params.values())
            _datafit = self._fitter.function(_fit_pvals, self._data_x)
            _residual = abs(np.std(self._data - _datafit) / np.mean(self._data))
            _area = self._fitter.area(_fit_pvals)
            if _residual > self._config["sigma_threshold"]:
                _new_data = self._config["single_result_shape"][0] * [np.nan]
            else:
                _new_data = []
                if "position" in _output:
                    _new_data.append(self._fit_params["center"])
                if "area" in _output:
                    _new_data.append(_area)
                if "FWHM" in _output:
                    _new_data.append(self._fitter.fwhm(_fit_pvals))
        else:
            _new_data = self._config["single_result_shape"][0] * [np.nan]

        _axis_label = "; ".join(
            [f"{i}: {_key.strip()}" for i, _key in enumerate(_output.split(";"))]
        )
        _result_dataset = Dataset(
            _new_data,
            data_label=_output,
            data_unit=self._data.axis_units[0],
            axis_labels=[_axis_label],
            axis_units=[""],
        )
        _result_dataset.metadata = self._data.metadata | {
            "fit_func": self._fitter.func_name,
            "fit_params": self._fit_params,
            "fit_residual_std": _residual,
        }
        return _result_dataset

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        _output = self.get_param_value("fit_output")
        self.output_data_label = _output
        if _output in [
            "Peak area",
            "Peak position",
            "Peak FWHM",
        ]:
            self._config["result_shape"] = (1,)
        elif _output in [
            "Peak position; peak area",
            "Peak position; peak FWHM",
            "Peak area; peak FWHM",
        ]:
            self._config["result_shape"] = (2,)
        elif _output == "Peak position; peak area; peak FWHM":
            self._config["result_shape"] = (3,)
        else:
            raise ValueError("No result shape defined for the selected input")
        self._config["single_result_shape"] = self._config["result_shape"]
