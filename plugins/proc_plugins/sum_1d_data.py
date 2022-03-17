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
Module with the Sum1dData Plugin which can be used to sum over 1D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Sum1dData']


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import ParameterCollection, Parameter, get_generic_parameter
from pydidas.plugins import ProcPlugin


class Sum1dData(ProcPlugin):
    """
    Sum up datapoints in a 1D dataset.
    """
    plugin_name = 'Sum 1D data'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('type_selection'),
        Parameter(
            'lower_limit', float, 0, name='Lower limit',
            tooltip=('The lower limit of data selection. This point is '
                     'included in the data. Note that the selection is either '
                     'in indices or data range, depending on the value of '
                     '"type_selection".')),
        Parameter(
            'upper_limit', float, 0, name='Upper limit',
            tooltip=('The upper limit of data selection. This point is'
                     ' included in the data. Note that the selection is either '
                     'in indices or data range, depending on the value of '
                     '"type_selection".')))
    input_data_dim = 1
    output_data_dim = 0

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
        _selection = self._data[self._get_index_range()]
        if _selection.size == 0:
            return np.array([0]), kwargs
        return np.array([np.sum(_selection)]), kwargs

    def _get_index_range(self):
        """
        Get the indices for the selected data range.

        Returns
        -------
        slice
            The slice object to select the range from the input data.
        """
        _low = self.get_param_value('lower_limit')
        _high = self.get_param_value('upper_limit')
        if self.get_param_value('type_selection') == 'Indices':
            return slice(int(_low), int(_high) + 1)
        _x = self._data.axis_ranges[0]
        assert isinstance(_x, np.ndarray), (
            'The data does not have a correct range and using the data range '
            'for selection is only available using the indices.')
        _bounds = np.where((_x >= _low) & (_x <= _high))[0]
        if _bounds.size == 0:
            return slice(0, 0)
        elif _bounds.size == 1:
            return slice(_bounds[0], _bounds[0] + 1)
        return slice(_bounds[0], _bounds[-1] + 1)
