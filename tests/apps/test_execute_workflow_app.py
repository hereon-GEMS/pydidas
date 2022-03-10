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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import tempfile
import shutil
import random
import os
import threading
import time
import multiprocessing as mp

import numpy as np
from qtpy import QtCore

from pydidas import unittest_objects
from pydidas.core import get_generic_parameter, AppConfigError, utils
from pydidas.apps import ExecuteWorkflowApp
from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.experiment import ScanSetup
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.workflow.result_savers import WorkflowResultSaverMeta
from pydidas.plugins import PluginCollection


TREE = WorkflowTree()
SCAN = ScanSetup()
RESULTS = WorkflowResults()
RESULT_SAVER = WorkflowResultSaverMeta
COLL = PluginCollection()
_PLUGIN_PATHS = COLL.get_all_registered_paths()


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
                _share.get_obj(), dtype=np.float32).reshape(_arr_shape)
        self._shared_arrays['flag'] = np.frombuffer(
                memory_addresses['flag'].get_obj(), dtype=np.int32)

    def run(self):
        self._mem['flag'].acquire()
        self._shared_arrays['flag'][:] = 1
        self._mem['flag'].release()
        time.sleep(0.1)
        self._mem['flag'].acquire()
        self._shared_arrays['flag'][:] = 0
        self._mem['flag'].release()


