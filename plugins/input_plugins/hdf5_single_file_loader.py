# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5singleFileLoader']


from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.image_io import read_image
from pydidas.utils import copy_docstring


class Hdf5singleFileLoader(InputPlugin):
    """
    Load data frames from Hdf5 data files.

    This class is designed to load data from a single Hdf5 file. The filename
    and dataset key must be specified.
    """
    plugin_name = 'HDF5 single file loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('filename'),
        get_generic_parameter('hdf5_key'))
    input_data_dim = None
    output_data_dim = 2

    def __init__(self):
        super().__init__()

    def execute(self, index, **kwargs):
        fname = self.get_param_value('filename')
        kwargs['hdf5_dataset'] = self.get_param_value('hdf5_key')
        kwargs['frame'] = index
        _data = read_image(fname, **kwargs)
        return _data, kwargs

    @copy_docstring(InputPlugin)
    def get_filename(self, index):
        """
        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        return self.get_param_value('filename')

    def get_result_shape(self):
        """
        Get the shape of the loaded file.

        Returns
        -------
        tuple
            The tuple with the image dimensions.
        """
        image, kwargs = self.execute(0)
        return image.shape
