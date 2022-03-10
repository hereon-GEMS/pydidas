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
__all__ = ['Hdf5singleFileLoader']


from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import InputPlugin
from pydidas.image_io import read_image
from pydidas.core.utils import copy_docstring, get_hdf5_metadata


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
        get_generic_parameter('hdf5_key'),
        get_generic_parameter('images_per_file'))
    input_data_dim = None
    output_data_dim = 2

    def __init__(self):
        super().__init__()

    def pre_execute(self):
        """
        Prepare loading of images from a single hdf5 file.
        """
        self._image_metadata.update()
        if self.get_param_value('images_per_file') == -1:
            self.__update_images_per_file()

    def __update_images_per_file(self):
        """
        Update the number of images per file.

        This method reads the first file of the list, extracts the number
        of frames in this dataset and stores the information.
        """
        _n_per_file = get_hdf5_metadata(
            self.get_param_value('filename'), 'shape',
            dset=self.get_param_value('hdf5_key'))[0]
        self.set_param_value('images_per_file', _n_per_file)

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
