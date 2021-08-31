# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5fileSeriesLoader']


from pathlib import Path

from pydidas.core import Parameter, ParameterCollection, get_generic_parameter
from pydidas.plugins import ProcPlugin, PROC_PLUGIN
from pydidas.image_io import read_image
from pydidas.apps.app_utils import FilelistManager


class MaskImage(ProcPlugin):
    """
    Load data frames from Hdf5 data files.

    This class is designed to load data from a single Hdf5 file. The
    """
    plugin_name = 'Mask image'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('live_processing'),
        get_generic_parameter('first_file'),
        get_generic_parameter('last_file'),
        get_generic_parameter('file_stepping'),
        get_generic_parameter('hdf5_key'),
        get_generic_parameter('images_per_file'),
        )
    input_data = None
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_manager = FilelistManager(
            self.params.get('first_file'),
            self.params.get('last_file'),
            self.params.get('live_processing'),
            self.params.get('file_stepping'))

    def execute(self, index, **kwargs):
        """
        Load a frame from a file.

        Parameters
        ----------
        index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._file_manager.update()
        _images_per_file = self.get_param_value('images_per_file')
        _i_file = index // _images_per_file
        _fname = self._file_manager.get_filename(_i_file)
        _hdf_index = index % _images_per_file
        kwargs['hdf5_dataset'] = self.get_param_value('hdf5_key')
        kwargs['frame'] = _hdf_index
        _data = read_image(_fname, **kwargs)
        return _data, kwargs
