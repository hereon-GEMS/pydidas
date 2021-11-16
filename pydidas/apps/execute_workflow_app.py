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
Module with the ExecuteWorkflowApp class which allows to run WorkflowTrees
for processing diffraction data.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExecuteWorkflowApp']

import time
import multiprocessing as mp

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.base_app import BaseApp
from pydidas._exceptions import AppConfigError
from pydidas.core import (ParameterCollection,get_generic_parameter,
                          ScanSettings, Dataset)
from pydidas.apps.app_parsers import parse_execute_workflow_cmdline_arguments
from pydidas.workflow_tree import WorkflowTree, WorkflowResults
from pydidas.workflow_tree.result_savers import WorkflowResultSaverMeta
from pydidas.utils import pydidas_logger

TREE = WorkflowTree()

SCAN = ScanSettings()

RESULTS = WorkflowResults()
RESULT_SAVER = WorkflowResultSaverMeta

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('autosave_results'),
    get_generic_parameter('autosave_dir'),
    get_generic_parameter('autosave_format'),
    get_generic_parameter('live_processing'),
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
    autosave_results : bool, optional
        Use this flag to control whether result data should be automatically
        saved to disk. The default is False.
    autosave_dir : Union[pathlib.Path, str], optional
        The directory for autosave_files. If autosave_results is True, the
        directory must be set.
    autosave_format : str
        The formats for saving the results. This must be chosen from the list
        of available formats.
    live_processing : bool, optional
        Flag to enable live processing. This will implement checks on file
        existance before processing starts. The default is False.
    """
    default_params = DEFAULT_PARAMS
    mp_func_results = QtCore.pyqtSignal(object)
    updated_composite = QtCore.pyqtSignal()
    parse_func = parse_execute_workflow_cmdline_arguments
    attributes_not_to_copy_to_slave_app = ['_shared_arrays', '_index']

    def __init__(self, *args, **kwargs):
        """
        Create a CompositeCreatorApp instance.
        """
        super().__init__(*args, **kwargs)
        self._config['result_shapes'] = {}
        self._config['shared_memory'] = {}
        self._config['result_metadata'] = {}
        self._config['result_metadata_set'] = False
        self._config['tree'] = None
        self._shared_arrays = {}
        self._index = None

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
            self._config['tree'] = TREE.get_copy()
            self._config['tree'].prepare_execution()
            self.__check_and_store_result_shapes()
            self.__get_and_store_tasks()
            self.__check_size_of_results_and_calc_buffer_size()
            self.__initialize_shared_memory()
            RESULTS.update_shapes_from_scan_and_workflow()
            if self.get_param_value('autosave_results'):
                RESULTS.prepare_files_for_saving(
                    self.get_param_value('autosave_dir'),
                    self.get_param_value('autosave_format'))
        self.__initialize_arrays_from_shared_memory()
        self._redefine_multiprocessing_carryon()
        if self.get_param_value('live_processing'):
            self._config['tree'].root.plugin.prepare_carryon_check()

    def __check_and_store_result_shapes(self):
        """
        Run through the WorkflowTree to get the shapes of all results.

        Raises
        ------
        AppConfigError
            If the WorkflowTree has no nodes.
        """
        _shapes = self._config['tree'].get_all_result_shapes()
        self._config['result_shapes'] = _shapes

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
        _buffer = self.q_settings_get_global_value('shared_buffer_size', float)
        _n_worker = self.q_settings_get_global_value('mp_n_workers', int)
        _n_data = self.q_settings_get_global_value('shared_buffer_max_n', int)
        _req_points_per_dataset = sum(
            np.prod(s) for s in self._config['result_shapes'].values())
        _req_mem_per_dataset = 4 * _req_points_per_dataset / 2**20
        _n_dataset_in_buffer = int(np.floor(_buffer / _req_mem_per_dataset))
        if _n_dataset_in_buffer < _n_worker:
            _min_buffer = _req_mem_per_dataset * _n_worker
            _error= ('The defined buffer is too small. The required memory '
                     f'per diffraction image is {_req_mem_per_dataset:.3f} '
                     f'MB and {_n_worker} workers have been defined. The '
                     f'minimum buffer size must be {_min_buffer:.2f} MB.')
            raise AppConfigError(_error)
        self._config['buffer_n'] = min(_n_dataset_in_buffer, _n_data,
                                       self._config['mp_tasks'].size)

    def __initialize_shared_memory(self):
        """
        Initialize the shared memory arrays based on the buffer size and
        the result shapes.
        """
        _n = self._config['buffer_n']
        _share = self._config['shared_memory']
        _share['flag'] = mp.Array('I', _n, lock=mp.Lock())
        for _key in self._config['result_shapes']:
            _num = int(_n * np.prod(self._config['result_shapes'][_key]))
            _share[_key] = mp.Array('f', _num, lock=mp.Lock())

    def __initialize_arrays_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        for _key, _shape in self._config['result_shapes'].items():
            _share = self._config['shared_memory'][_key]
            _arr_shape = (self._config['buffer_n'],) + _shape
            self._shared_arrays[_key] = np.frombuffer(
                _share.get_obj(), dtype=np.float32).reshape(_arr_shape)
        self._shared_arrays['flag'] = np.frombuffer(
                self._config['shared_memory']['flag'].get_obj(),
                dtype=np.int32)

    def _redefine_multiprocessing_carryon(self):
        """
        Redefine the multiprocessing_carryon method based on the the
        live_processing settings.

        To speed up processing, this method will link the required function
        directly to multiprocessing_carryon. If live_processing is used,
        this will be the input_available check of the input plugin. If not,
        the return value will always be True.
        """
        if self.get_param_value('live_processing'):
            self.multiprocessing_carryon = self.__live_mp_carryon
        else:
            self.multiprocessing_carryon = lambda: True

    def __live_mp_carryon(self):
        """
        Check the state of the latest file to allow continuation of the
        processing.

        Returns
        -------
        bool
            Flag whether the input is available on the file system.
        """
        return self._config['tree'].root.plugin.input_available(self._index)

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

        Note: This method is a dummy which will be overwritten in the
        prepare_run method depending on the settings for the live processing.

        Returns
        -------
        bool
            Flag whether the processing can carry on or needs to wait.
        """
        return True

    def multiprocessing_func(self, index):
        """
        Perform key operation with parallel processing.

        Returns
        -------
        _image : pydidas.core.Dataset
            The (pre-processed) image.
        """
        self._config['tree'].execute_process(index)
        self.__write_results_to_shared_arrays()
        if self._config['result_metadata_set']:
            return self._config['buffer_pos']
        self.__store_result_metadata()
        return (self._config['buffer_pos'], self._config['result_metadata'])

    def __store_result_metadata(self):
        """
        Store the result metadata because it cannot be broadcast to the shared
        array.
        """
        for _node_id in self._config['result_shapes']:
            _res = self._config['tree'].nodes[_node_id].results
            if isinstance(_res, Dataset):
                self._config['result_metadata'][_node_id] = {
                    'axis_labels': _res.axis_labels,
                    'axis_ranges': _res.axis_ranges,
                    'axis_units': _res.axis_units}
            else:
                self._config['result_metadata'][_node_id] = {
                    'axis_labels': {i: None for i in range(_res.ndim)},
                    'axis_ranges': {i: None for i in range(_res.ndim)},
                    'axis_units': {i: None for i in range(_res.ndim)}}
        self._config['result_metadata_set'] = True

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
                self._config['tree'].nodes[_node_id].results)
        _flag_lock.release()

    def multiprocessing_post_run(self):
        """
        Perform operations after running main parallel processing function.

        The ExecutiveWorkflowApp will update the
        """
        pass

    @QtCore.pyqtSlot(int, object)
    def multiprocessing_store_results(self, index, data):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index in the composite image.
        result : Union[tuple, int]
            The results from multiprocessing_func. This can be either a tuple
            with (buffer_pos, metadata) or the integer buffer_pos.
        """
        if self.slave_mode:
            return
        if isinstance(data, tuple):
            buffer_pos = data[0]
            if not self._config['result_metadata_set']:
                RESULTS.update_frame_metadata(data[1])
                self._store_frame_metadata(data[1])
        else:
            buffer_pos = data
        _new_results = {_key: None for _key in self._config['result_shapes']}
        _flag_lock = self._config['shared_memory']['flag']
        _flag_lock.acquire()
        for _key in _new_results:
            _new_results[_key] = self._shared_arrays[_key][buffer_pos]
        self._shared_arrays['flag'][buffer_pos] = 0
        _flag_lock.release()
        RESULTS.store_results(index, _new_results)
        if self.get_param_value('autosave_results'):
            RESULT_SAVER.export_to_active_savers(index, _new_results)

    def _store_frame_metadata(self, metadata, index=None):
        """
        Store the (separate) metadata from a frame internally.

        Parameters
        ----------
        metadata : dict
            The metadata dictionary.
        """
        for _node_id in self._config['result_shapes']:
            _node_metadata = metadata[_node_id]
            self._config['result_metadata'][_node_id] = {
                'axis_labels': _node_metadata['axis_labels'],
                'axis_ranges': _node_metadata['axis_ranges'],
                'axis_units': _node_metadata['axis_units']}
        self._config['result_metadata_set'] = True
        RESULT_SAVER.push_frame_metadata_to_active_savers(metadata)
