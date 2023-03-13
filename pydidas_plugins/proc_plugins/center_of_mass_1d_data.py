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
Module with the CenterOfMass1dData Plugin which can be used to sum over 1D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["CenterOfMass1dData"]


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.utils import (
    process_1d_with_multi_input_dims,
    calculate_result_shape_for_multi_input_dims,
)
from pydidas.plugins import ProcPlugin


class CenterOfMass1dData(ProcPlugin):
    """
    Sum up datapoints in a 1D dataset.
    """

    plugin_name = "Center of mass 1d data"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection("process_data_dim")
    input_data_dim = -1
    output_data_dim = 0
    output_data_label = "Center of mass (1d)"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None

    @process_1d_with_multi_input_dims
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
        _x = data.axis_ranges[0]
        self.output_data_unit = data.axis_units[0]
        _com = np.sum(_x * data) / np.sum(data)
        _new_data = Dataset(
            [_com],
            axis_labels=["Data center of mass"],
            axis_units=[""],
            metadata=data.metadata,
            axis_label="Data center of mass",
            axis_unit=data.data_unit,
        )
        return _new_data, kwargs

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        self._config["result_shape"] = (1,)
