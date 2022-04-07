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
Module with the ChiSaver Plugin which can be used to save 1d data in ASCII
format with a Chi header.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AsciiSaver']

import os

import numpy as np

from pydidas.core.constants import OUTPUT_PLUGIN
from pydidas.core import Dataset
from pydidas.plugins import OutputPlugin


class ChiSaver(OutputPlugin):
    """
    An Ascii saver to export one-dimensional data with a chi file header.

    This class is designed to store data passed down from other processing
    plugins into Ascii data.

    Parameters
    ----------
    label : str
        The prefix for saving the data.
    directory_path : Union[pathlib.Path, str]
        The output directory.
    """
    plugin_name = 'Chi Saver'
    basic_plugin = False
    plugin_type = OUTPUT_PLUGIN
    input_data_dim = 1
    output_data_dim = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, data, **kwargs):
        """
        Save data to file

        Parameters
        ----------
        Parameters
        ----------
        data : Union[np.ndarray, pydidas.core.Dataset]
            The data to be stored.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The input data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        print('type: ', type(data))
        if data.ndim > 1:
            raise TypeError('Only 1-d data can be saved as ASCII.')
        self._config['global_index'] = kwargs.get('global_index', None)
        _fname = self._get_base_output_filename() + '.chi'
        if not isinstance(data, Dataset):
            data = Dataset(data)
        if data.axis_ranges[0] is None:
            data.axis_ranges[0] = np.arange(data.size)
            data.axis_labels[0] = 'index'
        _title = os.path.basename(_fname) + '\n'
        _unit = data.axis_units[0]
        _axislabel = (str(data.axis_labels[0]) +
                      (f' ({_unit})\n' if _unit is not None and len(_unit) > 0
                      else '\n'))
        _dataunit = data.data_unit
        _datalabel = ('Intensity' +
                      (f' ({_dataunit})\n' if _dataunit is not None
                       and len(_dataunit) > 0 else '\n'))
        _npoints = f'\t{data.size}\n'
        with open(_fname, 'w') as _file:
            _file.write(_title)
            _file.write(_axislabel)
            _file.write(_datalabel)
            _file.write(_npoints)
            for _x, _y in zip(data.axis_ranges[0], data.array):
                _file.write(f'{_x:e}\t{_y:e}\n')
        return data, kwargs
