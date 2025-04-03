# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ExecuteWorkflowApp"]


import multiprocessing as mp
import time
import warnings
from multiprocessing.shared_memory import SharedMemory
from typing import Optional, Union

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import (
    BaseApp,
    Dataset,
    FileReadError,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.utils import pydidas_logger
from pydidas.core.utils.dataset_utils import get_default_property_dict
from pydidas.workflow import WorkflowResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoMeta


TREE = WorkflowTree()
SCAN = ScanContext()
EXP = DiffractionExperimentContext()
RESULTS = WorkflowResults()
RESULT_SAVER = ProcessingResultIoMeta

logger = pydidas_logger()


class ExecuteWorkflowApp(BaseApp):
    """
    Inherits from :py:class:`pydidas.apps.BaseApp<pydidas.apps.BaseApp>`.

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
        existence before processing starts. The default is False.

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
    attributes_not_to_copy_to_app_clone = (
        BaseApp.attributes_not_to_copy_to_app_clone
        + [
            "_shared_arrays",
            "_index",
            "_mp_tasks",
        ]
    )
    sig_results_updated = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        self.print_debug = kwargs.pop("print_debug", False)
        BaseApp.__init__(self, *args, **kwargs)
        self._config.update(
            {
                "result_metadata_set": False,
                "shared_memory": {},
                "tree_str_rep": "[]",
                "run_prepared": False,
                "latest_results": None,
                "scan_context": {},
                "exp_context": {},
                "export_files_prepared": False,
            }
        )
        self._index = -1
        self._locals = {"shared_memory_buffers": {}}
        if not self.clone_mode:
            self._prepare_mp_configuration()
        self.reset_runtime_vars()

    def _prepare_mp_configuration(self):
        """
        Prepare the multiprocessing configuration for the app.

        The following items are used for inter-process app communication:

        - A mp.Manager instance for shared state management
        - A dictionary for the shapes of the results
        - A dictionary for the metadata of the results
        - An Event to signal that the shapes are available which allows
          the main process to query the shapes dictionary and initialize
          the shared memory arrays.
        - An Event to signal that the shapes are set and the main process
          has created the shared memory arrays. Workers can then resume
          their work.
        - A Lock to synchronize access to the shared memory arrays.
        """
        self._mp_manager_instance = mp.Manager()
        for _item, _type in [
            ("shapes_dict", self._mp_manager_instance.dict),
            ("metadata_dict", self._mp_manager_instance.dict),
            ("shapes_available", self._mp_manager_instance.Event),
            ("shapes_set", self._mp_manager_instance.Event),
            ("lock", self._mp_manager_instance.Lock),
        ]:
            self.mp_manager[_item] = _type()
        self.mp_manager["main_pid"] = self._mp_manager_instance.Value(
            "I", mp.current_process().pid
        )
        self.mp_manager["buffer_n"] = self._mp_manager_instance.Value("I", 0)

    def reset_runtime_vars(self):
        """
        Reset the runtime variables for a new run.
        """
        self._config["result_metadata_set"] = False
        self._config["run_prepared"] = False
        self._mp_tasks = np.array(())
        self._index = None
        self._shared_arrays = {}
        if not self.clone_mode:
            for _key, _val in self.mp_manager.items():
                if _key.startswith("shape") or _key.endswith("_dict"):
                    _val.clear()

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()

    def prepare_run(self):
        """
        Prepare running the workflow execution.

        For the main App (i.e. running not in clone_mode), this involves the
        following steps:

            1. Get the shape of all results from the WorkflowTree and store
               them for internal reference.
            2. Get all multiprocessing tasks from the ScanContext.
            3. Calculate the required buffer size and verify that the memory
               requirements are okay.
            4. Initialize the shared memory arrays.

        Both the cloned and the main applications then initialize local numpy
        arrays from the shared memory.
        """
        self.reset_runtime_vars()
        self._mp_tasks = np.arange(SCAN.n_points)
        if self.clone_mode:
            self._recreate_context()
        else:
            self.close_shared_arrays_and_memory()
            RESULT_SAVER.set_active_savers_and_title([])
            self._store_context()
            RESULTS.prepare_new_results()
            if self.get_param_value("autosave_results"):
                self._config["export_files_prepared"] = False
        TREE.prepare_execution()
        self._config["run_prepared"] = True
        if self.get_param_value("live_processing"):
            TREE.root.plugin.prepare_carryon_check()

    def _recreate_context(self):
        """
        Recreate the required context from the config for app clones.
        """
        TREE.restore_from_string(self._config["tree_str_rep"])
        for _key, _val in self._config["scan_context"].items():
            SCAN.set_param_value(_key, _val)
        for _key, _val in self._config["exp_context"].items():
            EXP.set_param_value(_key, _val)

    def close_shared_arrays_and_memory(self):
        """
        Close (and unlink) the shared memory buffers.

        Note that only the manager app should unlink the shared memory buffers.
        """
        _buffers = self._locals.get("shared_memory_buffers", {})
        self._shared_arrays = {}
        while _buffers:
            _key, _buffer = _buffers.popitem()
            _buffer.close()
            if not self.clone_mode:
                try:
                    _buffer.unlink()
                except FileNotFoundError:
                    logger.error(
                        "Error while unlinking shared memory buffers from app: %s %s "
                        % (_buffer, self)
                    )
                    pass

    def _store_context(self):
        """
        Store the current context for app clone instances.
        """
        self._config["tree_str_rep"] = TREE.export_to_string()
        self._config["scan_context"] = SCAN.get_param_values_as_dict(
            filter_types_for_export=True
        )
        self._config["exp_context"] = EXP.get_param_values_as_dict(
            filter_types_for_export=True
        )

    def multiprocessing_get_tasks(self) -> np.ndarray:
        """
        Return all tasks required in multiprocessing.

        Returns
        -------
        np.ndarray
            The specified input tasks.
        """
        return self._mp_tasks

    def multiprocessing_pre_cycle(self, index: int):
        """
        Store the reference to the frame index internally.

        Parameters
        ----------
        index : int
            The index of the image / frame.
        """
        self._index = index

    def multiprocessing_carryon(self) -> bool:
        """
        Get the flag value whether to carry on processing.

        By default, this Flag is always True. In the case of live processing,
        a check is done whether the current file exists.

        Returns
        -------
        bool
            Flag whether the processing can carry on or needs to wait.
        """
        if not self.get_param_value("live_processing"):
            return True
        return TREE.root.plugin.input_available(self._index)

    def signal_processed_and_can_continue(self) -> bool:
        """
        Check if the processing can continue.

        This implementation waits for the shapes to be set before continuing.

        Returns
        -------
        bool
            Flag whether the processing can continue.
        """
        return self.mp_manager["shapes_set"].is_set()

    def multiprocessing_func(self, index: int) -> Union[None, int]:
        """
        Perform key operation with parallel processing.

        This method will execute the processing of the WorkflowTree for the
        specified index. The results will be available in the WorkflowTree.
        If the shapes are not yet available in the shared manager dictionary,
        they will be published.

        Parameters
        ----------
        index : int
            The task index to be executed.

        Returns
        -------
        _image : pydidas.core.Dataset
            The (pre-processed) image.
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                TREE.execute_process(index)
        except FileReadError:
            return -1
        with self.mp_manager["lock"]:
            if not self.mp_manager["shapes_available"].is_set():
                self._publish_shapes_and_metadata_to_manager()
        if not self.mp_manager["shapes_set"].is_set():
            if self.clone_mode:
                self._config["latest_results"] = TREE.get_current_results()
                return None
            self._create_shared_memory()
        self.__write_results_to_shared_arrays()
        return self._config["buffer_pos"]

    @QtCore.Slot()
    def multiprocessing_post_run(self):
        """
        Perform operations after running the main parallel processing function.

        This implementation will close the arrays and unlink the shared memory buffers.
        """
        self.close_shared_arrays_and_memory()

    def _publish_shapes_and_metadata_to_manager(self):
        """
        Publish the shapes and metadata to the multiprocessing manager dictionaries.
        """
        _results = TREE.get_current_results()
        for _node_id, _res in _results.items():
            self.mp_manager["shapes_dict"][_node_id] = _res.shape
            if isinstance(_res, Dataset):
                self.mp_manager["metadata_dict"][_node_id] = _res.property_dict
                self.mp_manager["metadata_dict"][_node_id].pop("metadata")
            else:
                self.mp_manager["metadata_dict"][_node_id] = get_default_property_dict(
                    _res.shape
                )
        self.mp_manager["shapes_available"].set()
        RESULTS.store_frame_metadata(dict(self.mp_manager["metadata_dict"]))

    def _create_shared_memory(self):
        """
        Create the necessary shared memory for passing the results.

        This method will determine the buffer size based on the number of
        workers and the size of the results. It will then create the shared
        memory buffers and initialize the numpy arrays from the shared memory.
        """
        if not self.mp_manager["shapes_available"].is_set():
            raise UserConfigError(
                "The shapes of the results are not yet available. "
                "Please run a processing step first to create results."
            )
        if len(self._locals["shared_memory_buffers"]) > 0:
            raise UserConfigError(
                "The shared memory buffers have already been created. "
                "Please unlink them first."
            )
        self._check_size_of_results_and_buffer()
        self._initialize_shared_memory()
        self._initialize_arrays_from_shared_memory()

    def _check_size_of_results_and_buffer(self):
        """
        Check the size of results and the buffer size.

        Raises
        ------
        UserConfigError
            If the buffer is too small to store a one dataset per MP worker.
        """
        _buffer_size_mb = self.q_settings_get("global/shared_buffer_size", float)
        _n_worker = self.q_settings_get("global/mp_n_workers", int)
        _n_data = self.q_settings_get("global/shared_buffer_max_n", int)
        _req_points_per_dataset = sum(
            np.prod(_shape) for _shape in self.mp_manager["shapes_dict"].values()
        )
        _req_mem_per_dataset = max(4 * _req_points_per_dataset / 2**20, 0.01)
        _n_dataset_in_buffer = int(np.floor(_buffer_size_mb / _req_mem_per_dataset))
        if _n_dataset_in_buffer < _n_worker:
            _min_buffer = _req_mem_per_dataset * _n_worker
            raise UserConfigError(
                "The defined buffer is too small. The required memory per diffraction "
                f"image is {_req_mem_per_dataset:.3f} MB and {_n_worker} workers have "
                f"been defined. The minimum buffer size must be {_min_buffer:.2f} MB. "
                "\nPlease update the buffer size or change number of workers in the "
                "global settings."
            )
        self.mp_manager["buffer_n"].value = min(
            _n_dataset_in_buffer, _n_data, self._mp_tasks.size
        )

    def _initialize_shared_memory(self):
        """
        Initialize the shared arrays from the buffer size and result shapes.
        """
        _n = self.mp_manager["buffer_n"].value
        _pid = self.mp_manager["main_pid"].value
        _buffers = self._locals["shared_memory_buffers"] = {}
        _buffers["in_use_flag"] = SharedMemory(
            name=f"share_in_use_flag_{_pid}", create=True, size=4 * _n
        )
        for _node_id, _shape in self.mp_manager["shapes_dict"].items():
            _num_bytes = int(4 * _n * np.prod(_shape))
            _buffers[f"node_{_node_id:03d}"] = SharedMemory(
                name=f"share_node_{_node_id:03d}_{_pid}", create=True, size=_num_bytes
            )
        self.mp_manager["shapes_set"].set()

    def _initialize_arrays_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        _buffer_size = self.mp_manager["buffer_n"].value
        for _key, _shape in self.mp_manager["shapes_dict"].items():
            _shared_mem = self.__get_shared_memory(f"node_{_key:03d}")
            _arr_shape = (_buffer_size,) + _shape
            self._shared_arrays[_key] = np.ndarray(
                _arr_shape, dtype=np.float32, buffer=_shared_mem.buf
            )
        _shared_mem = self.__get_shared_memory("in_use_flag")
        self._shared_arrays["in_use_flag"] = np.ndarray(
            (_buffer_size,), dtype=np.int32, buffer=_shared_mem.buf
        )

    def __get_shared_memory(self, name: Union[str, int]) -> SharedMemory:
        """
        Get the SharedMemory object from the shared memory buffers.

        Parameters
        ----------
        name : Union[str, int]
            The name of the shared memory buffer.

        Returns
        -------
        SharedMemory
            The SharedMemory object.
        """
        _main_pid = self.mp_manager["main_pid"].value
        if name not in self._locals["shared_memory_buffers"]:
            _mem_buffer = SharedMemory(name=f"share_{name}_{_main_pid}")
            self._locals["shared_memory_buffers"][name] = _mem_buffer
        return self._locals["shared_memory_buffers"][name]

    def __write_results_to_shared_arrays(self):
        """Write the results from the WorkflowTree execution to the shared array."""
        if self._shared_arrays == dict():
            self._initialize_arrays_from_shared_memory()
        while True:
            with self.mp_manager["lock"]:
                _zeros = np.where(self._shared_arrays["in_use_flag"] == 0)[0]
                if _zeros.size > 0:
                    _buffer_pos = _zeros[0]
                    self._config["buffer_pos"] = _buffer_pos
                    self._shared_arrays["in_use_flag"][_buffer_pos] = 1
                    break
            time.sleep(0.005)
        with self.mp_manager["lock"]:
            for _node_id in self.mp_manager["shapes_dict"].keys():
                self._shared_arrays[_node_id][_buffer_pos] = TREE.nodes[
                    _node_id
                ].results

    def must_send_signal_and_wait_for_response(self) -> Optional[str]:
        """
        Check if a signal must be sent and wait for the response.

        The ExecuteWorkflowApp sends a signal

        Returns
        -------
        Optional[str]
            The signal to be sent.
        """
        if not self.mp_manager["shapes_set"].is_set():
            return "::shapes_not_set::"
        return None

    def get_latest_results(self) -> Optional[object]:
        """
        Return the latest results from the WorkflowTree.

        Returns
        -------
        dict or None
            The latest results from the WorkflowTree.
        """
        if not self.mp_manager["shapes_set"].is_set():
            return None
        self.__write_results_to_shared_arrays()
        return self._config["buffer_pos"]

    @QtCore.Slot(str)
    def received_signal_message(self, message: str):
        """
        Process the received signal message.

        Parameters
        ----------
        message : str
            The received message.
        """
        if self.mp_manager["shapes_set"].is_set():
            return
        if message == "::shapes_not_set::":
            self._create_shared_memory()

    @QtCore.Slot(object, object)
    def multiprocessing_store_results(self, index: int, *data: tuple):
        """
        Store the results of the multiprocessing operation.

        Parameters
        ----------
        index : int
            The index of the processed task.
        data : tuple
            The results from multiprocessing_func. This can be either a tuple
            with (buffer_pos, metadata) or the integer buffer_pos.
        """
        if self.clone_mode:
            return
        if self._shared_arrays == dict():
            self._initialize_arrays_from_shared_memory()
        # the ExecutiveWorkflowApp only uses the first argument of the variadict data:
        buffer_pos = data[0]
        if buffer_pos == -1:
            _filename = TREE.root.plugin.get_filename(index)
            QtWidgets.QApplication.instance().set_status_message(
                f"File reading error during processing of scan index #{index}."
                f" (filename: {_filename})"
            )
            return
        if not self._config["result_metadata_set"]:
            RESULTS.store_frame_metadata(dict(self.mp_manager["metadata_dict"]))
            self._config["result_metadata_set"] = True
        with self.mp_manager["lock"]:
            _new_results = {
                _key: _arr[buffer_pos]
                for _key, _arr in self._shared_arrays.items()
                if _key != "in_use_flag"
            }
            self._shared_arrays["in_use_flag"][buffer_pos] = 0
        RESULTS.store_results(index, _new_results)
        if self.get_param_value("autosave_results"):
            if not self._config["export_files_prepared"]:
                RESULTS.prepare_files_for_saving(
                    self.get_param_value("autosave_directory"),
                    self.get_param_value("autosave_format"),
                )
                _new_results = {
                    _key: Dataset(_val, **self.mp_manager["metadata_dict"][_key])
                    for _key, _val in _new_results.items()
                }
                self._config["export_files_prepared"] = True
            RESULT_SAVER.export_frame_to_active_savers(index, _new_results)
        self.sig_results_updated.emit()

    def deleteLater(self):
        """
        Delete the instance of the ExecuteWorkflowApp.
        """
        self.__del__()
        super().deleteLater()

    def __del__(self):
        """
        Delete the ExecuteWorkflowApp.
        """
        if not self.clone_mode:
            if isinstance(self._mp_manager_instance, mp.managers.SyncManager):
                self._mp_manager_instance.shutdown()
        self.close_shared_arrays_and_memory()
