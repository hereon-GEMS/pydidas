# # This file is part of pydidas.
# #
# # Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
# # SPDX-License-Identifier: GPL-3.0-only
# #
# # pydidas is free software: you can redistribute it and/or modify
# # it under the terms of the GNU General Public License version 3 as
# # published by the Free Software Foundation.
# #
# # Pydidas is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with Pydidas. If not, see <http://www.gnu.org/licenses/>.
#
# """Unit tests for pydidas modules."""
#
# __author__ = "Malte Storm"
# __copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
# __license__ = "GPL-3.0-only"
# __maintainer__ = "Malte Storm"
# __status__ = "Production"
#
#
# import multiprocessing as mp
# import os
# import shutil
# import tempfile
# import threading
# import time
# import unittest
# from pathlib import Path
#
# import numpy as np
# from qtpy import QtWidgets
#
# from pydidas import unittest_objects
# from pydidas.apps import ExecuteWorkflowApp
# from pydidas.apps.parsers import execute_workflow_app_parser
# from pydidas.contexts import ScanContext
# from pydidas.core import PydidasQsettings, UserConfigError, get_generic_parameter, utils
# from pydidas.plugins import PluginCollection
# from pydidas.workflow import WorkflowResultsContext, WorkflowTree
# from pydidas.workflow.result_io import WorkflowResultIoMeta
# from pydidas_qtcore import PydidasQApplication
#
#
# TREE = WorkflowTree()
# SCAN = ScanContext()
# RESULTS = WorkflowResultsContext()
# RESULT_SAVER = WorkflowResultIoMeta
# COLL = PluginCollection()
#
#
# class TestLock(threading.Thread):
#     def __init__(self, memory_addresses, n_buffer, array_shapes):
#         super().__init__()
#         self._mem = memory_addresses
#         self._n_buffer = n_buffer
#         self._shapes = array_shapes
#         self._shared_arrays = {}
#         for _key, _shape in array_shapes.items():
#             _share = memory_addresses[_key]
#             _arr_shape = (n_buffer,) + _shape
#             self._shared_arrays[_key] = np.frombuffer(
#                 _share.get_obj(), dtype=np.float32
#             ).reshape(_arr_shape)
#         self._shared_arrays["flag"] = np.frombuffer(
#             memory_addresses["flag"].get_obj(), dtype=np.int32
#         )
#
#     def run(self):
#         self._mem["flag"].acquire()
#         self._shared_arrays["flag"][:] = 1
#         self._mem["flag"].release()
#         time.sleep(0.1)
#         self._mem["flag"].acquire()
#         self._shared_arrays["flag"][:] = 0
#         self._mem["flag"].release()
#
#
# def generate_tree():
#     TREE.clear()
#     TREE.create_and_add_node(unittest_objects.DummyLoader())
#     TREE.create_and_add_node(unittest_objects.DummyProc())
#     TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)
#
#
# class TestExecuteWorkflowApp(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         _app = QtWidgets.QApplication.instance()
#         if _app is None:
#             _ = PydidasQApplication([])
#         RESULTS.clear_all_results()
#         TREE.clear()
#         cls._path = tempfile.mkdtemp()
#         cls.generate_scan(cls)
#         cls.q_settings = PydidasQsettings()
#         cls._buf_size = cls.q_settings.value("global/shared_buffer_size", float)
#         cls._n_workers = cls.q_settings.value("global/mp_n_workers", int)
#         cls.__original_plugin_paths = COLL.registered_paths[:]
#         _path = Path(unittest_objects.__file__).parent
#         if _path not in COLL.registered_paths:
#             COLL.find_and_register_plugins(_path)
#
#     @classmethod
#     def tearDownClass(cls):
#         shutil.rmtree(cls._path)
#         cls.q_settings.set_value("global/shared_buffer_size", cls._buf_size)
#         cls.q_settings.set_value("global/mp_n_workers", cls._n_workers)
#         COLL.unregister_plugin_path(Path(unittest_objects.__file__).parent)
#
#     def setUp(self):
#         RESULT_SAVER.set_active_savers_and_title([])
#         generate_tree()
#         self.reset_scan_params()
#
#     def tearDown(self):
#         ExecuteWorkflowApp.parse_func = execute_workflow_app_parser
#
#     def generate_scan(self):
#         SCAN.restore_all_defaults(True)
#         SCAN.set_param_value("scan_dim", 3)
#         self._nscan = (9, 5, 7)
#         self._scandelta = (0.1, -0.2, 1.1)
#         self._scanoffset = (-5, 0, 1.2)
#
#     def reset_scan_params(self):
#         for i in range(3):
#             SCAN.set_param_value("scan_dim", 3)
#             SCAN.set_param_value(f"scan_dim{i}_n_points", self._nscan[i - 1])
#             SCAN.set_param_value(f"scan_dim{i}_delta", self._scandelta[i - 1])
#             SCAN.set_param_value(f"scan_dim{i}_offset", self._scanoffset[i - 1])
#
#     def test_creation(self):
#         app = ExecuteWorkflowApp()
#         self.assertIsInstance(app, ExecuteWorkflowApp)
#
#     def test_creation_with_args(self):
#         _autosave = get_generic_parameter("autosave_results")
#         _autosave.value = True
#         app = ExecuteWorkflowApp(_autosave)
#         self.assertTrue(app.get_param_value("autosave_results"))
#
#     def test_creation_with_cmdargs(self):
#         ExecuteWorkflowApp.parse_func = lambda x: {"autosave_results": True}
#         app = ExecuteWorkflowApp()
#         self.assertTrue(app.get_param_value("autosave_results"))
#
#     def test_store_context(self):
#         app = ExecuteWorkflowApp()
#         app._store_context()
#         self.assertEqual(app._config["result_shapes"], TREE.get_all_result_shapes())
#
#     def test_get_and_store_tasks(self):
#         app = ExecuteWorkflowApp()
#         app._mp_tasks = np.arange(SCAN.n_points)
#         self.assertTrue(np.allclose(app._mp_tasks, np.arange(np.prod(self._nscan))))
#
#     def test_check_size_of_results_and_calc_buffer_size__all_okay(self):
#         app = ExecuteWorkflowApp()
#         app._store_context()
#         app._mp_tasks = np.arange(SCAN.n_points)
#         app._check_size_of_results_and_buffer()
#         self.assertTrue(app._config["buffer_n"] > 0)
#
#     def test_check_size_of_results_and_calc_buffer_size__res_too_large(self):
#         app = ExecuteWorkflowApp()
#         app._config["result_shapes"] = {1: (10000, 10000), 2: (15000, 20000)}
#         with self.assertRaises(UserConfigError):
#             app._check_size_of_results_and_buffer()
#
#     def test_multiprocessing_pre_cycle(self):
#         _index = int(np.ceil(np.random.random() * 1e5))
#         app = ExecuteWorkflowApp()
#         app.multiprocessing_pre_cycle(_index)
#         self.assertEqual(_index, app._index)
#
#     def test_multiprocessing_post_run(self):
#         app = ExecuteWorkflowApp()
#         app.multiprocessing_post_run()
#         # assert does not raise an Exception
#
#     def test_multiprocessing_carryon__not_live(self):
#         app = ExecuteWorkflowApp()
#         app.set_param_value("live_processing", False)
#         self.assertTrue(app.multiprocessing_carryon())
#
#     def test_multiprocessing_carryon__live(self):
#         TREE.root.plugin.input_available = lambda x: x
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app.set_param_value("live_processing", True)
#         app._index = utils.get_random_string(8)
#         self.assertEqual(app.multiprocessing_carryon(), app._index)
#
#     def test_multiprocessing_carryon__waiting_for_shapes(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._waiting_for_shapes_to_be_set = True
#         self.assertFalse(app.multiprocessing_carryon())
#
#     def test_multiprocessing_pre_run(self):
#         app = ExecuteWorkflowApp()
#         app.multiprocessing_pre_run()
#         # assert does not raise error
#
#     def test_prepare_run__master_not_live_no_autosave(self):
#         app = ExecuteWorkflowApp()
#         app.set_param_value("autosave_results", False)
#         app.set_param_value("live_processing", False)
#         app.prepare_run()
#         self.assertIsInstance(app._shared_arrays[1], np.ndarray)
#         self.assertIsInstance(app._shared_arrays[2], np.ndarray)
#
#     def test_prepare_run__master_not_live_w_autosave(self):
#         app = ExecuteWorkflowApp()
#         app.set_param_value("autosave_results", True)
#         app.set_param_value("autosave_directory", self._path)
#         app.set_param_value("live_processing", False)
#         app.prepare_run()
#         self.assertTrue(os.path.exists(os.path.join(self._path, "node_01.h5")))
#         self.assertTrue(os.path.exists(os.path.join(self._path, "node_02.h5")))
#
#     def test_prepare_run__slave_not_live_no_autosave(self):
#         app = ExecuteWorkflowApp()
#         app.set_param_value("autosave_results", False)
#         app.set_param_value("live_processing", False)
#         app.prepare_run()
#         SCAN.set_param_value("scan_dim3_offset", -12345)
#         app2 = app.copy(slave_mode=True)
#         SCAN.set_param_value("scan_dim3_offset", 0)
#         app2.prepare_run()
#         self.assertIsInstance(app2._shared_arrays[1], np.ndarray)
#         self.assertIsInstance(app2._shared_arrays[2], np.ndarray)
#         self.assertEqual(
#             app._config["shared_memory"][1], app2._config["shared_memory"][1]
#         )
#         self.assertEqual(
#             app._config["shared_memory"][2], app2._config["shared_memory"][2]
#         )
#
#     def test_prepare_run__master_live_no_autosave(self):
#         app = ExecuteWorkflowApp()
#         app.set_param_value("autosave_results", False)
#         app.set_param_value("live_processing", True)
#         app.prepare_run()
#         app._index = 1
#         self.assertIsInstance(app._shared_arrays[1], np.ndarray)
#         self.assertIsInstance(app._shared_arrays[2], np.ndarray)
#
#     def test_initialize_shared_memory(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._mp_tasks = np.arange(SCAN.n_points)
#         app.mp_manager["shape_dict"] = {1: (10, 10), 2: (10, 10)}
#         app.mp_manager["shapes_available"].set()
#         app.initialize_shared_memory()
#         self.assertTrue(app.mp_manager["shapes_set"].is_set())
#         self.assertTrue(app._config["buffer_n"] > 0)
#         for _key in list(app.mp_manager["shape_dict"].keys()) + ["flag"]:
#             self.assertIsInstance(
#                 app.mp_manager[f"arr_{_key}"], mp.sharedctypes.SynchronizedArray
#             )
#
#     def test_initialize_shared_memory__no_shapes_available(self):
#         app = ExecuteWorkflowApp()
#         with self.assertRaises(UserConfigError):
#             app.initialize_shared_memory()
#
#     def test_initialize_arrays_from_shared_memory(self):
#         app = ExecuteWorkflowApp()
#         app._mp_tasks = np.arange(SCAN.n_points)
#         app.mp_manager["shape_dict"] = {1: (10, 10), 2: (10, 10)}
#         app.initialize_shared_memory()
#         app._ExecuteWorkflowApp__initialize_arrays_from_shared_memory()
#         _n = app._config["buffer_n"]
#         for key in app._shared_arrays:
#             if key == "flag":
#                 _target = (_n,)
#             else:
#                 _target = (_n,) + app._config["result_shapes"][key]
#             self.assertEqual(app._shared_arrays[key].shape, _target)
#
#     def test_multiprocessing_get_tasks__normal(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         _tasks = app.multiprocessing_get_tasks()
#         self.assertEqual(_tasks.size, np.prod(self._nscan))
#
#     def test_multiprocessing_get_tasks__no_tasks(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#
#     def test_multiprocessing_func__no_metadata(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         _res = app.multiprocessing_func(_index)
#         self.assertIsInstance(_res, tuple)
#         self.assertEqual(_res[0], 0)
#         self.assertIsInstance(_res[1], dict)
#
#     def test_multiprocessing_func__metadata_set(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._config["result_metadata_set"] = True
#         _pos0 = app.multiprocessing_func(_index)
#         _pos1 = app.multiprocessing_func(_index + 1)
#         self.assertEqual(_pos0, 0)
#         self.assertEqual(_pos1, 1)
#
#     def test_write_results_to_shared_arrays(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         TREE.execute_process(0)
#         self.assertTrue((app._shared_arrays[1][0] == 0).all())
#         self.assertTrue((app._shared_arrays[2][0] == 0).all())
#         app._ExecuteWorkflowApp__write_results_to_shared_arrays()
#         self.assertTrue((app._shared_arrays[1][0] > 0).all())
#         self.assertTrue((app._shared_arrays[2][0] > 0).all())
#
#     def test_multiprocessing_store_results__plain(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._config["result_metadata_set"] = True
#         _pos = app.multiprocessing_func(_index)
#         self.assertEqual(app._shared_arrays["flag"][0], 1)
#         app.multiprocessing_store_results(_index, _pos)
#         self.assertEqual(app._shared_arrays["flag"][0], 0)
#
#     def test_multiprocessing_store_results__slave(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app.slave_mode = True
#         app._config["result_metadata_set"] = True
#         _pos = app.multiprocessing_func(_index)
#         app.multiprocessing_store_results(_index, _pos)
#         self.assertEqual(app._shared_arrays["flag"][0], 1)
#
#     def test_multiprocessing_store_results__with_metadata(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         _res = app.multiprocessing_func(_index)
#         app._config["result_metadata_set"] = False
#         self.assertEqual(app._shared_arrays["flag"][0], 1)
#         app.multiprocessing_store_results(_index, _res)
#         self.assertEqual(app._shared_arrays["flag"][0], 0)
#
#     def test_multiprocessing_store_results__with_autosave(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app.set_param_value("autosave_results", True)
#         _pos = app.multiprocessing_func(_index)
#         self.assertEqual(app._shared_arrays["flag"][0], 1)
#         app.multiprocessing_store_results(_index, _pos)
#         self.assertEqual(app._shared_arrays["flag"][0], 0)
#
#     def test_store_result_metadata__with_dataset(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._config["result_metadata_set"] = False
#         TREE.execute_process(_index)
#         app._ExecuteWorkflowApp__store_result_metadata()
#         self.assertTrue(app._config["result_metadata_set"])
#
#     def test_store_result_metadata__with_ndarray(self):
#         _index = 12
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app._config["result_metadata_set"] = False
#         TREE.execute_process(_index)
#         for _node_id in app._config["result_shapes"]:
#             TREE.nodes[_node_id].results = np.ones((10, 10))
#         app._ExecuteWorkflowApp__store_result_metadata()
#         self.assertTrue(app._config["result_metadata_set"])
#
#     def test_write_results_to_shared_arrays__lock_test(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         TREE.execute_process(0)
#         _locker = TestLock(
#             app._config["shared_memory"],
#             app._config["buffer_n"],
#             app._config["result_shapes"],
#         )
#         _locker.start()
#         app._ExecuteWorkflowApp__write_results_to_shared_arrays()
#
#     def test_store_frame_metadata(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         TREE.execute_process(0)
#         app._config["result_metadata_set"] = False
#         _metadata = {}
#         for _id in app._config["result_shapes"]:
#             _res = TREE.nodes[_id].results
#             _metadata[_id] = {
#                 "axis_labels": _res.axis_labels,
#                 "axis_units": _res.axis_units,
#                 "axis_ranges": _res.axis_ranges,
#             }
#         app._store_frame_metadata(_metadata)
#         self.assertTrue(app._config["result_metadata_set"])
#
#     def test_run__single_processing(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app.run()
#         # assert does not raise Exception
#
#     def test_run__multiple_runs(self):
#         app = ExecuteWorkflowApp()
#         app.prepare_run()
#         app.run()
#         app.run()
#         # assert does not raise Exception
#
#
# if __name__ == "__main__":
#     unittest.main()
