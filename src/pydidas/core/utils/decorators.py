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
The decorator module has useful decorators to facilitate coding.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["copy_docstring", "process_1d_with_multi_input_dims"]


import functools
import itertools
from typing import Callable, Tuple

import numpy as np

from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import UserConfigError
from pydidas.core.utils.iterable_utils import (
    insert_item_in_tuple,
    insert_items_in_tuple,
    remove_item_at_index_from_iterable,
)


def copy_docstring(origin: type) -> type:
    """
    Initialize the docstring from another source.

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
            origin = getattr(origin, dest.__name__, None)
            if origin is None:
                raise ValueError("Origin class has no method called {dest.__name__}")

        dest.__doc__ = origin.__doc__
        return dest

    return functools.partial(_docstring, origin=origin)


def process_1d_with_multi_input_dims(method: Callable) -> Callable:
    """
    Decorator to run processing of 1-dim input with multi-dimensional inputs which are
    (except for the dimension to be processed) additional dimensions which are to be
    kept.
    """

    @functools.wraps(method)
    def _implementation(self, data: Dataset, **kwargs: dict) -> Tuple[Dataset, dict]:
        """
        Implement the multi-dimensional input decorator.

        This decorator updates the original execute method in the pydidas Plugin.

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
        _process_details = kwargs.get("store_details", False) and hasattr(
            self, "_details"
        )
        _details = {}
        _dim_to_process = np.mod(self.get_param_value("process_data_dim"), data.ndim)
        _results_shape = remove_item_at_index_from_iterable(data.shape, _dim_to_process)
        _indices = [np.arange(_s) for _s in _results_shape]
        if np.prod(_results_shape) > 500:
            raise UserConfigError(
                "The requested operation includes too many function calls. "
                "For performance reasons, the maximum number of function calls is "
                "limited to 500. Please check your workflow."
            )
        for _params in itertools.product(*_indices):
            _input = data[insert_item_in_tuple(_params, _dim_to_process, slice(None))]
            _single_result, _new_kws = method(self, _input, **kwargs)
            if _results is None:
                _results = _create_result_dataset(_dim_to_process, data, _single_result)
            if _process_details:
                _point = insert_item_in_tuple(_params, _dim_to_process, None)
                _detail_identifier = data.get_description_of_point(_point)
                _details[_detail_identifier] = self._details.pop(None)
            _output_slices = insert_items_in_tuple(
                _params, _dim_to_process, *(_single_result.ndim * (slice(None),))
            )
            _results[_output_slices] = _single_result
        # if _results.shape[_dim_to_process] == 1:
        #     _results = _results.squeeze(_dim_to_process)
        if _process_details:
            self._details = _details
        return _results, _new_kws

    _implementation.__doc__ = method.__doc__
    return _implementation


def _create_result_dataset(
    dim_to_process: int, input: Dataset, result: Dataset
) -> Dataset:
    """
    Create a result dataset.

    Parameters
    ----------
    dim_to_process : int
        The dimension to process
    input : Dataset
        The input data.
    result : Dataset
        The result data.

    Returns
    -------
    Dataset
        The result dataset.
    """
    _results_shape = insert_items_in_tuple(
        remove_item_at_index_from_iterable(input.shape, dim_to_process),
        dim_to_process,
        *result.shape,
    )
    _results = Dataset(
        np.zeros(_results_shape),
        data_unit=result.data_unit,
        data_label=result.data_label,
        metadata=result.metadata,
    )
    for _prop in ["axis_labels", "axis_units", "axis_ranges"]:
        _val = list(getattr(input, _prop).values())
        _val = (
            _val[:dim_to_process]
            + list(getattr(result, _prop).values())
            + _val[dim_to_process + 1 :]
        )
        setattr(_results, _prop, _val)
    return _results
