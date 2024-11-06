# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import shutil
import tempfile
import threading
import time
import unittest
from numbers import Integral
from pathlib import Path

import h5py
import numpy as np
from qtpy import QtTest, QtWidgets

from pydidas import IS_QT6, unittest_objects
from pydidas.apps import ExecuteWorkflowApp
from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import PydidasQsettings, UserConfigError, get_generic_parameter, utils
from pydidas.plugins import PluginCollection
from pydidas.workflow import WorkflowResultsContext, WorkflowTree
from pydidas.workflow.result_io import WorkflowResultIoMeta
from pydidas_qtcore import PydidasQApplication


COLL = PluginCollection()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
TREE = WorkflowTree()
RESULTS = WorkflowResultsContext()
RESULT_SAVER = WorkflowResultIoMeta


class TestLock(threading.Thread):
    def __init__(self, memory_addresses, n_buffer, array_shapes):
        super().__init__()
        self._mem = memory_addresses
        self._n_buffer = n_buffer
        self._shapes = array_shapes
        self._shared_arrays = {}
        for _key, _shape in array_shapes.items():
            _share = memory_addresses[_key]
            _arr_shape = (n_buffer,) + _shape
            self._shared_arrays[_key] = np.frombuffer(
                _share.get_obj(), dtype=np.float32
            ).reshape(_arr_shape)
        self._shared_arrays["flag"] = np.frombuffer(
            memory_addresses["flag"].get_obj(), dtype=np.int32
        )

    def run(self):
        self._mem["flag"].acquire()
        self._shared_arrays["flag"][:] = 1
        self._mem["flag"].release()
        time.sleep(0.1)
        self._mem["flag"].acquire()
        self._shared_arrays["flag"][:] = 0
        self._mem["flag"].release()


def generate_tree():
    TREE.clear()
    TREE.create_and_add_node(unittest_objects.DummyLoader())
    TREE.create_and_add_node(unittest_objects.DummyProc())
    TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)


class TestExecuteWorkflowApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _app = QtWidgets.QApplication.instance()
        if _app is None:
            _ = PydidasQApplication([])
        RESULTS.clear_all_results()
        TREE.clear()
        SCAN.restore_all_defaults(True)
        cls._path = Path(tempfile.mkdtemp())
        cls.generate_scan(cls)
        cls.q_settings = PydidasQsettings()
        cls._buf_size = cls.q_settings.value("global/shared_buffer_size", float)
        cls._n_workers = cls.q_settings.value("global/mp_n_workers", int)
        cls.__original_plugin_paths = COLL.registered_paths[:]
        _path = Path(unittest_objects.__file__).parent
        if _path not in COLL.registered_paths:
            COLL.find_and_register_plugins(_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)
        cls.q_settings.set_value("global/shared_buffer_size", cls._buf_size)
        cls.q_settings.set_value("global/mp_n_workers", cls._n_workers)
        COLL.unregister_plugin_path(Path(unittest_objects.__file__).parent)

    def setUp(self):
        RESULT_SAVER.set_active_savers_and_title([])
        RESULTS.clear_all_results()
        generate_tree()
        self.reset_scan_params()

    def tearDown(self):
        ExecuteWorkflowApp.parse_func = execute_workflow_app_parser

    def generate_scan(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_dim", 3)
        self._nscan = (9, 5, 7)
        self._scandelta = (0.1, -0.2, 1.1)
        self._scanoffset = (-5, 0, 1.2)

    def reset_scan_params(self):
        for i in range(3):
            SCAN.set_param_value("scan_dim", 3)
            SCAN.set_param_value(f"scan_dim{i}_n_points", self._nscan[i - 1])
            SCAN.set_param_value(f"scan_dim{i}_delta", self._scandelta[i - 1])
            SCAN.set_param_value(f"scan_dim{i}_offset", self._scanoffset[i - 1])

    def get_master_and_slave_app(self) -> tuple[ExecuteWorkflowApp, ExecuteWorkflowApp]:
        master = ExecuteWorkflowApp()
        master.prepare_run()
        slave = master.copy(slave_mode=True)
        slave.prepare_run()
        return master, slave

    def test_creation(self):
        app = ExecuteWorkflowApp()
        self.assertIsInstance(app, ExecuteWorkflowApp)

    def test_creation_with_args(self):
        _autosave = get_generic_parameter("autosave_results")
        _autosave.value = True
        app = ExecuteWorkflowApp(_autosave)
        self.assertTrue(app.get_param_value("autosave_results"))

    def test_creation_with_cmdargs(self):
        ExecuteWorkflowApp.parse_func = lambda x: {"autosave_results": True}
        app = ExecuteWorkflowApp()
        self.assertTrue(app.get_param_value("autosave_results"))

    def test_prepare_mp_configuration(self):
        app = ExecuteWorkflowApp()
        self.assertEqual(app._mp_manager_instance.__class__, mp.managers.SyncManager)
        for _key in ("shapes_available", "shapes_set", "shapes_dict", "metadata_dict"):
            self.assertIn(_key, app.mp_manager)

    def test_prepare_mp_configuration__slave_mode(self):
        app = ExecuteWorkflowApp(slave_mode=True)
        self.assertIsNone(app._mp_manager_instance)
        self.assertEqual(app.mp_manager, {})

    def test_reset_runtime_vars(self):
        app = ExecuteWorkflowApp()
        app._index = 12
        app._config.update(
            {
                "result_metadata_set": True,
                "run_prepared": True,
            }
        )
        app._mp_tasks = np.arange(SCAN.n_points)
        app._shared_arrays = {1: np.ones((10, 10)), 2: np.ones((10, 10))}
        app.mp_manager["shapes_available"].set()
        app.mp_manager["shapes_set"].set()
        app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        app.mp_manager["metadata_dict"] = {
            1: {
                "axis_labels": ["x", "y"],
                "axis_units": ["m", "m"],
                "axis_ranges": [(0, 1), (0, 1)],
            }
        }
        app.reset_runtime_vars()
        self.assertEqual(app._index, None)
        self.assertFalse(app._config["result_metadata_set"])
        self.assertFalse(app._config["run_prepared"])
        self.assertEqual(app._mp_tasks.size, 0)
        self.assertEqual(app._shared_arrays, {})
        self.assertFalse(app.mp_manager["shapes_available"].is_set())
        self.assertFalse(app.mp_manager["shapes_set"].is_set())

    def test_store_context(self):
        app = ExecuteWorkflowApp()
        app._store_context()
        self.assertEqual(app._config["tree_str_rep"], TREE.export_to_string())
        for _key, _val in SCAN.get_param_values_as_dict(
            filter_types_for_export=True
        ).items():
            self.assertEqual(app._config["scan_context"][_key], _val)
        for _key, _val in EXP.get_param_values_as_dict(
            filter_types_for_export=True
        ).items():
            self.assertEqual(app._config["exp_context"][_key], _val)

    def test_recreate_context__WorkflowTree(self):
        _tree_rep = TREE.export_to_string()
        app = ExecuteWorkflowApp()
        app._config["tree_str_rep"] = TREE.export_to_string()
        TREE.clear()
        app._recreate_context()
        self.assertEqual(_tree_rep, TREE.export_to_string())

    def test_recreate_context__Scan(self):
        self.generate_scan()
        _scan_copy = SCAN.get_param_values_as_dict()
        app = ExecuteWorkflowApp()
        app._config["scan_context"] = SCAN.get_param_values_as_dict(
            filter_types_for_export=True
        )
        SCAN.restore_all_defaults(True)
        app._recreate_context()
        for _key, _val in _scan_copy.items():
            self.assertEqual(SCAN.get_param_value(_key), _val)

    def test_recreate_context__DiffractionExperiment(self):
        EXP.set_param_value("xray_energy", 42)
        _exp_copy = EXP.get_param_values_as_dict()
        app = ExecuteWorkflowApp()
        app._config["exp_context"] = EXP.get_param_values_as_dict(
            filter_types_for_export=True
        )
        EXP.restore_all_defaults(True)
        app._recreate_context()
        for _key, _val in _exp_copy.items():
            self.assertEqual(EXP.get_param_value(_key), _val)

    def test_unlink_shared_memory_buffers__empty(self):
        app = ExecuteWorkflowApp()
        app._unlink_shared_memory_buffers()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})

    def test_unlink_shared_memory_buffers(self):
        app = ExecuteWorkflowApp()
        for _key in (1, 2):
            app._locals["shared_memory_buffers"][_key] = mp.shared_memory.SharedMemory(
                create=True, size=100, name=f"test_{_key}"
            )
        self.assertEqual(len(app._locals["shared_memory_buffers"]), 2)
        app._unlink_shared_memory_buffers()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})

    def test_unlink_shared_memory_buffers__slave(self):
        master = ExecuteWorkflowApp()
        for _key in (1, 2):
            master._locals["shared_memory_buffers"][_key] = (
                mp.shared_memory.SharedMemory(
                    create=True, size=100, name=f"test_{_key}"
                )
            )
        app = master.copy(slave_mode=True)
        app._unlink_shared_memory_buffers()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})
        self.assertEqual(len(master._locals["shared_memory_buffers"]), 2)

    def test_prepare_run__slave_mode(self):
        master_app = ExecuteWorkflowApp()
        master_app.prepare_run()
        app = master_app.copy(slave_mode=True)
        app.prepare_run()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__master_mode(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__master_not_live_no_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value("autosave_results", False)
        app.set_param_value("live_processing", False)
        app.prepare_run()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__master_not_live_w_autosave(self):
        app = ExecuteWorkflowApp()
        app._config["export_files_prepared"] = True
        app.set_param_value("autosave_results", True)
        app.set_param_value("autosave_directory", self._path.joinpath("test"))
        app.set_param_value("live_processing", False)
        app.prepare_run()
        self.assertFalse(app._config["export_files_prepared"])

    def test_prepare_run__master_live_no_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value("autosave_results", False)
        app.set_param_value("live_processing", True)
        app.prepare_run()
        self.assertTrue(TREE.root.plugin._config["carryon_checked"])

    def test_multiprocessing_pre_cycle(self):
        _index = int(np.ceil(np.random.random() * 1e5))
        app = ExecuteWorkflowApp()
        app.multiprocessing_pre_cycle(_index)
        self.assertEqual(_index, app._index)

    def test_multiprocessing_carryon__not_live(self):
        app = ExecuteWorkflowApp()
        app.set_param_value("live_processing", False)
        self.assertTrue(app.multiprocessing_carryon())

    def test_multiprocessing_carryon__live(self):
        TREE.root.plugin.input_available = lambda x: x
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.set_param_value("live_processing", True)
        app._index = utils.get_random_string(8)
        self.assertEqual(app.multiprocessing_carryon(), app._index)

    def test_multiprocessing_func__as_master(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.mp_manager["shapes_dict"][1] = (12, 24)
        app.mp_manager["shapes_dict"][2] = (24, 12)
        _res = app.multiprocessing_func(_index)
        self.assertEqual(_res, 0)
        self.assertIsInstance(app._shared_arrays[1], np.ndarray)
        self.assertIsInstance(app._shared_arrays[2], np.ndarray)
        self.assertTrue(np.allclose(TREE.nodes[1].results, app._shared_arrays[1][0]))
        self.assertTrue(np.allclose(TREE.nodes[2].results, app._shared_arrays[2][0]))
        self.assertTrue(app.mp_manager["shapes_set"].is_set())

    def test_multiprocessing_func__as_slave__fresh(self):
        _index = 12
        master = ExecuteWorkflowApp()
        master.prepare_run()
        app = master.copy(slave_mode=True)
        app.prepare_run()
        _res = app.multiprocessing_func(_index)
        _tree_res = TREE.get_current_results()
        self.assertTrue(master.mp_manager["shapes_available"].is_set())
        self.assertIsNone(_res)
        for _key, _data in _tree_res.items():
            _shape = _data.shape
            self.assertTrue(master.mp_manager["shapes_dict"][_key], _shape)
            for _k in ["axis_labels", "axis_units", "data_unit", "data_label"]:
                _stored_data = master.mp_manager["metadata_dict"][_key]
                self.assertEqual(getattr(_data, _k), _stored_data[_k])
            for _dim in range(_data.ndim):
                self.assertTrue(
                    np.allclose(
                        _data.axis_ranges[_dim],
                        master.mp_manager["metadata_dict"][_key]["axis_ranges"][_dim],
                    )
                )

    def test_multiprocessing_func__as_slave__master_configured(self):
        _index = 12
        master = ExecuteWorkflowApp()
        master.prepare_run()
        app = master.copy(slave_mode=True)
        app.prepare_run()
        _ = master.multiprocessing_func(_index)
        _ = master.multiprocessing_func(_index)
        for _ in range(4):
            _buffer = app.multiprocessing_func(_index)
        _tree_res = TREE.get_current_results()
        _res1 = master._shared_arrays[1][_buffer]
        _res2 = master._shared_arrays[2][_buffer]
        self.assertTrue(np.allclose(_res1, _tree_res[1]))
        self.assertTrue(np.allclose(_res2, _tree_res[2]))

    def test_publish_shapes_and_metadata_to_manager__with_Dataset(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        TREE.execute_process(0)
        app._publish_shapes_and_metadata_to_manager()
        self.assertTrue(app.mp_manager["shapes_available"].is_set())
        self.assertTrue(RESULTS._config["shapes_set"])
        for _key, _res in TREE.get_current_results().items():
            self.assertEqual(app.mp_manager["shapes_dict"][_key], _res.shape)
            self.assertEqual(
                app.mp_manager["metadata_dict"][_key]["axis_labels"], _res.axis_labels
            )
            self.assertEqual(
                app.mp_manager["metadata_dict"][_key]["axis_units"], _res.axis_units
            )
            self.assertEqual(
                app.mp_manager["metadata_dict"][_key]["data_unit"], _res.data_unit
            )
            self.assertEqual(
                app.mp_manager["metadata_dict"][_key]["data_label"], _res.data_label
            )
            for _dim in range(_res.ndim):
                self.assertTrue(
                    np.allclose(
                        _res.axis_ranges[_dim],
                        app.mp_manager["metadata_dict"][_key]["axis_ranges"][_dim],
                    )
                )

    def test_publish_shapes_and_metadata_to_manager__with_ndarray(self):
        TREE.delete_node_by_id(2)
        TREE.execute_process(0)
        TREE.nodes[1].results = TREE.nodes[1].results.array
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._publish_shapes_and_metadata_to_manager()
        self.assertTrue(RESULTS._config["shapes_set"])
        self.assertTrue(app.mp_manager["shapes_available"].is_set())
        for _key, _res in TREE.get_current_results().items():
            self.assertEqual(app.mp_manager["shapes_dict"][_key], _res.shape)
            for _dim in range(_res.ndim):
                self.assertIsInstance(
                    app.mp_manager["metadata_dict"][_key]["axis_labels"][_dim], str
                )
                self.assertIsInstance(
                    app.mp_manager["metadata_dict"][_key]["axis_units"][_dim], str
                )
                self.assertIsInstance(
                    app.mp_manager["metadata_dict"][_key]["axis_ranges"][_dim],
                    np.ndarray,
                )
                self.assertIsInstance(
                    app.mp_manager["metadata_dict"][_key]["data_unit"], str
                )
                self.assertIsInstance(
                    app.mp_manager["metadata_dict"][_key]["data_label"], str
                )

    def test_create_shared_memory__not_set(self):
        app = ExecuteWorkflowApp()
        with self.assertRaises(UserConfigError):
            app._create_shared_memory()

    def test_create_shared_memory__memory_buffer_not_empty(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.mp_manager["shapes_available"].set()
        app._locals["shared_memory_buffers"][1] = mp.shared_memory.SharedMemory(
            create=True, size=100, name="test"
        )
        with self.assertRaises(UserConfigError):
            app._create_shared_memory()

    def test_check_size_of_results_and_buffer__buffer_too_small(self):
        app = ExecuteWorkflowApp()
        _max_size = int(app.q_settings_get("global/shared_buffer_size", float))
        app.mp_manager["shapes_dict"] = {1: tuple(_max_size * 500 for _ in range(3))}
        with self.assertRaises(UserConfigError):
            app._check_size_of_results_and_buffer()

    def test_check_size_of_results_and_buffer__buffer_okay(self):
        app = ExecuteWorkflowApp()
        app._mp_tasks = np.arange(SCAN.n_points)
        app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        app._check_size_of_results_and_buffer()
        self.assertTrue(app.mp_manager["buffer_n"].value > 0)

    def test_initialize_shared_memory(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.mp_manager["buffer_n"].value = 10
        app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        app.mp_manager["shapes_available"].set()
        app._initialize_shared_memory()
        self.assertTrue(app.mp_manager["shapes_set"].is_set())
        self.assertTrue(app.mp_manager["buffer_n"].value > 0)
        for _key in list(app.mp_manager["shapes_dict"].keys()) + ["flag"]:
            self.assertIsInstance(
                app._locals["shared_memory_buffers"][_key],
                mp.shared_memory.SharedMemory,
            )

    def test_initialize_arrays_from_shared_memory(self):
        master = ExecuteWorkflowApp()
        master.prepare_run()
        master.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        master.mp_manager["buffer_n"].value = 10
        master._initialize_shared_memory()
        app = master.copy(slave_mode=True)
        app._initialize_arrays_from_shared_memory()
        for _key in (1, 2):
            self.assertIsInstance(app._shared_arrays[_key], np.ndarray)
            self.assertEqual(app._shared_arrays[_key].shape, (10, 10, 10))
        self.assertIsInstance(app._shared_arrays["flag"], np.ndarray)

    def test_get_shared_memory__in_buffer(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _share = mp.shared_memory.SharedMemory(create=True, size=100, name="test")
        app._locals["shared_memory_buffers"][1] = _share
        _res = app._ExecuteWorkflowApp__get_shared_memory(1)
        self.assertIsInstance(_res, mp.shared_memory.SharedMemory)
        self.assertEqual(id(_share), id(_res))

    def test_get_shared_memory__new(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _share = mp.shared_memory.SharedMemory(
            create=True, size=100, name=f"1_{app.mp_manager['master_pid'].value}"
        )
        _res = app._ExecuteWorkflowApp__get_shared_memory(1)
        self.assertIsInstance(_res, mp.shared_memory.SharedMemory)

    def test_write_results_to_shared_arrays__arrays_not_created(self):
        TREE.execute_process(0)
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._publish_shapes_and_metadata_to_manager()
        app._check_size_of_results_and_buffer()
        app._initialize_shared_memory()
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][0]))

    def test_write_results_to_shared_arrays__arrays_created(self):
        TREE.execute_process(0)
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._publish_shapes_and_metadata_to_manager()
        app._create_shared_memory()
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][0]))

    def test_must_send_signal_and_wait_for_respose(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _sig = app.must_send_signal_and_wait_for_response()
        self.assertEqual(_sig, "::shapes_not_set::")

    def test_must_send_signal_and_wait_for_response__shapes_set(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.mp_manager["shapes_set"].set()
        _sig = app.must_send_signal_and_wait_for_response()
        self.assertIsNone(_sig)

    def test_get_latest_results__shapes_not_set(self):
        master = ExecuteWorkflowApp()
        master.prepare_run()
        app = master.copy(slave_mode=True)
        app.prepare_run()
        self.assertIsNone(app.get_latest_results())

    def test_get_latest_results__shapes_set(self):
        master = ExecuteWorkflowApp()
        master.prepare_run()
        _ = master.multiprocessing_func(0)
        app = master.copy(slave_mode=True)
        app.prepare_run()
        _index = app.get_latest_results()
        self.assertIsInstance(_index, Integral)
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][_index]))

    def test_received_signal_message__shapes_not_set(self):
        master = ExecuteWorkflowApp()
        master.prepare_run()
        app = master.copy(slave_mode=True)
        app.prepare_run()
        _index = app.multiprocessing_func(0)
        self.assertIsNone(_index)
        master.received_signal_message("::shapes_not_set::")
        self.assertTrue(master.mp_manager["shapes_set"].is_set())
        for _key in master.mp_manager["shapes_dict"]:
            self.assertIsInstance(master._shared_arrays[_key], np.ndarray)

    def test_multiprocessing_store_results_as_slave(self):
        master, app = self.get_master_and_slave_app()
        _spy = QtTest.QSignalSpy(app.sig_results_updated)
        _index = app.multiprocessing_func(0)
        app.multiprocessing_store_results(0, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 0)

    def test_multiprocessing_store_results__processing_error(self):
        master, _ = self.get_master_and_slave_app()
        _spy = QtTest.QSignalSpy(master.sig_results_updated)
        _index = master.multiprocessing_func(0)
        master.multiprocessing_store_results(0, -1)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 0)

    def test_multiprocessing_store_results(self):
        master, _ = self.get_master_and_slave_app()
        _spy = QtTest.QSignalSpy(master.sig_results_updated)
        _index = master.multiprocessing_func(0)
        master.multiprocessing_store_results(0, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 1)
        self.assertTrue(master._config["result_metadata_set"])
        self.assertTrue(RESULTS._composites[1][SCAN.get_index_of_frame(0)].std() > 0)

    def test_multiprocessing_store_results__autosave(self):
        master, _ = self.get_master_and_slave_app()
        master.set_param_value("autosave_results", True)
        master.set_param_value("autosave_directory", self._path.joinpath("test"))
        _index = master.multiprocessing_func(0)
        master.multiprocessing_store_results(0, _index)
        _node_id = 1
        _fname = self._path.joinpath("test", f"node_{_node_id:02d}.h5")
        self.assertTrue(master._config["export_files_prepared"])
        with h5py.File(_fname, "r") as _f:
            _data = _f["entry/data/data"][SCAN.get_index_position_in_scan(0)]
            self.assertTrue(np.all(_data > 0))

    def test_multiprocessing_store_results__repetitive(self):
        master, _ = self.get_master_and_slave_app()
        _spy = QtTest.QSignalSpy(master.sig_results_updated)
        _i_dim = SCAN.ndim - 1
        for _i in range(SCAN.shape[_i_dim]):
            _index = master.multiprocessing_func(_i)
            master.multiprocessing_store_results(_i, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, SCAN.shape[_i_dim])
        _slices = (0,) * _i_dim + (
            slice(
                None,
            ),
        )
        self.assertTrue(np.all(RESULTS._composites[1][_slices] > 0))

    def test_multiprocessing_store_results__w_master_and_slave(self):
        master, app = self.get_master_and_slave_app()
        _spy = QtTest.QSignalSpy(master.sig_results_updated)
        _i_dim = SCAN.ndim - 1
        for _i in range(SCAN.shape[_i_dim]):
            _index = app.multiprocessing_func(_i)
            if _index is None:
                master._create_shared_memory()
                _index = app.get_latest_results()
            master.multiprocessing_store_results(_i, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, SCAN.shape[_i_dim])
        _slices = (0,) * _i_dim + (
            slice(
                None,
            ),
        )
        self.assertTrue(np.all(RESULTS._composites[1][_slices] > 0))

    def test_run(self):
        app = ExecuteWorkflowApp()
        SCAN.set_param_value("scan_dim", 2)
        app.run()
        _res = RESULTS.get_results(1)
        self.assertTrue(np.all(_res > 0))

    def test_run__repetitive(self):
        app = ExecuteWorkflowApp()
        SCAN.set_param_value("scan_dim", 2)
        app.run()
        app.run()
        _res = RESULTS.get_results(1)
        self.assertTrue(np.all(_res > 0))


if __name__ == "__main__":
    unittest.main()
