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
Module with the CropData Plugin which can be used to reduce the range of data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Crop1dData']


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import (ParameterCollection, Parameter,
                          get_generic_parameter)
from pydidas.plugins import ProcPlugin


class Crop1dData(ProcPlugin):
    """
    Crop a 1D dataset by specifying bounds, either indices or in the data
    range.
    """
    plugin_name = 'Crop 1D data'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('crop_type'),
        Parameter('crop_low', float, 0, name='Cropping lower boundary',
                  tooltip='The lower boundary for cropping.'),
        Parameter('crop_high', float, 0, name='Cropping upper boundary',
                  tooltip='The upper boundary for cropping.'))
    input_data_dim = 1
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """

    def execute(self, data, **kwargs):
        """
        Crop 1D data.

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
        self._data = data
        _bounds = self._get_index_range()
        _new_data = data[_bounds]
        return _new_data, kwargs

    def _get_index_range(self):
        """
        Get the indices for the selected data range.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input data

        Returns
        -------
        slice
            The slice object to select the range from the input data.
        """
        _low = self.get_param_value('crop_low')
        _high = self.get_param_value('crop_high')
        if self.get_param_value('crop_type') == 'Indices':
            return slice(int(_low), int(_high) + 1)
        _x = self._data.axis_ranges[0]
        assert isinstance(_x, np.ndarray), (
            'The data does not have a correct range and cropping is only '
            'available using the indices.')
        _bounds = np.where((_x >= _low) & (_x <= _high))[0]
        if _bounds.size == 0:
            return slice(0, 0)
        elif _bounds.size == 1:
            return slice(_bounds[0], _bounds[0] + 1)
        return slice(_bounds[0], _bounds[-1] + 1)
