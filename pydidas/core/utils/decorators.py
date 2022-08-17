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
The decorator module has useful decorators to facilitate coding.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "copy_docstring",
    "process_1d_with_multi_input_dims",
    "calculate_result_shape_for_multi_input_dims",
]

import functools
import itertools

import numpy as np

from ..dataset import Dataset


def copy_docstring(origin):
    """
    Decorator to initialize the docstring from another source.

    This is useful to duplicate a docstring for inheritance and composition.

    If origin is a method or a function, it copies its docstring.
    If origin is a class, the docstring is copied from the method
    of that class which has the same name as the method/function
    being decorated.

    Parameters
    ----------
    origin : object
        The origin object with the docstring.

    Raises
    ------
    ValueError
        If the origin class does not have the method with the same name.
    """

    def _docstring(dest, origin):
        if not isinstance(dest, type) and isinstance(origin, type):
            try:
                origin = getattr(origin, dest.__name__)
            except AttributeError:
                raise ValueError(
                    "Origin class has no method called " f"{dest.__name__}"
                )

        dest.__doc__ = origin.__doc__
        return dest

    return functools.partial(_docstring, origin=origin)


def process_1d_with_multi_input_dims(method):
    """
    Decorator to run processing of 1-dim input with multi-dimensional inputs which are
    (except for the dimension to be processed) additional dimensions which are to be
    kept.
    """

    @functools.wraps(method)
    def _implementation(self, data, **kwargs):
        """
        Implementation of the multi-dimensional input decorator which updates the
        original execute method in the pydidas Plugin.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input data
        **kwargs : dict
            Any input

        Returns
        -------
        pydidas.core.Dataset
            The result dataset.
        """
        if data.ndim == 1:
            return method(self, data, **kwargs)
        _results = None
        _dim_to_process = np.mod(self.get_param_value("process_data_dim"), data.ndim)
        _datasize = data.shape[_dim_to_process]
        _dataslice = slice(0, _datasize)
        _res_shape = list(data.shape)
        del _res_shape[_dim_to_process]
        _indices = [np.arange(_s) for _s in _res_shape]
        for _params in itertools.product(*_indices):
            _input_slices = list(_params)
            _input_slices.insert(_dim_to_process, _dataslice)
            _input_slices = tuple(_input_slices)
            _single_result, _new_kws = method(self, data[_input_slices], **kwargs)
            if _results is None:
                _res_shape.insert(_dim_to_process, _single_result.size)
                _results = Dataset(
                    np.zeros(_res_shape),
                    data_unit=_single_result.data_unit,
                    data_label=_single_result.data_label,
                )
                for _prop in ["axis_labels", "axis_units", "axis_ranges"]:
                    _tmp = list(getattr(data, _prop).values())
                    del _tmp[_dim_to_process]
                    _tmp.insert(_dim_to_process, getattr(_single_result, _prop).get(0))
                    setattr(_results, _prop, _tmp)
            _output_slices = list(_params)
            _output_slices.insert(_dim_to_process, slice(0, _single_result.size))
            _output_slices = tuple(_output_slices)
            _results[_output_slices] = _single_result
        if _results.shape[_dim_to_process] == 1:
            _results = _results.squeeze(_dim_to_process)
        return _results, _new_kws

    _implementation.__doc__ = method.__doc__
    return _implementation


def calculate_result_shape_for_multi_input_dims(method):
    """
    Decorator to update the result shape for multiple input dimensions.
    """

    @functools.wraps(method)
    def _implementation(self):
        """
        Implementation of the calculate_result_shape for multi-dimensional input
        decorator which updates the original calculate_result_shape method in the
        pydidas Plugin.

        Returns
        -------
        tuple
            The resulting result shape.
        """
        method(self)
        if self._config["input_shape"] is None:
            return
        _input_ndim = len(self._config["input_shape"])
        if _input_ndim <= 1:
            return
        _dim_to_process = np.mod(self.get_param_value("process_data_dim"), _input_ndim)
        _shape = list(self._config["input_shape"])
        del _shape[_dim_to_process]
        if self._config["result_shape"] == (1,):
            self._config["result_shape"] = tuple(_shape)
        else:
            self._config["result_shape"] = tuple(
                _shape[:_dim_to_process]
                + list(self._config["result_shape"])
                + _shape[_dim_to_process:]
            )

    _implementation.__doc__ = method.__doc__
    return _implementation
