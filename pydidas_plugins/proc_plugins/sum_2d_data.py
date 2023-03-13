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
Module with the Sum2dData Plugin which can be used to sum over 2D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["Sum2dData"]


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import Dataset, get_generic_param_collection
from pydidas.plugins import ProcPlugin


class Sum2dData(ProcPlugin):
    """
    Sum up datapoints in a 2D dataset.
    """

    plugin_name = "Sum 2D data"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        "type_selection",
        "lower_limit_ax0",
        "upper_limit_ax0",
        "lower_limit_ax1",
        "upper_limit_ax1",
    )
    input_data_dim = 2
    output_data_dim = 0
    output_data_label = "data sum (2d)"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None

    def execute(self, data, **kwargs):
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
        sum : np.ndarray
            The data sum in form of an array of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        _selection = self._data[self._get_index_ranges()]
        _sum = np.sum(_selection)
        _new_data = Dataset(
            [_sum],
            axis_labels=["Data sum"],
            axis_units=[""],
            metadata=data.metadata,
            data_label=self.output_data_label,
            data_unit=self.output_data_unit,
        )
        return _new_data, kwargs

    def _get_index_ranges(self):
        """
        Get the indices for the selected data range.

        Parameters
        ----------
        axis : str
            The axis to be processed. Must be either "x" or "y".

        Returns
        -------
        slice
            The slice object to select the range from the input data.
        """
        _slices = []
        for _ax in [0, 1]:
            if self.get_param_value("type_selection") == "Indices":
                _low, _high = self._get_axis_range(_ax, 0, self._data.shape[_ax])
                _slices.append(slice(int(_low), int(_high) + 1))
            else:
                _x = self._data.axis_ranges[_ax]
                assert isinstance(_x, np.ndarray), (
                    "The data does not have a correct range and using the data range "
                    "for selection is only available using the indices."
                )
                _low, _high = self._get_axis_range(_ax, _x[0], _x[-1])
                _bounds = np.where((_x >= _low) & (_x <= _high))[0]
                if _bounds.size == 0:
                    _slices.append(slice(0, 0))
                else:
                    _slices.append(slice(_bounds[0], _bounds[-1] + 1))
        return tuple(_slices)

    def _get_axis_range(self, axis, default_low, default_high):
        """
        Get the range for the selected axis.

        Parameters
        ----------
        axis : int
            The axis numbe.
        default_low : float
            The default value in case the lower limit is None.
        default_high : float
            The default value in case the lower limit is None.

        Returns
        -------
        tuple
            The axis bounds
        """
        _low = (
            self.get_param_value(f"lower_limit_ax{axis}")
            if self.get_param_value(f"lower_limit_ax{axis}") is not None
            else default_low
        )
        _high = (
            self.get_param_value(f"upper_limit_ax{axis}")
            if self.get_param_value(f"upper_limit_ax{axis}") is not None
            else default_high
        )
        return (_low, _high)

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        self._config["result_shape"] = (1,)
