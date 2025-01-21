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
Module with the Sum1dData Plugin which can be used to sum over 1D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Sum1dData"]


import numpy as np

from pydidas.core import Dataset, get_generic_param_collection
from pydidas.plugins import ProcPlugin


class Sum1dData(ProcPlugin):
    """
    Sum up data points in one dimensions dataset.

    This plugin sums up the data values of the selected data points.
    Summation limits are defined using the 'lower_limit' and 'upper_limit'
    parameters in the plugin. Data can be selected either by indices or by
    the data range. The 'type_selection' parameter determines the selection.

    Note that the value for the 'upper_limit' parameter is included in
    the summation.

    Higher-dimensional datasets can also be processed. The 'process_data_dim'
    parameter determines which dimension to sum over. The other dimensions
    are being kept. For example, in a 3-dimensional dataset, summing over
    axis 1 would yield a 2-dimensional datasets with the original dimensions
    0 and 2 kept in place. This example would be equivalent to
    numpy.sum(dataset, axis=1).
    """

    plugin_name = "Sum 1D data"
    default_params = get_generic_param_collection(
        "process_data_dim",
        "_process_data_dim",
        "type_selection",
        "lower_limit",
        "upper_limit",
    )

    input_data_dim = -1
    output_data_dim = -1
    output_data_label = "data sum (1d)"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None

    def pre_execute(self):
        """
        Reset the index range slices before starting a new processing run.
        """
        self._mask = None

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Sum data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _new_data : Dataset
            The data sum in form of a Dataset of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        _mask = self._get_mask()
        _new_data = np.sum(
            data, axis=self.get_param_value("_process_data_dim"), where=_mask
        )
        if not isinstance(_new_data, Dataset):
            _new_data = Dataset(
                [_new_data],
                axis_labels=["Data sum"],
                axis_units=[""],
                metadata=data.metadata,
                data_label="data sum",
                data_unit=data.data_unit,
            )
        return _new_data, kwargs

    def _get_mask(self) -> np.ndarray[bool]:
        """
        Get the mask to be used in the sum for the selected data range.

        Returns
        -------
        np.ndarray
            The array mask which indices to use in the sum.
        """
        if self._mask is not None:
            return self._mask
        _dim_to_sum = np.mod(self.get_param_value("process_data_dim"), self._data.ndim)
        self.set_param_value("_process_data_dim", _dim_to_sum)
        if self.get_param_value("type_selection") == "Indices":
            _x = np.arange(self._data.shape[_dim_to_sum])
        else:
            _x = self._data.axis_ranges[_dim_to_sum]
        _low = (
            self.get_param_value("lower_limit")
            if self.get_param_value("lower_limit") is not None
            else _x[0]
        )
        _high = (
            self.get_param_value("upper_limit")
            if self.get_param_value("upper_limit") is not None
            else _x[-1]
        )
        _sum_mask = np.where((_x >= _low) & (_x <= _high), 1, 0).astype(bool)
        _slicer = (
            [None] * _dim_to_sum
            + [slice(None)]
            + [None] * (self._data.ndim - _dim_to_sum - 1)
        )
        self._mask = np.ones(self._data.shape, dtype=bool) * _sum_mask[*_slicer]
        return self._mask
