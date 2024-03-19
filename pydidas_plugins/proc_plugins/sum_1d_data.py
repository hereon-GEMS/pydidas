# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Sum1dData"]


import numpy as np

from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN
from pydidas.core.utils import (
    calculate_result_shape_for_multi_input_dims,
    process_1d_with_multi_input_dims,
)
from pydidas.plugins import ProcPlugin


class Sum1dData(ProcPlugin):
    """
    Sum up data points in a 1D dataset.

    This plugin sums up the data values of the selected data points.
    Summation limits are defined using the 'lower_limit' and 'upper_limit'
    parameters in the plugin.

    Higher-dimensional datasets can also be processed. The 'process_data_dim'
    parameter determines which dimension to sum over. The other dimensions
    are being kept. For example, in a 3-dimensional dataset, summing over
    axis 1 would yield a 2-dimensional datasets with the original dimensions
    0 and 2 kept in place. This example would be equivalent to
    numpy.sum(dataset, axis=1).
    """

    plugin_name = "Sum 1D data"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        "process_data_dim",
        "type_selection",
        "lower_limit",
        "upper_limit",
    )
    input_data_dim = -1
    output_data_dim = 0
    output_data_label = "data sum (1d)"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config["slice"] = None

    def pre_execute(self):
        """
        Reset the index range slices before starting a new processing run.
        """
        self._config["slice"] = None

    @process_1d_with_multi_input_dims
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
        sum : Dataset
            The data sum in form of a Dataset of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        _selection = self._data[self._get_slice()]
        _sum = np.sum(_selection)
        _new_data = Dataset(
            [_sum],
            axis_labels=["Data sum"],
            axis_units=[""],
            metadata=data.metadata,
            data_label="data sum",
            data_unit=data.data_unit,
        )
        return _new_data, kwargs

    def _get_slice(self) -> slice:
        """
        Get the indices for the selected data range.

        Returns
        -------
        slice
            The slice object to select the range from the input data.
        """
        if self._config["slice"] is not None:
            return self._config["slice"]
        if self.get_param_value("type_selection") == "Indices":
            _low = (
                self.get_param_value("lower_limit")
                if self.get_param_value("lower_limit") is not None
                else 0
            )
            _high = (
                self.get_param_value("upper_limit")
                if self.get_param_value("upper_limit") is not None
                else self._data.size
            )
            self._config["slice"] = slice(int(_low), int(_high) + 1)
        else:
            _x = self._data.axis_ranges[0]
            assert isinstance(_x, np.ndarray), (
                "The data does not have a correct range and using the data range "
                "for selection is only available using the indices."
            )
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
            _bounds = np.where((_x >= _low) & (_x <= _high))[0]
            if _bounds.size == 0:
                self._config["slice"] = slice(0, 0)
            elif _bounds.size == 1:
                self._config["slice"] = slice(_bounds[0], _bounds[0] + 1)
            else:
                self._config["slice"] = slice(_bounds[0], _bounds[-1] + 1)
        return self._config["slice"]

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        self._config["result_shape"] = (1,)
