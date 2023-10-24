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
Module with the Sum2dData Plugin which can be used to sum over 2D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Sum2dData"]


import numpy as np

from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN
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
        self._config["slices"] = None

    def pre_execute(self):
        """
        Reset the index range slices before starting a new processing run.
        """
        self._config["slices"] = None

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
        sum : np.ndarray
            The data sum in form of an array of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        return (
            Dataset(
                [np.sum(data[self._get_index_ranges()])],
                axis_labels=["Data sum"],
                axis_units=[""],
                metadata=data.metadata,
                data_label=self.output_data_label,
                data_unit=self.output_data_unit,
            ),
            kwargs,
        )

    def _get_index_ranges(self) -> tuple[slice, slice]:
        """
        Get the indices for the selected data range.

        Returns
        -------
        tuple[slice, slice]
            The slice object to select the range from the input data.
        """
        if self._config["slices"] is not None:
            return self._config["slices"]
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
        self._config["slices"] = tuple(_slices)
        return self._config["slices"]

    def _get_axis_range(
        self, axis: int, default_low: float, default_high: float
    ) -> tuple[float, float]:
        """
        Get the range for the selected axis.

        Parameters
        ----------
        axis : int
            The axis number.
        default_low : float
            The default value in case the lower limit is None.
        default_high : float
            The default value in case the lower limit is None.

        Returns
        -------
        tuple[float, float]
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
