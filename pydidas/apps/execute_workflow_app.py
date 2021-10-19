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

"""Module with the ExecuteWorkflowApp class which allows to run workflows."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowApp']

import os
import time
import multiprocessing as mp

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.app_utils import FilelistManager, ImageMetadataManager
from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import (ParameterCollection, Dataset,
                          CompositeImage, get_generic_parameter, ScanSettings)
from pydidas.constants import HDF5_EXTENSIONS
from pydidas.utils import (check_file_exists, check_hdf5_key_exists_in_file)
from pydidas.image_io import read_image, rebin2d
from pydidas.utils import copy_docstring
from pydidas.apps.app_parsers import parse_composite_creator_cmdline_arguments
from pydidas.workflow_tree import WorkflowTree, WorkflowResults


TREE = WorkflowTree()

SCAN = ScanSettings()

RESULTS = WorkflowResults()

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('live_processing'),
    get_generic_parameter('first_file'),
    get_generic_parameter('last_file'),
    get_generic_parameter('file_stepping'),
    get_generic_parameter('hdf5_key'),
    get_generic_parameter('hdf5_first_image_num'),
    get_generic_parameter('hdf5_last_image_num'),
    get_generic_parameter('hdf5_stepping'),
    get_generic_parameter('use_bg_file'),
    get_generic_parameter('bg_file'),
    get_generic_parameter('bg_hdf5_key'),
    get_generic_parameter('bg_hdf5_frame'),
    get_generic_parameter('composite_nx'),
    get_generic_parameter('composite_ny'),
    get_generic_parameter('composite_dir'),
    get_generic_parameter('use_roi'),
    get_generic_parameter('roi_xlow'),
    get_generic_parameter('roi_xhigh'),
    get_generic_parameter('roi_ylow'),
    get_generic_parameter('roi_yhigh'),
    get_generic_parameter('use_thresholds'),
    get_generic_parameter('threshold_low'),
    get_generic_parameter('threshold_high'),
    get_generic_parameter('binning'),
    )


class ExecuteWorkflowApp(BaseApp):
    """
    Inherits from :py:class:`pydidas.apps.BaseApp<pydidas.apps.BaseApp>`

    The ExecuteWorkflowApp is used to run workflows which can be any operation
    which can be written as Plugin.

    Parameters can be passed either through the argparse module during
    command line calls or through keyword arguments in scripts.

    The names of the parameters are similar for both cases, only the calling
    syntax changes slightly, based on the underlying structure used.
    For the command line, parameters must be passed as -<parameter name>
    <value>.
    For keyword arguments, parameters must be passed during instantiation
    using the keyword argument syntax of standard <parameter name>=<value>.

    Parameters
    ----------
    """
    default_params = DEFAULT_PARAMS
    mp_func_results = QtCore.pyqtSignal(object)
    updated_composite = QtCore.pyqtSignal()
    parse_func = parse_composite_creator_cmdline_arguments
    attributes_not_to_copy_to_slave_app = ['_shared_arrays', '_index']

    def __init__(self, *args, **kwargs):
        """
        Create a CompositeCreatorApp instance.
        """
        super().__init__(*args, **kwargs)
        self._config['result_shapes'] = {}
        self._config['shared_memory'] = {}
        self._shared_arrays = {}
        self._index
        self._tree = TREE.get_copy()

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()

    def prepare_run(self):
        """
        Prepare running the workflow execution.

        For the main App (i.e. running not in slave_mode), this involves the
        following steps:
            1. Get the shape of all results from the WorkflowTree and store
               them for internal reference.
            2. Get all multiprocessing tasks from the ScanSettings.
            3. Calculate the required buffer size and verify that the memory
               requirements are okay.
            4. Initialize the shared memory arrays.

        Both the slaved and the main applications then initialize local numpy
        arrays from the shared memory.
        """
        if not self.slave_mode:
            self.__check_and_store_results_shapes()
            self.__get_and_store_tasks()
            self.__check_size_of_results_and_calc_buffer_size()
            self.__initialize_shared_memory()
            RESULTS.update_shapes_from_scan()
        self.__initialize_arrays_from_shared_memory()
        if self.get_param_value('live_processing'):
            self.__get_file_target_size()

    def __check_and_store_results_shapes(self):
        """
        Run through the WorkflowTree to get the shapes of all results.

        Raises
        ------
        AppConfigError
            If the WorkflowTree has no nodes.
        """
        _shapes = TREE.get_all_result_shapes()
        self._config['results_shapes'] = _shapes

    def __get_and_store_tasks(self):
        """
        Get the tasks from the global ScanSettings and store them internally.
        """
        _dim = SCAN.get_param_value('scan_dim')
        _points_per_dim = [SCAN.get_param_value(f'n_points_{_n}')
                           for _n in range(1, _dim + 1)]
        _n_total = np.prod(_points_per_dim)
        self._config['mp_tasks'] = np.arange(_n_total)

    def __check_size_of_results_and_calc_buffer_size(self):
        """
        Check the size of results and calculate the number of datasets which
        can be stored in the buffer.

        Raises
        ------
        AppConfigError
            If the buffer is too small to store a one dataset per MP worker.
        """
        _buffer = self.get_global_q_setting_value('shared_buffer_size')
        _n_worker = self.get_global_q_setting_value('mp_workers')
        _req_points_per_dataset = np.sum(
            [np.prod(s) for s in self._config['results_shapes'].items()])
        _req_mem_per_dataset = 4 * _req_points_per_dataset / 2**20
        _n_dataset_in_buffer = int(np.floor(_buffer / _req_mem_per_dataset))
        if _n_dataset_in_buffer < _n_worker:
            _min_buffer = _req_mem_per_dataset * _n_worker
            _error= ('The defined buffer is too small. The required memory '
                     f'per diffraction image is {_req_mem_per_dataset:.3f} '
                     f'MB and {_n_worker} workers have been defined. The '
                     f'minimum buffer size must be {_min_buffer:.2f} MB.')
            raise AppConfigError(_error)
        self._config['buffer_n'] = _n_dataset_in_buffer

    def __initialize_shared_memory(self):
        """
        Initialize the shared memory arrays based on the buffer size and
        the result shapes.
        """
        _n = self._config['buffer_n']
        _share = self._config['shared_memory']
        _share['flag'] = mp.Array('I', _n, lock=mp.Lock())
        for _key in self._config['results_shapes']:
            _shape = (_n, ) + self._config['results_shapes'][_key]
            _share[_key] = mp.Array('f', _shape, lock=mp.Lock())

    def __initialize_arrays_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        for _key, _shape in self._config['results_shapes']:
            _share = self._config['shared_memory'][_key]
            _arr_shape = (self._config['buffer_n'],) + _shape
            self._shared_arrays[_key] = np.frombuffer(
                _share.get_obj(), dtype=np.float32).reshape(_arr_shape)
        self._shared_arrays['flag'] = np.frombuffer(
                self._config['shared_memory']['flag'].get_obj(),
                dtype=np.int32)

    def __store_file_target_size(self):
        """
        Get and store the file target size for live processing.
        """
        self._config['file_size'] = self._tree.root.get_first_file_size(self)

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        if 'mp_tasks' not in self._config.keys():
            raise KeyError('Key "mp_tasks" not found. Please execute'
                           'multiprocessing_pre_run() first.')
        return self._config['mp_tasks']

    def multiprocessing_pre_cycle(self, index):
        """
        Store the reference to the frame index internally.

        Parameters
        ----------
        index : int
            The index of the image / frame.
        """
        self._index = index

    def multiprocessing_carryon(self):
        """
        Get the flag value whether to carry on processing.

        By default, this Flag is always True. In the case of live processing,
        a check is done whether the current file exists.

        Returns
        -------
        bool
            Flag whether the processing can carry on or needs to wait.
        """
        if self.get_param_value('live_processing'):
            _fname = self._tree.root.get_filename(self._index)
            if os.path.exists(_fname):
                _ok = self._config['file_size'] == os.stat(_fname).st_size
                return _ok
        return True

    def multiprocessing_func(self, *index):
        """
        Perform key operation with parallel processing.

        Returns
        -------
        _image : pydidas.core.Dataset
            The (pre-processed) image.
        """
        self._tree.execute_process(0)
        self.__write_results_to_shared_arrays()
        return self._config['buffer_pos']

    def __write_results_to_shared_arrays(self):
        """
        Write the results from the WorkflowTree execution to the shared array.
        """
        _flag_lock = self._config['shared_memory']['flag']
        while True:
            _flag_lock.acquire()
            _zeros = np.where(self._shared_arrays['flag'] == 0)[0]
            if _zeros.size > 0:
                _buffer_pos = _zeros[0]
                self._config['buffer_pos'] = _buffer_pos
                self._shared_arrays['flag'][_buffer_pos] = 1
                break
            _flag_lock.release()
            time.sleep(0.01)
        for _node_id in self._config['result_shapes']:
            self._shared_arrays[_node_id][_buffer_pos] = (
                self._tree.nodes[_node_id].results)
        _flag_lock.release()

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """
        pass

    @QtCore.pyqtSlot(int, object)
    def multiprocessing_store_results(self, index, buffer_pos):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index in the composite image.
        buffer_pos : int
            The buffer position of the results.
        """
        _results = {_key: None for _key in self._config['results_shapes']}
        _flag_lock = self._config['shared_memory']['flag']
        _flag_lock.acquire()
        for _key in _results:
            _results[_key] = self._shared_arrays[_key][buffer_pos]
        self._shared_arrays['flag'][buffer_pos] = 0
        _flag_lock.release()
        RESULTS.store_results(index, _results)
