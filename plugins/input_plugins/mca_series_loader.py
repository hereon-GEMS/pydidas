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
Module with the FioMcaSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['FioMcaSeriesLoader']

import os

import numpy as np

from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core import (ParameterCollection, AppConfigError, Parameter,
                          get_generic_parameter, Dataset)
from pydidas.plugins import InputPlugin1d
from pydidas.core.utils import copy_docstring


class FioMcaSeriesLoader(InputPlugin1d):
    """
    Load data frames from a series of Fio files with MCA data.


    Parameters
    ----------
    directory_path : Union[str, pathlib.Path]
        The base path to the directory with all the scan subdirectories.
    filename_pattern : str
        The name and pattern of the sub-directories and the prefixes in the
        filename.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """
    plugin_name = 'Fio MCA series loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('directory_path'),
        get_generic_parameter('filename_pattern'),
        get_generic_parameter('first_index'),
        get_generic_parameter('live_processing'),
        get_generic_parameter('file_stepping'),
        Parameter('filename_suffix', str, '.fio', name='The filename pattern',
                  tooltip=('The pattern of the filename. Use a hash "#" for '
                           'the wildcard which will be substituted with '
                           'numbers.')),
        Parameter('files_per_directory', int, -1,
                  name='Files per directory',
                  tooltip=('The number of files in each directory. A value of '
                           '"-1" will take the number of present files in the '
                           'first directory.')),
        Parameter('use_absolute_energy', int, 0, choices=[True, False],
                  name='use absolute energy scale', 
                  tooltip=('Use an absolute energy scale for the results.')), 
        Parameter('energy_offset', float, 0, name='Energy offset', unit='eV',
                  tooltip=('The absolute offset in energy for the zeroth '
                          'channel.')), 
        Parameter('energy_delta', float, 1, name='Channel energy delta', 
                  unit='eV',
                  tooltip=('The width of each energy channels in eV.')), 
        )
    input_data_dim = None
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, use_filename_pattern=True, **kwargs)
        self.set_param_value('live_processing', False)
        self._filepath_generator = None
        self._filename_generator = None
        self.__pattern = None
        self._config.update({'header_lines': 0})

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        self.__check_files_per_directory()
        self.__create_filepath_generator()
        self.__create_filename_generator()
        self.__determine_header_size()
        self._config['energy_scale'] = None

    def __check_files_per_directory(self):
        """
        Check the number of files in each directory to compose the filename
        correctly.
        """
        if self.get_param_value('files_per_directory') == -1:
            _path = self.get_param_value('directory_path', dtype=str)
            _pattern = self.get_param_value('filename_pattern', dtype=str)
            _len_pattern =_pattern.count('#')
            _name = os.path.join(_path, _pattern).replace(
                '#' * _len_pattern, '{:0' + str(_len_pattern) + 'd}')
            _dirname = _name.format(self.get_param_value('first_index'))
            _files = os.listdir(_dirname)
            _nfiles = len(_files)
            self.set_param_value('files_per_directory', _nfiles)

    def __create_filepath_generator(self):
        """
        Set up the generator that can create the file paths to load
        MCA spectra.
        """
        _basepath = self.get_param_value('directory_path', dtype=str)
        _pattern = self.get_param_value('filename_pattern', dtype=str)
        _offset = self.get_param_value('first_index')
        _len_pattern =_pattern.count('#')
        if _len_pattern < 1:
            raise AppConfigError('No pattern detected!')
        _pattern = _pattern.replace('#' * _len_pattern,
                                    '{:0' + str(_len_pattern) + 'd}')
        self.__pattern = _pattern
        _path = os.path.join(_basepath, _pattern)
        self._filepath_generator = lambda index: _path.format(index + _offset)

    def __create_filename_generator(self):
        """
        Set up the generator that can create the file names to load
        MCA spectra.
        """
        _suffix = self.get_param_value('filename_suffix', dtype=str)
        _offset = self.get_param_value('first_index')
        _name = self.__pattern + '_mca_s' + '{:d}' + _suffix
        self._filename_generator = (
            lambda pathindex, fileindex: _name.format(pathindex + _offset, 
                                                      fileindex + 1))
        
    def __determine_header_size(self):
        """
        Determine the size of the header in lines.
        """
        _fname = self.get_filename(0)
        with open(_fname, 'r') as _f:
            _lines = _f.readlines()
        _n = 0
        while not _lines[0].startswith('! Data'):
            _lines.pop(0)
            _n += 1
        _n += 3
        self._config['header_lines'] = _n

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
            The dataset data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        _fname = self.get_filename(index)
        _data = np.loadtxt(_fname, skiprows=self._config['header_lines'])
        if self._config['energy_scale'] is None:
            self.__create_energy_scale(_data.size)
                    
        _dataset = Dataset(_data, axis_labels=['energy'],
                           axis_units=[self._config['energy_unit']],
                           axis_ranges=[self._config['energy_scale']])
        return _dataset, kwargs

    def __create_energy_scale(self, n):
        if not self.get_param_value('use_absolute_energy'):
            self._config['energy_unit'] = 'channels'
            self._config['energy_scale'] = np.arange(n)
            return
        self._config['energy_unit'] = 'eV'
        self._config['energy_scale'] = (
            np.arange(n) * self.get_param_value('energy_delta')
            + self.get_param_value('energy_offset'))
            
    @copy_docstring(InputPlugin1d)
    def get_filename(self, index):
        """
        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        _n_per_dir = self.get_param_value('files_per_directory')
        _pathindex = index // _n_per_dir
        _fileindex = index % _n_per_dir
        _path = self._filepath_generator(_pathindex)
        _name = self._filename_generator(_pathindex, _fileindex)
        return os.path.join(_path, _name)

    def get_raw_input_size(self):
        """
        Get the raw input size.

        Returns
        -------
        int
            The number of bins in the input data.
        """
        self.pre_execute()
        _data, _ = self.execute(0)
        return _data.size

    def get_first_file_size(self):
        """
        Get the size of the first file to be processed.

        Returns
        -------
        int
            The file size in bytes.
        """
        if self._filepath_generator is None:
            self.__create_filepath_generator()
        _fname = self._filepath_generator(
            self.get_param_value('first_index'))
        self._config['file_size'] = os.stat(_fname).st_size
        return self._config['file_size']
