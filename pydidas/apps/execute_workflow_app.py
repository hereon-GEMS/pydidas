# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ExecuteWorkflowApp class which allows to run WorkflowTrees
for processing diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ExecuteWorkflowApp"]

import multiprocessing as mp
import time
import warnings

import numpy as np
from qtpy import QtCore

from ..contexts import DiffractionExperimentContext, ScanContext
from ..core import BaseApp, Dataset, UserConfigError, get_generic_param_collection
from ..workflow import WorkflowResultsContext, WorkflowTree
from ..workflow.result_io import WorkflowResultIoMeta
from .parsers import execute_workflow_app_parser


TREE = WorkflowTree()
SCAN = ScanContext()
EXP = DiffractionExperimentContext()
RESULTS = WorkflowResultsContext()
RESULT_SAVER = WorkflowResultIoMeta


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

    Notes
    -----
    The full list of Parameters used by the ExecuteWorkflowApp:

    autosave_results : bool, optional
        Use this flag to control whether result data should be automatically
        saved to disk. The default is False.
    autosave_directory : Union[pathlib.Path, str], optional
        The directory for autosave_files. If autosave_results is True, the
        directory must be set.
    autosave_format : str
        The formats for saving the results. This must be chosen from the list
        of available formats.
    live_processing : bool, optional
        Flag to enable live processing. This will implement checks on file
        existance before processing starts. The default is False.

    The "sig_results_updated" signal will be emitted upon a new update of the
    stored result and can be used

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
        "autosave_results", "autosave_directory", "autosave_format", "live_processing"
    )
    parse_func = execute_workflow_app_parser
    attributes_not_to_copy_to_slave_app = [
        "_shared_arrays",
        "_index",
        "_result_metadata",
        "_mp_tasks",
    ]
    sig_results_updated = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config.update(
            {
                "result_shapes": {},
                "shared_memory": {},
                "tree_str_rep": "[]",
                "buffer_n": 4,
            }
        )
        self._index = -1
        self.reset_runtime_vars()

    def reset_runtime_vars(self):
        """
        Reset the runtime variables for a new run.
        """
        self._config["result_metadata_set"] = False
        self._shared_arrays = {}
        self._result_metadata = {}
        self._mp_tasks = np.array(())
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
            2. Get all multiprocessing tasks from the ScanContext.
            3. Calculate the required buffer size and verify that the memory
               requirements are okay.
            4. Initialize the shared memory arrays.

        Both the slaved and the main applications then initialize local numpy
        arrays from the shared memory.
        """
        self.reset_runtime_vars()
        self._mp_tasks = np.arange(SCAN.n_points)
        if self.slave_mode:
            TREE.restore_from_string(self._config["tree_str_rep"])
            for _key, _val in self._config["scan_context"].items():
                SCAN.set_param_value(_key, _val)
            for _key, _val in self._config["exp_context"].items():
                EXP.set_param_value(_key, _val)
        if not self.slave_mode:
            RESULTS.update_shapes_from_scan_and_workflow()
            RESULT_SAVER.set_active_savers_and_title([])
            self._config["tree_str_rep"] = TREE.export_to_string()
            self._config["scan_context"] = SCAN.get_param_values_as_dict(
                filter_types_for_export=True
            )
            self._config["exp_context"] = EXP.get_param_values_as_dict(
                filter_types_for_export=True
            )
            self.__check_and_store_result_shapes()
            self.__check_size_of_results_and_buffer()
            self.initialize_shared_memory()
            if self.get_param_value("autosave_results"):
                RESULTS.prepare_files_for_saving(
                    self.get_param_value("autosave_directory"),
                    self.get_param_value("autosave_format"),
                )
        self.__initialize_arrays_from_shared_memory()
        self._redefine_multiprocessing_carryon()
        TREE.prepare_execution()
        if self.get_param_value("live_processing"):
            TREE.root.plugin.prepare_carryon_check()

    def __check_and_store_result_shapes(self):
        """
        Run through the WorkflowTree to get the shapes of all results.
        """
        _shapes = TREE.get_all_result_shapes()
        self._config["result_shapes"] = _shapes

    def __check_size_of_results_and_buffer(self):
        """
        Check the size of results and calculate the number of datasets which
        can be stored in the buffer.

        Raises
        ------
        UserConfigError
            If the buffer is too small to store a one dataset per MP worker.
        """
        _buffer = self.q_settings_get_value("global/shared_buffer_size", float)
        _n_worker = self.q_settings_get_value("global/mp_n_workers", int)
        _n_data = self.q_settings_get_value("global/shared_buffer_max_n", int)
        _req_points_per_dataset = sum(
            np.prod(s) for s in self._config["result_shapes"].values()
        )
        _req_mem_per_dataset = max(4 * _req_points_per_dataset / 2**20, 0.01)
        _n_dataset_in_buffer = int(np.floor(_buffer / _req_mem_per_dataset))
        if _n_dataset_in_buffer < _n_worker:
            _min_buffer = _req_mem_per_dataset * _n_worker
            _error = (
                "The defined buffer is too small. The required memory "
                f"per diffraction image is {_req_mem_per_dataset:.3f} "
                f"MB and {_n_worker} workers have been defined. The "
                f"minimum buffer size must be {_min_buffer:.2f} MB."
            )
            raise UserConfigError(_error)
        self._config["buffer_n"] = min(
            _n_dataset_in_buffer, _n_data, self._mp_tasks.size
        )

    def initialize_shared_memory(self):
        """
        Initialize the shared memory arrays based on the buffer size and
        the result shapes.
        """
        _n = self._config["buffer_n"]
        _share = self._config["shared_memory"]
        self._config["shared_memory"]["lock"] = mp.Lock()
        _share["flag"] = mp.Array("I", _n, lock=self._config["shared_memory"]["lock"])
        for _key in self._config["result_shapes"]:
            _num = int(_n * np.prod(self._config["result_shapes"][_key]))
            _share[_key] = mp.Array("f", _num, lock=mp.Lock())

    def __initialize_arrays_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        for _key, _shape in self._config["result_shapes"].items():
            _share = self._config["shared_memory"][_key]
            _arr_shape = (self._config["buffer_n"],) + _shape
            self._shared_arrays[_key] = np.frombuffer(
                _share.get_obj(), dtype=np.float32
            ).reshape(_arr_shape)
        self._shared_arrays["flag"] = np.frombuffer(
            self._config["shared_memory"]["flag"].get_obj(), dtype=np.int32
        )

    def _redefine_multiprocessing_carryon(self):
        """
        Redefine the multiprocessing_carryon method based on the the
        live_processing settings.

        To speed up processing, this method will link the required function
        directly to multiprocessing_carryon. If live_processing is used,
        this will be the input_available check of the input plugin. If not,
        the return value will always be True.
        """
        if self.get_param_value("live_processing"):
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
        return TREE.root.plugin.input_available(self._index)

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        return self._mp_tasks

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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            TREE.execute_process(index)
        self.__write_results_to_shared_arrays()
        if self._config["result_metadata_set"]:
            return self._config["buffer_pos"]
        self.__store_result_metadata()
        return (self._config["buffer_pos"], self._result_metadata)

    def __store_result_metadata(self):
        """
        Store the result metadata because it cannot be broadcast to the shared
        array.
        """
        for _node_id in self._config["result_shapes"]:
            _res = TREE.nodes[_node_id].results
            if isinstance(_res, Dataset):
                self._result_metadata[_node_id] = {
                    "axis_labels": _res.axis_labels,
                    "axis_ranges": _res.axis_ranges,
                    "axis_units": _res.axis_units,
                    "data_unit": _res.data_unit,
                    "data_label": _res.data_label,
                }
            else:
                self._result_metadata[_node_id] = {
                    "axis_labels": {i: None for i in range(_res.ndim)},
                    "axis_ranges": {i: None for i in range(_res.ndim)},
                    "axis_units": {i: None for i in range(_res.ndim)},
                    "data_unit": "",
                    "data_label": "",
                }
        self._config["result_metadata_set"] = True
        if not self.slave_mode:
            RESULT_SAVER.push_frame_metadata_to_active_savers(self._result_metadata)

    def __write_results_to_shared_arrays(self):
        """
        Write the results from the WorkflowTree execution to the shared array.
        """
        while True:
            with self._config["shared_memory"]["lock"]:
                _zeros = np.where(self._shared_arrays["flag"] == 0)[0]
                if _zeros.size > 0:
                    _buffer_pos = _zeros[0]
                    self._config["buffer_pos"] = _buffer_pos
                    self._shared_arrays["flag"][_buffer_pos] = 1
                    break
            time.sleep(0.01)
        for _node_id in self._config["result_shapes"]:
            self._shared_arrays[_node_id][_buffer_pos] = TREE.nodes[_node_id].results

    def multiprocessing_post_run(self):
        """
        Perform operations after running main parallel processing function.
        """

    @QtCore.Slot(int, object)
    def multiprocessing_store_results(self, index, *data):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index of the buffer position.
        data : tuple
            The results from multiprocessing_func. This can be either a tuple
            with (buffer_pos, metadata) or the integer buffer_pos.
        """
        # the ExecutiveWorkflowApp only uses the first argument of the variadict data:
        data = data[0]
        if self.slave_mode:
            return
        if isinstance(data, tuple):
            buffer_pos = data[0]
            if not RESULTS._config["metadata_complete"]:
                RESULTS.update_frame_metadata(data[1])
                self._store_frame_metadata(data[1])
        else:
            buffer_pos = data
        _new_results = {_key: None for _key in self._config["result_shapes"]}
        with self._config["shared_memory"]["lock"]:
            for _key in _new_results:
                _new_results[_key] = self._shared_arrays[_key][buffer_pos]
            self._shared_arrays["flag"][buffer_pos] = 0
        RESULTS.store_results(index, _new_results)
        if self.get_param_value("autosave_results"):
            RESULT_SAVER.export_frame_to_active_savers(index, _new_results)
        self.sig_results_updated.emit()

    def _store_frame_metadata(self, metadata):
        """
        Store the (separate) metadata from a frame internally.

        Parameters
        ----------
        metadata : dict
            The metadata dictionary.
        """
        for _node_id in self._config["result_shapes"]:
            _node_metadata = metadata[_node_id]
            self._result_metadata[_node_id] = {
                "axis_labels": _node_metadata["axis_labels"],
                "axis_ranges": _node_metadata["axis_ranges"],
                "axis_units": _node_metadata["axis_units"],
            }
        self._config["result_metadata_set"] = True
        RESULT_SAVER.push_frame_metadata_to_active_savers(metadata)
