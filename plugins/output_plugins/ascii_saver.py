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
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AsciiSaver']

import numpy as np

from pydidas.core.constants import OUTPUT_PLUGIN
from pydidas.core import Dataset
from pydidas.plugins import OutputPlugin


class AsciiSaver(OutputPlugin):
    """
    An Ascii saver to export one-dimensional data

    This class is designed to store data passed down from other processing
    plugins into Ascii data.

    Parameters
    ----------
    label : str
        The prefix for saving the data.
    directory_path : Union[pathlib.Path, str]
        The output directory.
    """
    plugin_name = 'ASCII Saver'
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
        if data.ndim > 1:
            raise TypeError('Only 1-d data can be saved as ASCII')
        self._config['global_index'] = kwargs.get('global_index', None)
        _fname = self._get_output_filename()
        if not isinstance(data, Dataset):
            data = Dataset(data)
        if data.axis_ranges[0] is None:
            data.axis_ranges[0] = np.arange(data.size)
        with open(_fname, 'w') as _file:
            _file.write('# Metadata:\n')
            for _key, _val in data.metadata:
                _file.write(f'# {_key}: {_val}\n')
            _file.write('#\n')
            _file.write(f'# Axis label: {data.axis_labels[0]}\n')
            _file.write(f'# Axis unit: {data.axis_units[0]}\n')
            _file.write('# --- end of metadata ---\n')
            _file.write('# axis\tvalue\n')
            for _x, _y in zip(data.axis_ranges[0], data.array):
                _file.write(f'{_x}\t{_y}\n')
        return data, kwargs
