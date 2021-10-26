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
__all__ = ['Hdf5fileSeriesLoader']


from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.image_io import read_image
from pydidas.apps.app_utils import FilelistManager
from pydidas.utils import copy_docstring, get_hdf5_metadata


class Hdf5fileSeriesLoader(InputPlugin):
    """
    Load data frames from Hdf5 data files.

    This class is designed to load data from a series of hdf5 file. The file
    series is defined through the first and last file and file stepping.
    The key to the hdf5 dataset needs to be provided as well as the number
    of images per file.
    Filesystem checks can be enabled using the live_processing keyword but
    are disabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    first_file : Union[str, pathlib.Path]
        The name of the first file in the file series.
    last_file : Union[str, pathlib.Path]
        The name of the last file in the file series.
    hdf5_key : str
        The key to access the hdf5 dataset in the file.
    images_per_file : int
        The number of images per file.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """
    plugin_name = 'HDF5 file series loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('first_file'),
        get_generic_parameter('last_file'),
        get_generic_parameter('hdf5_key'),
        get_generic_parameter('images_per_file'),
        get_generic_parameter('live_processing'),
        get_generic_parameter('file_stepping'),
        )
    input_data_dim = None
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_param_value('live_processing', True)
        self._file_manager = FilelistManager(
            self.get_param('first_file'),
            self.get_param('last_file'),
            self.get_param('live_processing'),
            self.get_param('file_stepping'))

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        self._file_manager.update()
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
            self.get_param_value('first_file'), 'shape',
            dset=self.get_param_value('hdf5_key'))[0]
        self.set_param_value('images_per_file', _n_per_file)

    def execute(self, index, **kwargs):
        """
        Load a frame from a file.

        Parameters
        ----------
        index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        _fname = self.get_filename(index)
        _hdf_index = index % self.get_param_value('images_per_file')
        kwargs['hdf5_dataset'] = self.get_param_value('hdf5_key')
        kwargs['frame'] = _hdf_index
        kwargs['binning'] = self.get_param_value('binning')
        kwargs['roi'] = self._image_metadata.roi
        _data = read_image(_fname, **kwargs)
        return _data, kwargs

    @copy_docstring(InputPlugin)
    def get_filename(self, index):
        """
        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        _images_per_file = self.get_param_value('images_per_file')
        _i_file = index // _images_per_file
        return self._file_manager.get_filename(_i_file)
