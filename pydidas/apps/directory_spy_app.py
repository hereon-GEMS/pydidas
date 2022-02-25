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
Module with the BaseApp class from which all apps should inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseApp']

import os
import glob
import multiprocessing as mp

import numpy as np

from ..core import BaseApp, get_generic_param_collection, AppConfigError
from ..core.utils import (check_file_exists, check_hdf5_key_exists_in_file,
                          get_hdf5_metadata)
from ..core.constants import HDF5_EXTENSIONS
from ..image_io import read_image


class DirectorySpyApp(BaseApp):
    """
    The DirectorySpy is an App to scan a folder and load the latest image
    and keep it in shared memory. To run the app in the background, please
    refer to the :py:class:`pydidas.multiprocessing.AppRunner`.

    Parameters
    ----------
    *args : tuple
        Any number of Parameters. These will be added to the app's
        ParameterCollection.
    **kwargs : dict
        Parameters supplied with their reference key as dict key and the
        Parameter itself as value.
    """
    default_params = get_generic_param_collection(
        'scan_for_all', 'filename_pattern', 'hdf5_key', 'use_global_det_mask',
        'use_bg_file', 'bg_file', 'bg_hdf5_key', 'bg_hdf5_frame')
    parse_func = None
    attributes_not_to_copy_to_slave_app = ['_shared_arrays', '_index']

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._index = -1
        self._bg_image = None
        self._fname = lambda x: None
        self._path = None
        self.__current_image = None
        self.__current_fname = None
        self.reset_runtime_vars()
        self._det_mask = self._get_detector_mask()
        self._config['shared_memory'] = {}

    def reset_runtime_vars(self):
        """
        Reset the runtime variables for a new run.
        """
        self._shared_array = None
        self._index = -1
        self._config['det_mask_val'] = float(self.q_settings_get_global_value(
            'det_mask_val'))

    def _get_detector_mask(self):
        """
        Get the detector mask from the file specified in the global QSettings.

        Returns
        -------
        _mask : Union[None, np.ndarray]
            If the mask could be loaded from a numpy file, return the mask.
            Else, None is returned.
        """
        if not self.get_param_value('use_global_det_mask'):
            return None
        _maskfile = self.q_settings_get_global_value('det_mask')
        try:
            _mask = np.load(_maskfile)
            return _mask
        except (FileNotFoundError, ValueError):
            return None
        raise AppConfigError('Unknown error when reading detector mask file.')

    def _apply_mask(self, image):
        """
        Apply the detector mask to an image.

        Parameters
        ----------
        image : np.ndarray
            The image data.

        Returns
        -------
        image : np.ndarray
            The masked image data.
        """
        if self._det_mask is None:
            return image
        return np.where(self._det_mask,
                        self._config['det_mask_val'], image)

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()

    def prepare_run(self):
        """
        Prepare running the directory spy app.

        For the main App (i.e. running not in slave_mode), this involves the
        following steps:

            1. Get the shape of all results from the WorkflowTree and store
               them for internal reference.
            2. Get all multiprocessing tasks from the ScanSetup.
            3. Calculate the required buffer size and verify that the memory
               requirements are okay.
            4. Initialize the shared memory arrays.

        Both the slaved and the main applications then initialize local numpy
        arrays from the shared memory.
        """
        self.define_path_and_name()
        self.reset_runtime_vars()
        if self.get_param_value('use_bg_file'):
            self._load_bg_file()
        if not self.slave_mode:
            self.__initialize_shared_memory()
        self.__initialize_arrays_from_shared_memory()
        self.__redefine_mp_carryon()
        self.__find_current_index()

    def define_path_and_name(self):
        """
        Define the path and the name pattern to search for files.

        Raises
        ------
        AppConfigError
            If the naming pattern could not be interpreted.
        """
        self._path = os.path.dirname(self.get_param_value('filename_pattern'))
        if self.get_param_value('scan_for_all'):
            return
        _strs = self.get_param_value('filename_pattern').split('#')
        _lens = [len(_s) for _s in _strs]
        if len(_strs) == 1:
            raise AppConfigError(
                'No pattern detected in the filename. Please verify that '
                'the hashtag has been used.')
        if set(_lens[1:-1]) != {0}:
            raise AppConfigError(
                'Multiple patterns detected. Cannot process the filename '
                'pattern.')
        _prefix = _strs[0]
        _suffix = _strs[-1]
        _npattern = len(_strs) - 1
        _raw_str = (self._path + os.sep + _prefix
                    + '{index:0' + f'{_npattern}' + 'd}' + _suffix)
        self._config['glob_pattern'] = (self._path + os.sep + _prefix
                                        + '*' + _suffix)
        self._fname = lambda index: _raw_str.format(index=index)

    def _load_bg_file(self):
        """
        Check the selected background image file for consistency.

        The background image file is checked and if all checks pass, the
        background image is stored.

        Raises
        ------
        AppConfigError
            - If the selected background file does not exist
            - If the selected dataset key does not exist (in case of hdf5
              files)
            - If the  selected dataset number does not exist (in case of
              hdf5 files)
            - If the image dimensions for the background file differ from the
              image files.
        """
        _bg_file = self.get_param_value('bg_file')
        check_file_exists(_bg_file)
        if os.path.splitext(_bg_file)[1] in HDF5_EXTENSIONS:
            check_hdf5_key_exists_in_file(
                _bg_file, self.get_param_value('bg_hdf5_key'))
            _params = {'hdf5_dataset': self.get_param_value('bg_hdf5_key'),
                       'frame': self.get_param_value('bg_hdf5_frame')}
        _bg_image = read_image(_bg_file, **_params)
        self._bg_image = self.__apply_mask(_bg_image)

    def __initialize_shared_memory(self):
        """
        Initialize the shared memory arrays based on the buffer size and
        the result shapes.
        """
        _share = self._config['shared_memory']
        _share['flag'] = mp.Value('I', lock=mp.Lock())
        _share['width'] = mp.Value('I', lock=mp.Lock())
        _share['height'] = mp.Value('I', lock=mp.Lock())
        _share['array'] = mp.Array('f', 10000 * 10000, lock=mp.Lock())

    def __initialize_array_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        self._shared_array = np.frombuffer(
            self._config['shared_memory']['array'].get_obj(),
            dtype=np.float32).reshape((10000, 10000))

    def __redefine_mp_carryon(self):
        """
        Redefine the multiprocessing_carryon method based on the selection
        of the "scan for all" Parameter.

        The multiprocessing_carryon will scan the file system and store links
        to the latest files found.
        """
        if self.get_param_value('scan_for_all'):
            self.multiprocessing_carryon = self.__find_latest_file
        else:
            self.multiprocessing_carryon = self.__find_latest_file_of_pattern

    def __find_latest_file(self):
        """
        Find the file with the last timestamp in a directory.
        """
        _files = glob.glob(self._path + os.sep + '*')
        _files = [_f for _f in _files if os.path.isfile(_f)]
        _files.sort(key=os.path.getmtime)
        self._config['latest_file'] = (_files[-1] if len(_files) > 0 else None)
        self._config['2nd_latest_file'] = (_files[-2] if len(_files) >= 2
                                           else None)

    def __find_latest_file_of_pattern(self):
        """
        Find the latest file matching the defined file pattern.
        """
        while os.path.isfile(self._fname(self._index + 1)):
            self._index += 1
        self._config['latest_file'] = (self._fname(self._index)
                                       if self._index >= 0 else None)
        self._config['2nd_latest_file'] = (self._fname(self._index - 1)
                                           if self._index > 0 else None)

    def __find_current_index(self):
        """
        Find the current index of files matching the pattern.
        """
        _files = glob.glob(self._config['glob_pattern'])
        _index = self._config['glob_pattern'].find('*')
        _prefix = self.get_param_value('filename_pattern')[:_index]
        _suffix = self.get_param_value('filename_pattern')[_index + 1:]
        _files = [_f for _f in _files
                  if (os.path.isfile(_f) and _f.startswith(_prefix)
                      and _f.endswith(_suffix))]
        _files.sort()
        if len(_files) > 0:
            _index = _files[-1].removeprefix(_prefix).removesuffix(_suffix)
            self._index = _index

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """

    def multiprocessing_get_tasks(self):
        """
        The DirectorySpyApp does not use tasks and will always return an empty
        list.
        """
        return []

    def multiprocessing_pre_cycle(self, index):
        """
        Perform operations in the pre-cycle of every task.
        """
        return

    def multiprocessing_func(self, index):
        """
        Read the latest image. If the latest image cannot be read (e.g. the
        file is currently being written), the 2nd latest file will be read.

        Returns
        -------
        index : Union[int, None]
            The input index. This will generally be None.
        filename : str
            The full filename of the file being read
        """
        try:
            _fname = self._config['latest_file']
            _image = self.get_image(_fname)
        except FileNotFoundError:
            try:
                _fname = self._config['2nd_latest_file']
                _image = self.get_image(_fname)
            except FileNotFoundError:
                raise RuntimeError('Cannot read either of the last to files.')
        _image = self._apply_mask(_image)
        self.__store_image_in_shared_memory(_image)
        return index, _fname

    def get_image(self, fname):
        """
        Get an image from the given filename.

        In case of HDF5 files, the method will always return the last frame.

        Parameters
        ----------
        fname : str
            The filename (including full path) to the image file.

        Returns
        -------
        np.ndarray
            The image.
        """
        _params = {}
        if os.path.splitext(fname)[1] in HDF5_EXTENSIONS:
            _params.update(self.__get_hdf5_params(fname))
        return read_image(fname, **_params)

    def __get_hdf5_params(self, fname):
        """
        Get the parameters to read a frame from an HDF5 file.

        Parameters
        ----------
        fname : str
            The filename (including full path) to the HDF5 file.

        Returns
        -------
        dict
            The parameters required to read the frame from the given file.
        """
        _hdf5_dataset=self.get_param_value('hdf5_key')
        _shape = get_hdf5_metadata(fname, meta='shape', dset=_hdf5_dataset)
        return {'frame': _shape[0] - 1, 'hdf5_dataset': _hdf5_dataset}

    def __store_image_in_shared_memory(self, image):
        """
        Store the image data in the shared memory.

        Parameters
        ----------
        image : np.ndarray
            The image data
        """
        _flag_lock = self._config['shared_memory']['flag']
        with _flag_lock.get_lock():
            _width = image.shape[1]
            _height = image.shape[0]
            self._config['shared_memory']['width'].value = _width
            self._config['shared_memory']['height'].value = _height
            self._shared_array[:_width, :_height] = image

    def multiprocessing_carryon(self):
        """
        Wait for specific tasks to give the clear signal.

        This method will be re-implemented by the prepare_run method.

        Returns
        -------
        bool
            Flag whether processing can continue or should wait.
        """
        return True

    def multiprocessing_store_results(self, index, fname):
        """
        Store the multiprocessing results for other pydidas apps and processes.

        Parameters
        ----------
        index : int
            The frame index. This entry is kept for compatibility and not used
            in this app.
        fname : str
            The filename
        """
        _flag_lock = self._config['shared_memory']['flag']
        with _flag_lock.get_lock():
            _width = self._config['shared_memory']['width'].value
            _height = self._config['shared_memory']['height'].value
            self.__current_image = self._shared_array[:_width, :_height]
            self.__current_fname = fname

    @property
    def image(self):
        """
        Get the currently stored image.

        Returns
        -------
        np.ndarray
            The image data
        """
        return self.__current_image

    @property
    def filename(self):
        """
        Get the curently stored filename.

        Returns
        -------
        str
            The filename.
        """
        return self.__current_fname
