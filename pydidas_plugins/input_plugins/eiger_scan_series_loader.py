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
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['EigerScanSeriesLoader']

import os

from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core import (ParameterCollection, AppConfigError,
                          get_generic_parameter)
from pydidas.plugins import InputPlugin
from pydidas.image_io import read_image
from pydidas.core.utils import copy_docstring, get_hdf5_metadata


class EigerScanSeriesLoader(InputPlugin):
    """
    Load data frames from an Eiger scan series with files in different
    directories.

    This class is designed to load data from a series of directories with a
    single hdf5 file in each, as created by a series of scans with the Eiger
    detector.
    The key to the hdf5 dataset needs to be provided as well as the number
    of images per file. A value of -1 will have the class check for the number
    of images per file on its own.
    Filesystem checks can be enabled using the live_processing keyword but
    are disabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    directory_path : Union[str, pathlib.Path]
        The base path to the directory with all the scan subdirectories.
    filename_pattern : str
        The name and pattern of the sub-directories and the prefixes in the
        filename.
    eiger_key : str, optional
        The directory name created by the Eiger detector to store its data.
        The default is "eiger9m".
    filename_suffix : str, optional
        The suffix to be appended to the filename pattern (including extension)
        to make up the full filename. The default is "_data_00001.h5"
    first_index: int, optional
        The index of the first file to be processed. The default is 0.
    hdf5_key : str
        The key to access the hdf5 dataset in the file.

    images_per_file : int, optional
        The number of images per file. A value of -1 will make the class
        determine the number automatically based on the first file. The default
        is -1.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """
    plugin_name = 'Eiger scan series loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('directory_path'),
        get_generic_parameter('filename_pattern'),
        get_generic_parameter('eiger_key'),
        get_generic_parameter('filename_suffix'),
        get_generic_parameter('first_index'),
        get_generic_parameter('hdf5_key'),
        get_generic_parameter('images_per_file'),
        get_generic_parameter('live_processing'),
        get_generic_parameter('file_stepping'),
        )
    input_data_dim = None
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, use_filename_pattern=True, **kwargs)
        self.set_param_value('live_processing', False)
        self._filename_generator = None

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        self.__create_filename_generator()
        self.__update_image_metadata()
        if self.get_param_value('images_per_file') == -1:
            self.__update_images_per_file()

    def __create_filename_generator(self):
        """
        Set up the generator that can create the full file names to load
        images.
        """
        _basepath = self.get_param_value('directory_path', dtype=str)
        _pattern = self.get_param_value('filename_pattern', dtype=str)
        _eigerkey = self.get_param_value('eiger_key')
        _suffix = self.get_param_value('filename_suffix', dtype=str)
        _len_pattern =_pattern.count('#')
        if _len_pattern < 1:
            raise AppConfigError('No pattern detected!')
        _name = os.path.join(_basepath, _pattern, _eigerkey,
                             _pattern + _suffix)
        _fname = _name.replace('#' * _len_pattern,
                               '{:0' + str(_len_pattern) + 'd}')
        self._filename_generator = lambda index: _fname.format(index, index)

    def __update_image_metadata(self):
        """
        Update the image metadata, including updating the filename based on the
        input Parameters.
        """
        self.__create_filename_generator()
        _start_fname = self._filename_generator(
            self.get_param_value('first_index'))
        self._image_metadata.set_param_value('filename', _start_fname)
        self._image_metadata.update()


    def __update_images_per_file(self):
        """
        Update the number of images per file.

        This method reads the first file of the list, extracts the number
        of frames in this dataset and stores the information.
        """
        _n_per_file = get_hdf5_metadata(
            self.get_filename(0), 'shape',
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
        _i_file = (index // _images_per_file
                   + self.get_param_value('first_index'))
        return self._filename_generator(_i_file)

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self.__update_image_metadata()
        self._config['result_shape'] = self._image_metadata.final_shape
        self._original_input_shape = (self._image_metadata.raw_size_y,
                                      self._image_metadata.raw_size_x)

    def get_first_file_size(self):
        """
        Get the size of the first file to be processed.

        Returns
        -------
        int
            The file size in bytes.
        """
        if self._filename_generator is None:
            self.__create_filename_generator()
        _fname = self._filename_generator(
            self.get_param_value('first_index'))
        self._config['file_size'] = os.stat(_fname).st_size
        return self._config['file_size']