class TestExecuteWorkflowApp(unittest.TestCase):

    def setUp(self):
        RESULT_SAVER.set_active_savers_and_title([])
        self._path = tempfile.mkdtemp()
        self.generate_tree()
        self.generate_scan()
        self.q_settings = QtCore.QSettings('Hereon', 'pydidas')
        self._buf_size = float(
            self.q_settings.value('global/shared_buffer_size'))
        self._n_workers = int(self.q_settings.value('global/mp_n_workers'))
        _path = os.path.dirname(unittest_objects.__file__)
        if _path not in _PLUGIN_PATHS:
            COLL.find_and_register_plugins(_path)

    def tearDown(self):
        shutil.rmtree(self._path)
        self.q_settings.setValue('global/shared_buffer_size', self._buf_size)
        self.q_settings.setValue('global/mp_n_workers', self._n_workers)
        ExecuteWorkflowApp.parse_func = (
            execute_workflow_app_parser)
        COLL.clear_collection(True)
        COLL.find_and_register_plugins(*_PLUGIN_PATHS)

    def generate_tree(self):
        TREE.clear()
        TREE.create_and_add_node(unittest_objects.DummyLoader())
        TREE.create_and_add_node(unittest_objects.DummyProc())
        TREE.create_and_add_node(unittest_objects.DummyProc(),
                                 parent=TREE.root)

    def generate_scan(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value('scan_dim', 3)
        self._nscan = (random.choice([5,7,9,11]), random.choice([2, 4, 5]),
                       random.choice([5,6,7,8]))
        self._scandelta = (0.1, -0.2, 1.1)
        self._scanoffset = (-5, 0, 1.2)
        for i in range(1, 4):
            SCAN.set_param_value('scan_dim', 3)
            SCAN.set_param_value(f'n_points_{i}', self._nscan[i-1])
            SCAN.set_param_value(f'delta_{i}', self._scandelta[i-1])
            SCAN.set_param_value(f'offset_{i}', self._scanoffset[i-1])

    def test_creation(self):
        app = ExecuteWorkflowApp()
        self.assertIsInstance(app, ExecuteWorkflowApp)

    def test_creation_with_args(self):
        _autosave = get_generic_parameter('autosave_results')
        _autosave.value = True
        app = ExecuteWorkflowApp(_autosave)
        self.assertTrue(app.get_param_value('autosave_results'))

    def test_creation_with_cmdargs(self):
        ExecuteWorkflowApp.parse_func = lambda x: {'autosave_results': True}
        app = ExecuteWorkflowApp()
        self.assertTrue(app.get_param_value('autosave_results'))

    def test_multiprocessing_pre_run(self):
        app = ExecuteWorkflowApp()
        app.multiprocessing_pre_run()
        # assert does not raise error

    def test_multiprocessing_carryon(self):
        app = ExecuteWorkflowApp()
        self.assertTrue(app.multiprocessing_carryon())

    def test_prepare_run__master_not_live_no_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value('autosave_results', False)
        app.set_param_value('live_processing', False)
        app.prepare_run()
        self.assertIsInstance(app._shared_arrays[1], np.ndarray)
        self.assertIsInstance(app._shared_arrays[2], np.ndarray)
        self.assertTrue(app.multiprocessing_carryon())

    def test_prepare_run__master_not_live_w_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value('autosave_results', True)
        app.set_param_value('autosave_dir', self._path)
        app.set_param_value('live_processing', False)
        app.prepare_run()
        self.assertTrue(os.path.exists(os.path.join(self._path, 'node_01.h5')))
        self.assertTrue(os.path.exists(os.path.join(self._path, 'node_02.h5')))

    def test_prepare_run__slave_not_live_no_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value('autosave_results', False)
        app.set_param_value('live_processing', False)
        app.prepare_run()
        SCAN.set_param_value('offset_4', -12345)
        app2 = app.get_copy(slave_mode=True)
        SCAN.set_param_value('offset_4', 0)
        app2.prepare_run()
        self.assertIsInstance(app2._shared_arrays[1], np.ndarray)
        self.assertIsInstance(app2._shared_arrays[2], np.ndarray)
        self.assertEqual(app._config['shared_memory'][1],
                         app2._config['shared_memory'][1])
        self.assertEqual(app._config['shared_memory'][2],
                         app2._config['shared_memory'][2])
        self.assertTrue(app.multiprocessing_carryon())

    def test_prepare_run__master_live_no_autosave(self):
        app = ExecuteWorkflowApp()
        app.set_param_value('autosave_results', False)
        app.set_param_value('live_processing', True)
        app.prepare_run()
        app._index = 1
        self.assertIsInstance(app._shared_arrays[1], np.ndarray)
        self.assertIsInstance(app._shared_arrays[2], np.ndarray)
        self.assertTrue(app.multiprocessing_carryon())

    def test_check_and_store_results_shapes(self):
        app = ExecuteWorkflowApp()
        app._ExecuteWorkflowApp__check_and_store_result_shapes()
        self.assertEqual(app._config['result_shapes'],
                         TREE.get_all_result_shapes())

    def test_get_and_store_tasks(self):
        app = ExecuteWorkflowApp()
        app._ExecuteWorkflowApp__get_and_store_tasks()
        self.assertTrue(np.equal(app._mp_tasks,
                                 np.arange(np.prod(self._nscan))).all())

    def test_check_size_of_results_and_calc_buffer_size__all_okay(self):
        app = ExecuteWorkflowApp()
        app._ExecuteWorkflowApp__check_and_store_result_shapes()
        app._ExecuteWorkflowApp__get_and_store_tasks()
        app._ExecuteWorkflowApp__check_size_of_results_and_calc_buffer_size()
        self.assertTrue(app._config['buffer_n'] > 0)

    def test_check_size_of_results_and_calc_buffer_size__res_too_large(self):
        app = ExecuteWorkflowApp()
        app._config['result_shapes'] = {1: (10000, 10000), 2: (15000, 20000)}
        with self.assertRaises(AppConfigError):
            app._ExecuteWorkflowApp__check_size_of_results_and_calc_buffer_size()

    def test_initialize_shared_memory(self):
        app = ExecuteWorkflowApp()
        app._ExecuteWorkflowApp__get_and_store_tasks()
        app._ExecuteWorkflowApp__check_and_store_result_shapes()
        app._ExecuteWorkflowApp__check_size_of_results_and_calc_buffer_size()
        app._ExecuteWorkflowApp__initialize_shared_memory()
        for key in app._config['shared_memory']:
            self.assertIsInstance(app._config['shared_memory'][key],
                                  mp.sharedctypes.SynchronizedArray)

    def test_initialize_arrays_from_shared_memory(self):
        app = ExecuteWorkflowApp()
        app._ExecuteWorkflowApp__get_and_store_tasks()
        app._ExecuteWorkflowApp__check_and_store_result_shapes()
        app._ExecuteWorkflowApp__check_size_of_results_and_calc_buffer_size()
        app._ExecuteWorkflowApp__initialize_shared_memory()
        app._ExecuteWorkflowApp__initialize_arrays_from_shared_memory()
        _n = app._config['buffer_n']
        for key in app._shared_arrays:
            if key == 'flag':
                _target = (_n,)
            else:
                _target = (_n, ) + app._config['result_shapes'][key]
            self.assertEqual(app._shared_arrays[key].shape, _target)

    def test_redefine_multiprocessing_carryon__not_live(self):
        app = ExecuteWorkflowApp()
        app._redefine_multiprocessing_carryon()
        self.assertTrue(app.multiprocessing_carryon())

    def test_redefine_multiprocessing_carryon__live(self):
        TREE.root.plugin.input_available = lambda x: x
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.set_param_value('live_processing', True)
        app._redefine_multiprocessing_carryon()
        app._index = utils.get_random_string(8)
        self.assertEqual(app.multiprocessing_carryon(), app._index)

    def test_multiprocessing_get_tasks__normal(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _tasks = app.multiprocessing_get_tasks()
        self.assertEqual(_tasks.size, np.prod(self._nscan))

    def test_multiprocessing_get_tasks__no_tasks(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()

    def test_multiprocessing_pre_cycle(self):
        _index = int(np.ceil(np.random.random() * 1e5))
        app = ExecuteWorkflowApp()
        app.multiprocessing_pre_cycle(_index)
        self.assertEqual(_index, app._index)

    def test_multiprocessing_func__no_metadata(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _res = app.multiprocessing_func(_index)
        self.assertIsInstance(_res, tuple)
        self.assertEqual(_res[0], 0)
        self.assertIsInstance(_res[1], dict)

    def test_multiprocessing_func__metadata_set(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._config['result_metadata_set'] = True
        _pos0 = app.multiprocessing_func(_index)
        _pos1 = app.multiprocessing_func(_index + 1)
        self.assertEqual(_pos0, 0)
        self.assertEqual(_pos1, 1)

    def test_write_results_to_shared_arrays(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        TREE.execute_process(0)
        self.assertTrue((app._shared_arrays[1][0] == 0).all())
        self.assertTrue((app._shared_arrays[2][0] == 0).all())
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()
        self.assertTrue((app._shared_arrays[1][0] > 0).all())
        self.assertTrue((app._shared_arrays[2][0] > 0).all())

    def test_multiprocessing_store_results__plain(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._config['result_metadata_set'] = True
        _pos = app.multiprocessing_func(_index)
        self.assertEqual(app._shared_arrays['flag'][0], 1)
        app.multiprocessing_store_results(_index, _pos)
        self.assertEqual(app._shared_arrays['flag'][0], 0)

    def test_multiprocessing_store_results__slave(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.slave_mode = True
        app._config['result_metadata_set'] = True
        _pos = app.multiprocessing_func(_index)
        app.multiprocessing_store_results(_index, _pos)
        self.assertEqual(app._shared_arrays['flag'][0], 1)

    def test_multiprocessing_store_results__with_metadata(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        _res = app.multiprocessing_func(_index)
        app._config['result_metadata_set'] = False
        self.assertEqual(app._shared_arrays['flag'][0], 1)
        app.multiprocessing_store_results(_index, _res)
        self.assertEqual(app._shared_arrays['flag'][0], 0)

    def test_multiprocessing_store_results__with_autosave(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.set_param_value('autosave_results', True)
        _pos = app.multiprocessing_func(_index)
        self.assertEqual(app._shared_arrays['flag'][0], 1)
        app.multiprocessing_store_results(_index, _pos)
        self.assertEqual(app._shared_arrays['flag'][0], 0)

    def test_multiprocesssing_post_run(self):
        app = ExecuteWorkflowApp()
        app.multiprocessing_post_run()
        # assert does not raise an Exception

    def test_store_result_metadata__with_dataset(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._config['result_metadata_set'] = False
        TREE.execute_process(_index)
        app._ExecuteWorkflowApp__store_result_metadata()
        self.assertTrue(app._config['result_metadata_set'])

    def test_store_result_metadata__with_ndarray(self):
        _index = 12
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app._config['result_metadata_set'] = False
        TREE.execute_process(_index)
        for _node_id in app._config['result_shapes']:
            TREE.nodes[_node_id].results = np.ones((10, 10))
        app._ExecuteWorkflowApp__store_result_metadata()
        self.assertTrue(app._config['result_metadata_set'])

    def test_write_results_to_shared_arrays__lock_test(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        TREE.execute_process(0)
        _locker = TestLock(app._config['shared_memory'],
                           app._config['buffer_n'],
                           app._config['result_shapes'])
        _locker.start()
        app._ExecuteWorkflowApp__write_results_to_shared_arrays()

    def test_store_frame_metadata(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        TREE.execute_process(0)
        app._config['result_metadata_set'] = False
        _metadata = {}
        for _id in app._config['result_shapes']:
            _res = TREE.nodes[_id].results
            _metadata[_id] = {'axis_labels': _res.axis_labels,
                              'axis_units': _res.axis_units,
                              'axis_ranges': _res.axis_ranges}
        app._store_frame_metadata(_metadata)
        self.assertTrue(app._config['result_metadata_set'])

    def test_run__single_processing(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.run()
        #assert does not raise Exception

    def test_run__multiple_runs(self):
        app = ExecuteWorkflowApp()
        app.prepare_run()
        app.run()
        app.run()
        #assert does not raise Exception


if __name__ == "__main__":
    unittest.main()
