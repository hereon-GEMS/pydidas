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


import shutil
import tempfile
import unittest
from numbers import Integral

import numpy as np
from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.plugins import PluginCollection
from pydidas.unittest_objects import DummyLoader, DummyProc, DummyProcNewDataset
from pydidas.workflow import WorkflowResultsContext, WorkflowTree
from pydidas.workflow.result_io import WorkflowResultIoMeta
from pydidas.workflow.workflow_results_selector import WorkflowResultsSelector


PLUGINS = PluginCollection()
SCAN = ScanContext()
TREE = WorkflowTree()
RES = WorkflowResultsContext()
SAVER = WorkflowResultIoMeta


class TestWorkflowResultSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TREE.clear()
        SCAN.restore_all_defaults(True)
        RES.clear_all_results()
        for _cls in (DummyLoader, DummyProc, DummyProcNewDataset):
            PLUGINS.check_and_register_class(_cls)
        PLUGINS.verify_is_initialized()

    @classmethod
    def tearDownClass(cls):
        for _cls in (DummyLoader, DummyProc, DummyProcNewDataset):
            PLUGINS.remove_plugin_from_collection(_cls)

    def setUp(self):
        self.set_up_scan()
        self.set_up_tree()
        RES.clear_all_results()
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def set_up_scan(self):
        self._scan_n = (5, 2, 3)
        self._scan_offsets = (-3, 0, 3.2)
        self._scan_delta = (0.1, 1, 12)
        self._scan_unit = ("m", "mm", "m")
        self._scan_label = ("Test", "Dir 2", "other dim")
        SCAN.set_param_value("scan_dim", len(self._scan_n))
        for _dim in range(len(self._scan_n)):
            SCAN.set_param_value(f"scan_dim{_dim}_n_points", self._scan_n[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_offset", self._scan_offsets[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_delta", self._scan_delta[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_unit", self._scan_unit[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_label", self._scan_label[_dim])

    def set_up_tree(self):
        self._result1_shape = (12, 27)
        self._result2_shape = (3, 3, 5)
        TREE.clear()
        TREE.create_and_add_node(DummyLoader())
        TREE.nodes[0].plugin.set_param_value("image_height", self._result1_shape[0])
        TREE.nodes[0].plugin.set_param_value("image_width", self._result1_shape[1])
        TREE.create_and_add_node(DummyProc())
        TREE.create_and_add_node(
            DummyProcNewDataset(output_shape=self._result2_shape), parent=TREE.root
        )
        TREE.create_and_add_node(
            DummyProcNewDataset(output_shape=(1,)), parent=TREE.root
        )
        TREE.prepare_execution()

    def populate_WorkflowResults(self):
        RES._config["frozen_TREE"].update_from_tree(TREE)
        RES.prepare_new_results()
        _results = {
            1: Dataset(
                np.random.random(self._result1_shape),
                axis_units=["m", "mm"],
                axis_labels=["dim1", "dim 2"],
                axis_ranges=[
                    np.arange(self._result1_shape[0]),
                    37 - np.arange(self._result1_shape[1]),
                ],
            ),
            2: Dataset(
                np.random.random(self._result2_shape),
                axis_units=["m", "Test", ""],
                axis_labels=["dim1", "2nd dim", "dim #3"],
                axis_ranges=[12 + np.arange(self._result2_shape[0]), None, None],
            ),
            3: Dataset(
                np.random.random((1,)),
                axis_units=["m"],
                axis_labels=["dim1"],
                axis_ranges=[12],
            ),
        }
        RES.store_results(0, _results)
        RES._composites[1][:] = (
            np.random.random(self._scan_n + self._result1_shape) + 0.0001
        )
        RES._composites[2][:] = (
            np.random.random(self._scan_n + self._result2_shape) + 0.0001
        )

    def test_unitttest_setUp(self): ...

    def test_populate_WorkflowResults(self):
        self.populate_WorkflowResults()
        for _index in [1, 2]:
            _res = RES.get_results(_index)
            self.assertEqual(
                _res.shape, self._scan_n + getattr(self, f"_result{_index}_shape")
            )
            self.assertTrue(np.all(_res > 0))

    def test_init(self):
        obj = WorkflowResultsSelector()
        self.assertIsInstance(obj, WorkflowResultsSelector)
        self.assertTrue("_selection" in obj.__dict__)
        self.assertTrue("_npoints" in obj.__dict__)
        self.assertTrue("active_node" in obj._config)
        self.assertEqual(obj._SCAN, RES.frozen_scan)
        self.assertEqual(obj._RESULTS, RES)

    def test_init__with_param(self):
        _param = Parameter("result_n_dim", int, 124)
        obj = WorkflowResultsSelector(_param)
        self.assertIsInstance(obj, WorkflowResultsSelector)
        self.assertEqual(_param, obj.get_param("result_n_dim"))

    def test_re_pattern__int_selection(self):
        obj = WorkflowResultsSelector()
        _str = "1, 4, 5:7, 5:5 : 8, 5, 9"
        self.assertTrue(bool(obj._re_pattern.fullmatch(_str)))

    def test_re_pattern__float_selection(self):
        obj = WorkflowResultsSelector()
        _str = "1.6, 4.5, 5.7:7.9, 5.9:5:8.2, 5.2, 9, 1:1.2:4.2"
        self.assertTrue(bool(obj._re_pattern.fullmatch(_str)))

    def test_reset(self):
        obj = WorkflowResultsSelector()
        obj._config["active_node"] = 12
        obj._selection = [1, 2, 3]
        obj.reset()
        self.assertIsNone(obj._selection)
        self.assertEqual(obj._config["active_node"], -1)

    def test_check_and_create_params_for_slice_selection(self):
        self.populate_WorkflowResults()
        _ndim = len(self._scan_n) + len(self._result2_shape)
        obj = WorkflowResultsSelector()
        obj._config["active_node"] = 2
        obj._check_and_create_params_for_slice_selection()
        for _dim in range(_ndim):
            self.assertIn(f"data_slice_{_dim}", obj.params)
        self.assertNotIn(f"data_slice_{_ndim}", obj.params)

    def test_calc_and_store_ndim_of_results__no_timeline(self):
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj._config["active_node"] = 2
        obj._calc_and_store_ndim_of_results()
        self.assertEqual(
            obj._config["result_ndim"], len(self._scan_n) + len(self._result2_shape)
        )

    def test_calc_and_store_ndim_of_results__with_timeline(self):
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj._config["active_node"] = 2
        obj.set_param_value("use_scan_timeline", True)
        obj._calc_and_store_ndim_of_results()
        self.assertEqual(obj._config["result_ndim"], 1 + len(self._result2_shape))

    def test_select_active_node(self):
        _node = 2
        self.populate_WorkflowResults()
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        self.assertEqual(obj._config["active_node"], _node)
        self.assertIsNotNone(obj._config.get("result_ndim", None))

    def test_check_for_selection_dim__no_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__0d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 0)
        with self.assertRaises(UserConfigError):
            obj._check_for_selection_dim(_selection)

    def test_check_for_selection_dim__0d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[42], np.r_[3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 0)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__1d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 1)
        with self.assertRaises(UserConfigError):
            obj._check_for_selection_dim(_selection)

    def test_check_for_selection_dim__1d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[6], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 1)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__2d_check_okay(self):
        _selection = (np.r_[0], np.r_[0], np.r_[6, 5], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 2)
        obj._check_for_selection_dim(_selection)
        # assert does not raise an Exception

    def test_check_for_selection_dim__6d_check(self):
        _selection = (np.r_[0], np.r_[0], np.r_[1, 2, 3], np.r_[1, 2, 3], np.r_[2])
        obj = WorkflowResultsSelector()
        obj.set_param_value("result_n_dim", 6)
        with self.assertRaises(UserConfigError):
            obj._check_for_selection_dim(_selection)

    def test_get_single_slice_object__empty_str(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index])

    def test_get_single_slice_object__simple_colon(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", ":")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index])

    def test_get_single_slice_object__sliced(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "1:-1")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 2)

    def test_get_single_slice_object__multiple_single_numbers(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "1, 3, 5, 6, 7")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 5)

    def test_get_single_slice_object__multiple_numbers_w_duplicates(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "1, 3, 5, 1, 5")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 3)

    def test_get_single_slice_object__multiple_slices(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "0:2, 4:6")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 4)

    def test_get_single_slice_object__multiple_slices_scan_timeline(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 0
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", True)
        obj.set_param_value("use_scan_timeline", True)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "0:2, 4:6")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 6)

    def test_get_single_slice_object__multiple_slices_and_numbers(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "1:4, 3, 4, 6:8")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 6)

    def test_get_single_slice_object__slice_w_open_end(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "1:")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 1)

    def test_get_single_slice_object__slice_w_open_start(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", ":-1")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, RES.shapes[_node][_index] - 1)

    def test_get_single_slice_object__slice_w_stepping(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "0:12:2")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, 6)

    def test_get_single_slice_object__slice_w_stepping_only(self):
        self.populate_WorkflowResults()
        _node = 1
        _index = 4
        _arrsize = RES.shapes[_node][_index]
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        obj._npoints = list(RES.shapes[obj._config["active_node"]])
        obj.set_param_value(f"data_slice_{_index}", "::2")
        _slice = obj._get_single_slice_object(_index)
        self.assertEqual(_slice.size, _arrsize // 2 + _arrsize % 2)

    def test_update_selection__simple(self):
        self.populate_WorkflowResults()
        _node = 1
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1:")
        obj._update_selection()
        _delta = [
            RES.shapes[_node][_i] - obj._selection[_i].size
            for _i in range(RES.ndims[_node])
        ]
        self.assertEqual(_delta, [1] * RES.ndims[_node])

    def test_update_selection__with_use_scan_timeline(self):
        TREE.prepare_execution()
        TREE.execute_process(0)
        self.populate_WorkflowResults()
        _node = 1
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_scan_timeline", True)
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node] - 2):
            obj.set_param_value(f"data_slice_{_index}", "1:")
        obj._update_selection()
        self.assertEqual(len(obj.selection), RES.ndims[_node] - 2)
        self.assertTrue(np.allclose(obj.selection[0], np.arange(1, SCAN.n_points)))
        self.assertTrue(
            np.allclose(
                obj.selection[1], np.arange(1, TREE.nodes[_node].result_shape[0])
            )
        )
        self.assertTrue(
            np.allclose(
                obj.selection[2], np.arange(1, TREE.nodes[_node].result_shape[1])
            )
        )

    def test_get_best_index_for_value__low_val(self):
        _val = 42
        _range = np.arange(45, 105)
        obj = WorkflowResultsSelector()
        _match = obj.get_best_index_for_value(_val, _range)
        self.assertEqual(_match, 0)

    def test_get_best_index_for_value__high_val(self):
        _val = 42
        _range = np.arange(0, 37)
        obj = WorkflowResultsSelector()
        _match = obj.get_best_index_for_value(_val, _range)
        self.assertEqual(_match, _range.size - 1)

    def test_get_best_index_for_value__middle_val(self):
        _val = 42
        _range = np.arange(12, 47, 0.5)
        _target = (_val - _range[0]) / (_range[1] - _range[0])
        obj = WorkflowResultsSelector()
        _match = obj.get_best_index_for_value(_val, _range)
        self.assertEqual(_match, _target)

    def test_get_best_index_for_value__None_range(self):
        _val = 42
        _range = None
        obj = WorkflowResultsSelector()
        _match = obj.get_best_index_for_value(_val, _range)
        self.assertEqual(_match, _val)
        self.assertIsInstance(_match, Integral)

    def test_get_best_index_for_value__None_range_and_float_value(self):
        _val = 42.0
        _range = None
        obj = WorkflowResultsSelector()
        _match = obj.get_best_index_for_value(_val, _range)
        self.assertEqual(_match, _val)
        self.assertIsInstance(_match, Integral)

    def test_convert_values_to_indices(self):
        _target_range = np.arange(12, 78)
        _data = 12 - np.arange(0, 89, 0.5)
        _start = _data[_target_range[0]]
        _stop = _data[_target_range[-1]]
        obj = WorkflowResultsSelector()
        obj._config["active_index"] = 0
        obj._config["active_ranges"] = {0: _data}
        obj._config["index_defaults"] = [0, _data.size, 1]
        _str = [f"{_start}:{_stop}"]
        _res = obj._convert_values_to_indices(_str)
        self.assertEqual(_res[0], [_target_range[0], _target_range[-1]])

    def test_active_dims__no_active_dim(self):
        self.populate_WorkflowResults()
        _node = 1
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        self.assertEqual(obj.active_dims, [])

    def test_active_dims__one_active_dim__w_indices(self):
        self.populate_WorkflowResults()
        _node = 1
        _dim = 2
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        obj.set_param_value(f"data_slice_{_dim}", "1:")
        self.assertEqual(obj.active_dims, [_dim])

    def test_active_dims__one_active_dim__w_data_range(self):
        self.populate_WorkflowResults()
        _node = 1
        _dim = 3
        _value = RES.get_result_ranges(_node)[_dim][4]
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", True)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        obj.set_param_value(f"data_slice_{_dim}", f"{_value}:")
        self.assertEqual(obj.active_dims, [_dim])

    def test_active_dims__two_active_dim__w_indices(self):
        self.populate_WorkflowResults()
        _node = 1
        _dim1 = 2
        _dim2 = 0
        _res = [_dim1, _dim2]
        _res.sort()
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        obj.set_param_value(f"data_slice_{_dim1}", "1:")
        obj.set_param_value(f"data_slice_{_dim2}", ":")
        self.assertEqual(obj.active_dims, _res)

    def test_active_dims__two_active_dim__w_data_range(self):
        self.populate_WorkflowResults()
        _node = 1
        _dim1 = 2
        _dim2 = 0
        _res = [_dim1, _dim2]
        _res.sort()
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", True)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        obj.set_param_value(f"data_slice_{_dim1}", ":")
        obj.set_param_value(f"data_slice_{_dim2}", ":")
        self.assertEqual(obj.active_dims, _res)

    def test_active_dims__three_active_dim__w_indices(self):
        self.populate_WorkflowResults()
        _node = 1
        _res = [0, 2, 3]
        _res.sort()
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        for _dim in _res:
            obj.set_param_value(f"data_slice_{_dim}", "1:")
        self.assertEqual(obj.active_dims, _res)

    def test_active_dims__three_active_dim__w_data_range(self):
        self.populate_WorkflowResults()
        _node = 1
        _res = [0, 2, 3]
        _res.sort()
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", True)
        obj.select_active_node(_node)
        for _index in range(RES.ndims[_node]):
            obj.set_param_value(f"data_slice_{_index}", "1")
        for _dim in _res:
            obj.set_param_value(f"data_slice_{_dim}", ":")
        self.assertEqual(obj.active_dims, _res)

    def test_selection_property(self):
        self.populate_WorkflowResults()
        _node = 1
        obj = WorkflowResultsSelector()
        obj.set_param_value("use_data_range", False)
        obj.select_active_node(_node)
        _slices = obj.selection
        self.assertIsInstance(_slices, tuple)
        for _item in _slices:
            self.assertIsInstance(_item, np.ndarray)


if __name__ == "__main__":
    unittest.main()
