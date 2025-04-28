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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import multiprocessing as mp
import queue
import shutil
import tempfile
import time
import unittest
from numbers import Integral
from pathlib import Path

import h5py
import numpy as np
from qtpy import QtTest, QtWidgets

from pydidas import IS_QT6, LOGGING_LEVEL, unittest_objects
from pydidas.apps import ExecuteWorkflowApp
from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import PydidasQsettings, UserConfigError, get_generic_parameter, utils
from pydidas.core.utils import get_random_string
from pydidas.multiprocessing import app_processor
from pydidas.plugins import PluginCollection
from pydidas.workflow import WorkflowResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoMeta
from pydidas_qtcore import PydidasQApplication


COLL = PluginCollection()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
TREE = WorkflowTree()
RESULTS = WorkflowResults()
RESULT_SAVER = ProcessingResultIoMeta


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
        TREE.clear()
        TREE.create_and_add_node(unittest_objects.DummyLoader())
        TREE.create_and_add_node(unittest_objects.DummyProc())
        TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)
        self.reset_scan_params()
        self._shares = []
        self._apps = []

    def tearDown(self):
        ExecuteWorkflowApp.parse_func = execute_workflow_app_parser
        for _app in self._apps:
            _app.close_shared_arrays_and_memory()
        for _share in self._shares:
            _share.close()
            _share.unlink()

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

    def get_main_app_and_app_clone(
        self,
    ) -> tuple[ExecuteWorkflowApp, ExecuteWorkflowApp]:
        manager = ExecuteWorkflowApp()
        manager.prepare_run()
        self._apps.append(manager)
        clone = manager.copy(clone_mode=True)
        clone.prepare_run()
        self._apps.append(clone)
        return manager, clone

    def get_exec_workflow_app(self, *args, **kwargs) -> ExecuteWorkflowApp:
        app = ExecuteWorkflowApp(*args, **kwargs)
        if app.clone_mode:
            app._config["tree_str_rep"] = TREE.export_to_string()
        app.prepare_run()
        self._apps.append(app)
        return app

    def test_creation(self):
        app = self.get_exec_workflow_app()
        self.assertIsInstance(app, ExecuteWorkflowApp)

    def test_creation_with_args(self):
        _autosave = get_generic_parameter("autosave_results")
        _autosave.value = True
        app = self.get_exec_workflow_app(_autosave)
        self.assertTrue(app.get_param_value("autosave_results"))

    def test_creation_with_cmdargs(self):
        ExecuteWorkflowApp.parse_func = lambda x: {"autosave_results": True}
        app = self.get_exec_workflow_app()
        self.assertTrue(app.get_param_value("autosave_results"))

    def test_prepare_mp_configuration(self):
        app = self.get_exec_workflow_app()
        self.assertEqual(app._mp_manager_instance.__class__, mp.managers.SyncManager)
        for _key in ("shapes_available", "shapes_set", "shapes_dict", "metadata_dict"):
            self.assertIn(_key, app.mp_manager)

    def test_prepare_mp_configuration__clone_mode(self):
        app = self.get_exec_workflow_app(clone_mode=True)
        self.assertIsNone(app._mp_manager_instance)
        self.assertEqual(app.mp_manager, {})

    def test_reset_runtime_vars(self):
        app = self.get_exec_workflow_app()
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
        app = self.get_exec_workflow_app()
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
        app = self.get_exec_workflow_app()
        app._config["tree_str_rep"] = TREE.export_to_string()
        TREE.clear()
        app._recreate_context()
        self.assertEqual(_tree_rep, TREE.export_to_string())

    def test_recreate_context__Scan(self):
        self.generate_scan()
        _scan_copy = SCAN.get_param_values_as_dict()
        app = self.get_exec_workflow_app()
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
        app = self.get_exec_workflow_app()
        app._config["exp_context"] = EXP.get_param_values_as_dict(
            filter_types_for_export=True
        )
        EXP.restore_all_defaults(True)
        app._recreate_context()
        for _key, _val in _exp_copy.items():
            self.assertEqual(EXP.get_param_value(_key), _val)

    def test_close_shared_arrays_and_memory__empty(self):
        app = self.get_exec_workflow_app()
        app.close_shared_arrays_and_memory()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})

    def test_close_shared_arrays_and_memory(self):
        app = self.get_exec_workflow_app()
        for _key in (1, 2):
            app._locals["shared_memory_buffers"][_key] = mp.shared_memory.SharedMemory(
                create=True, size=100, name=f"test_{_key}"
            )
        self.assertEqual(len(app._locals["shared_memory_buffers"]), 2)
        app.close_shared_arrays_and_memory()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})

    def test_close_shared_arrays_and_memory__clone(self):
        main_app = self.get_exec_workflow_app()
        for _key in (1, 2):
            _share = mp.shared_memory.SharedMemory(
                create=True, size=100, name=f"test_{_key}"
            )
            main_app._locals["shared_memory_buffers"][_key] = _share
        app = main_app.copy(clone_mode=True)
        self._apps.append(app)
        app.close_shared_arrays_and_memory()
        self.assertEqual(app._locals.get("shared_memory_buffers"), {})
        self.assertEqual(len(main_app._locals["shared_memory_buffers"]), 2)

    def test_prepare_run__clone_mode(self):
        main_app, app = self.get_main_app_and_app_clone()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__main_mode(self):
        app = self.get_exec_workflow_app()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__main_no_autosave(self):
        app = self.get_exec_workflow_app()
        app.set_param_value("autosave_results", False)
        app.prepare_run()
        self.assertTrue(app._config["run_prepared"])

    def test_prepare_run__main_w_autosave(self):
        app = self.get_exec_workflow_app()
        app._config["export_files_prepared"] = True
        app.set_param_value("autosave_results", True)
        app.set_param_value("autosave_directory", self._path.joinpath("test"))
        app.prepare_run()
        self.assertFalse(app._config["export_files_prepared"])

    def test_multiprocessing_pre_cycle(self):
        _index = int(np.ceil(np.random.random() * 1e5))
        app = self.get_exec_workflow_app()
        app.multiprocessing_pre_cycle(_index)
        self.assertEqual(_index, app._index)

    def test_multiprocessing_carryon__not_live(self):
        app = self.get_exec_workflow_app()
        app.set_param_value("live_processing", False)
        self.assertTrue(app.multiprocessing_carryon())

    def test_multiprocessing_carryon__live(self):
        TREE.root.plugin.input_available = lambda x: x
        app = self.get_exec_workflow_app()
        app.prepare_run()
        app.set_param_value("live_processing", True)
        app._index = utils.get_random_string(8)
        self.assertEqual(app.multiprocessing_carryon(), app._index)

    def signal_processed_and_can_continue__as_main(self):
        app = self.get_exec_workflow_app()
        app.mp_manager["shapes_set"].set()
        self.assertTrue(app.signal_processed_and_can_continue())

    def signal_processed_and_can_continue__as_clone(self):
        main_app, app = self.get_main_app_and_app_clone()
        main_app.mp_manager["shapes_set"].set()
        self.assertTrue(app.signal_processed_and_can_continue())

    def test_multiprocessing_func__as_main_app(self):
        _index = 12
        app = self.get_exec_workflow_app()
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

    def test_multiprocessing_func__as_clone__fresh(self):
        _index = 12
        main_app, app = self.get_main_app_and_app_clone()
        _res = app.multiprocessing_func(_index)
        _tree_res = TREE.get_current_results()
        self.assertTrue(main_app.mp_manager["shapes_available"].is_set())
        self.assertIsNone(_res)
        for _key, _data in _tree_res.items():
            _shape = _data.shape
            self.assertTrue(main_app.mp_manager["shapes_dict"][_key], _shape)
            for _k in ["axis_labels", "axis_units", "data_unit", "data_label"]:
                _stored_data = main_app.mp_manager["metadata_dict"][_key]
                self.assertEqual(getattr(_data, _k), _stored_data[_k])
            for _dim in range(_data.ndim):
                self.assertTrue(
                    np.allclose(
                        _data.axis_ranges[_dim],
                        main_app.mp_manager["metadata_dict"][_key]["axis_ranges"][_dim],
                    )
                )

    def test_multiprocessing_func__as_clone__main_app_configured(self):
        _index = 12
        main_app, app = self.get_main_app_and_app_clone()
        _ = main_app.multiprocessing_func(_index)
        _ = main_app.multiprocessing_func(_index)
        for _ in range(4):
            _buffer = app.multiprocessing_func(_index)
        _tree_res = TREE.get_current_results()
        _res1 = main_app._shared_arrays[1][_buffer]
        _res2 = main_app._shared_arrays[2][_buffer]
        self.assertTrue(np.allclose(_res1, _tree_res[1]))
        self.assertTrue(np.allclose(_res2, _tree_res[2]))

    def test_publish_shapes_and_metadata_to_manager__with_Dataset(self):
        app = self.get_exec_workflow_app()
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
        app = self.get_exec_workflow_app()
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
        app = self.get_exec_workflow_app()
        with self.assertRaises(UserConfigError):
            app._create_shared_memory()

    def test_create_shared_memory__memory_buffer_not_empty(self):
        app = self.get_exec_workflow_app()
        app.prepare_run()
        app.mp_manager["shapes_available"].set()
        app._locals["shared_memory_buffers"][1] = mp.shared_memory.SharedMemory(
            create=True, size=100, name="test"
        )
        with self.assertRaises(UserConfigError):
            app._create_shared_memory()

    def test_check_size_of_results_and_buffer__buffer_too_small(self):
        app = self.get_exec_workflow_app()
        _max_size = int(app.q_settings_get("global/shared_buffer_size", float))
        app.mp_manager["shapes_dict"] = {1: tuple(_max_size * 500 for _ in range(3))}
        with self.assertRaises(UserConfigError):
            app._check_size_of_results_and_buffer()

    def test_check_size_of_results_and_buffer__buffer_okay(self):
        app = self.get_exec_workflow_app()
        app._mp_tasks = np.arange(SCAN.n_points)
        app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        app._check_size_of_results_and_buffer()
        self.assertTrue(app.mp_manager["buffer_n"].value > 0)

    def test_initialize_shared_memory(self):
        app = self.get_exec_workflow_app()
        app.mp_manager["buffer_n"].value = 10
        app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        app.mp_manager["shapes_available"].set()
        app._initialize_shared_memory()
        self.assertTrue(app.mp_manager["shapes_set"].is_set())
        self.assertTrue(app.mp_manager["buffer_n"].value > 0)
        for _key in list(app.mp_manager["shapes_dict"].keys()):
            _label = f"node_{_key:03d}"
            self.assertIsInstance(
                app._locals["shared_memory_buffers"][_label],
                mp.shared_memory.SharedMemory,
            )
        self.assertIsInstance(
            app._locals["shared_memory_buffers"]["in_use_flag"],
            mp.shared_memory.SharedMemory,
        )

    def test_initialize_arrays_from_shared_memory(self):
        main_app = self.get_exec_workflow_app()
        main_app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
        main_app.mp_manager["buffer_n"].value = 10
        main_app._initialize_shared_memory()
        app = main_app.copy(clone_mode=True)
        self._apps.append(app)
        app._initialize_arrays_from_shared_memory()
        for _key in (1, 2):
            self.assertIsInstance(app._shared_arrays[_key], np.ndarray)
            self.assertEqual(app._shared_arrays[_key].shape, (10, 10, 10))
        self.assertIsInstance(app._shared_arrays["in_use_flag"], np.ndarray)

    def test_get_shared_memory__in_buffer(self):
        app = self.get_exec_workflow_app()
        _pid = app.mp_manager["main_pid"].value
        _share = mp.shared_memory.SharedMemory(create=True, size=100, name="test")
        app._locals["shared_memory_buffers"]["test"] = _share
        _res = app._ExecuteWorkflowApp__get_shared_memory("test")
        self.assertIsInstance(_res, mp.shared_memory.SharedMemory)
        self.assertEqual(id(_share), id(_res))

    def test_get_shared_memory__new(self):
        app = self.get_exec_workflow_app()
        _share = mp.shared_memory.SharedMemory(
            create=True,
            size=100,
            name=f"share_node_001_{app.mp_manager['main_pid'].value}",
        )
        _res = app._ExecuteWorkflowApp__get_shared_memory("node_001")
        self.assertIsInstance(_res, mp.shared_memory.SharedMemory)

    def test_write_results_to_shared_arrays__arrays_not_created(self):
        TREE.execute_process(0)
        app = self.get_exec_workflow_app()
        app._publish_shapes_and_metadata_to_manager()
        app._check_size_of_results_and_buffer()
        app._initialize_shared_memory()
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][0]))

    def test_write_results_to_shared_arrays__arrays_created(self):
        TREE.execute_process(0)
        app = self.get_exec_workflow_app()
        app._publish_shapes_and_metadata_to_manager()
        app._create_shared_memory()
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][0]))

    def test_must_send_signal_and_wait_for_respose(self):
        app = self.get_exec_workflow_app()
        _sig = app.must_send_signal_and_wait_for_response()
        self.assertEqual(_sig, "::shapes_not_set::")

    def test_must_send_signal_and_wait_for_response__shapes_set(self):
        app = self.get_exec_workflow_app()
        app.mp_manager["shapes_set"].set()
        _sig = app.must_send_signal_and_wait_for_response()
        self.assertIsNone(_sig)

    def test_get_latest_results__shapes_not_set(self):
        main_app, app = self.get_main_app_and_app_clone()
        self.assertIsNone(app.get_latest_results())

    def test_get_latest_results__shapes_set(self):
        main_app, app = self.get_main_app_and_app_clone()
        _ = main_app.multiprocessing_func(0)
        _index = app.get_latest_results()
        self.assertIsInstance(_index, Integral)
        for _key, _data in TREE.get_current_results().items():
            self.assertTrue(np.allclose(_data, app._shared_arrays[_key][_index]))

    def test_received_signal_message__shapes_not_set(self):
        main_app, app = self.get_main_app_and_app_clone()
        _index = app.multiprocessing_func(0)
        self.assertIsNone(_index)
        main_app.received_signal_message("::shapes_not_set::")
        self.assertTrue(main_app.mp_manager["shapes_set"].is_set())
        for _key in main_app.mp_manager["shapes_dict"]:
            self.assertIsInstance(main_app._shared_arrays[_key], np.ndarray)

    def test_multiprocessing_store_results_as_clone(self):
        main_app, app = self.get_main_app_and_app_clone()
        _spy = QtTest.QSignalSpy(app.sig_results_updated)
        _index = app.multiprocessing_func(0)
        app.multiprocessing_store_results(0, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 0)

    def test_multiprocessing_store_results__processing_error(self):
        main_app, _ = self.get_main_app_and_app_clone()
        _spy = QtTest.QSignalSpy(main_app.sig_results_updated)
        _index = main_app.multiprocessing_func(0)
        main_app.multiprocessing_store_results(0, -1)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 0)

    def test_multiprocessing_store_results(self):
        main_app, _ = self.get_main_app_and_app_clone()
        _spy = QtTest.QSignalSpy(main_app.sig_results_updated)
        _index = main_app.multiprocessing_func(0)
        main_app.multiprocessing_store_results(0, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 1)
        self.assertTrue(main_app._config["result_metadata_set"])
        self.assertTrue(
            np.all(RESULTS._composites[1][SCAN.get_index_position_in_scan(0)] > 0)
        )

    def test_multiprocessing_store_results__autosave(self):
        main_app, _ = self.get_main_app_and_app_clone()
        main_app.set_param_value("autosave_results", True)
        main_app.set_param_value("autosave_directory", self._path.joinpath("test"))
        _index = main_app.multiprocessing_func(0)
        main_app.multiprocessing_store_results(0, _index)
        _node_id = 1
        _fname = self._path.joinpath("test", f"node_{_node_id:02d}.h5")
        self.assertTrue(main_app._config["export_files_prepared"])
        with h5py.File(_fname, "r") as _f:
            _data = _f["entry/data/data"][SCAN.get_index_position_in_scan(0)]
            self.assertTrue(np.all(_data > 0))

    def test_multiprocessing_store_results__repetitive(self):
        main_app, _ = self.get_main_app_and_app_clone()
        _spy = QtTest.QSignalSpy(main_app.sig_results_updated)
        _i_dim = SCAN.ndim - 1
        for _i in range(SCAN.shape[_i_dim]):
            _index = main_app.multiprocessing_func(_i)
            main_app.multiprocessing_store_results(_i, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, SCAN.shape[_i_dim])
        _slices = (0,) * _i_dim + (
            slice(
                None,
            ),
        )
        self.assertTrue(np.all(RESULTS._composites[1][_slices] > 0))

    def test_multiprocessing_store_results__w_main_app_and_clone(self):
        main_app, app = self.get_main_app_and_app_clone()
        _spy = QtTest.QSignalSpy(main_app.sig_results_updated)
        _i_dim = SCAN.ndim - 1
        for _i in range(SCAN.shape[_i_dim]):
            _index = app.multiprocessing_func(_i)
            if _index is None:
                main_app._create_shared_memory()
                _index = app.get_latest_results()
            main_app.multiprocessing_store_results(_i, _index)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, SCAN.shape[_i_dim])
        _slices = (0,) * _i_dim + (
            slice(
                None,
            ),
        )
        self.assertTrue(np.all(RESULTS._composites[1][_slices] > 0))

    def test_run(self):
        app = self.get_exec_workflow_app()
        SCAN.set_param_value("scan_dim", 2)
        app.run()
        _res = RESULTS.get_results(1)
        self.assertTrue(np.all(_res > 0))

    def test_run__repetitive(self):
        app = self.get_exec_workflow_app()
        SCAN.set_param_value("scan_dim", 2)
        app.run()
        app.run()
        _res = RESULTS.get_results(1)
        self.assertTrue(np.all(_res > 0))

    def test_copy__to_clone(self):
        main_app = self.get_exec_workflow_app()
        for _key in ExecuteWorkflowApp.attributes_not_to_copy_to_app_clone:
            if _key == "_mp_manager_instance":
                continue
            setattr(main_app, _key, get_random_string(8))
        main_app._locals = {1: 1, 2: 2}
        main_app.mp_manager["shapes_available"].set()
        _copy = main_app.copy(clone_mode=True)
        self._apps.append(_copy)
        for _key in ExecuteWorkflowApp.attributes_not_to_copy_to_app_clone:
            if isinstance(getattr(main_app, _key), np.ndarray) and isinstance(
                getattr(_copy, _key), np.ndarray
            ):
                self.assertTrue(
                    np.allclose(getattr(main_app, _key), getattr(_copy, _key))
                )
            elif isinstance(getattr(main_app, _key), np.ndarray) != isinstance(
                getattr(_copy, _key), np.ndarray
            ):
                pass
            else:
                self.assertNotEqual(getattr(main_app, _key), getattr(_copy, _key))
        self.assertEqual(_copy._locals, {"shared_memory_buffers": {}})
        for _key in main_app.mp_manager:
            self.assertEqual(main_app.mp_manager[_key], _copy.mp_manager[_key])

    def test__run_in_processor_with_clone_worker(self):
        # logging.basicConfig(level=logging.DEBUG)
        self._main_app = self.get_exec_workflow_app(print_debug=True)
        _lock_manager = mp.Manager()
        _queues = {
            "queue_input": mp.Queue(),
            "queue_output": mp.Queue(),
            "queue_stop": mp.Queue(),
            "queue_shutting_down": mp.Queue(),
            "queue_signal": mp.Queue(),
        }
        _mp_kwargs = {
            "logging_level": LOGGING_LEVEL,
            "lock": _lock_manager.Lock(),
            **_queues,
        }
        _proc = mp.Process(
            target=app_processor,
            args=(
                _mp_kwargs,
                ExecuteWorkflowApp,
                self._main_app.params.copy(),
                self._main_app.get_config(),
            ),
            kwargs={
                "use_tasks": True,
                "app_mp_manager": self._main_app.mp_manager,
                "print_debug": True,
            },
            name=f"pydidas_{mp.current_process().pid}_worker",
        )
        for _i in range(SCAN.shape[-1]):
            _queues["queue_input"].put(_i)
        _proc.start()
        time.sleep(0.05)
        with self.assertRaises(queue.Empty):
            _res = _queues["queue_output"].get_nowait()
        _signal = _queues["queue_signal"].get()
        self.assertEqual(_signal, "::shapes_not_set::")
        self._main_app._create_shared_memory()
        time.sleep(0.05)
        for _i in range(SCAN.shape[-1]):
            _latest = _queues["queue_output"].get_nowait()
            self._main_app.multiprocessing_store_results(*_latest)
            self.assertEqual(_latest[0], _i)
            self.assertIsInstance(_latest[1], Integral)
            time.sleep(0.05)
        for _node in TREE.get_all_nodes_with_results():
            _id = _node.node_id
            _res = RESULTS.get_results(_id)
            self.assertTrue(np.all(_res[((0,) * (SCAN.ndim - 1)) + (slice(None),)] > 0))
        _queues["queue_stop"].put(1)
        _proc.join()
        time.sleep(0.05)

    def test__repeated_run_in_processor_with_clone_worker(self):
        self.test__run_in_processor_with_clone_worker()
        _ = self._apps.pop()
        self._main_app.deleteLater()
        self._main_app = None
        self.test__run_in_processor_with_clone_worker()


if __name__ == "__main__":
    print(
        "\n\nWarning: Calling test_execute_workflow_app.py as main is very slow. "
        "Please consider calling it with unittest discover option instead: \n"
        "python -m unittest discover .\\tests\\apps\\test_execute_workflow_app.py\n\n"
    )
    unittest.main()
