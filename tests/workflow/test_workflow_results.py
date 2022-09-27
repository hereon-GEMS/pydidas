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
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import os
import shutil
import tempfile
from numbers import Real

import numpy as np
import h5py

from pydidas.core import Dataset, get_generic_parameter, Parameter
from pydidas.core.utils import get_random_string, create_hdf5_dataset
from pydidas.experiment import SetupScan
from pydidas.unittest_objects import DummyProc, DummyLoader
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.workflow.result_savers import WorkflowResultSaverMeta


SCAN = SetupScan()
TREE = WorkflowTree()
RES = WorkflowResults()
SAVER = WorkflowResultSaverMeta


class TestWorkflowResults(unittest.TestCase):
    def setUp(self):
        self.set_up_scan()
        self.set_up_tree()
        RES.clear_all_results()
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def set_up_scan(self):
        self._scan_n = (21, 3, 7)
        self._scan_offsets = (-3, 0, 3.2)
        self._scan_delta = (0.1, 1, 12)
        self._scan_unit = ("m", "mm", "m")
        self._scan_label = ("Test", "Dir 2", "other dim")
        SCAN.set_param_value("scan_dim", len(self._scan_n))
        for _dim in range(len(self._scan_n)):
            SCAN.set_param_value(f"n_points_{_dim + 1}", self._scan_n[_dim])
            SCAN.set_param_value(f"offset_{_dim + 1}", self._scan_offsets[_dim])
            SCAN.set_param_value(f"delta_{_dim + 1}", self._scan_delta[_dim])
            SCAN.set_param_value(f"unit_{_dim + 1}", self._scan_unit[_dim])
            SCAN.set_param_value(f"scan_label_{_dim + 1}", self._scan_label[_dim])

    def set_up_tree(self):
        self._input_shape = (127, 324)
        self._result2_shape = (12, 3, 5)
        TREE.clear()
        TREE.create_and_add_node(DummyLoader())
        TREE.nodes[0].plugin.set_param_value("image_height", self._input_shape[0])
        TREE.nodes[0].plugin.set_param_value("image_width", self._input_shape[1])
        TREE.create_and_add_node(DummyProc())
        TREE.create_and_add_node(DummyProc(), parent=TREE.root)
        TREE.prepare_execution()
        TREE.nodes[2]._result_shape = self._result2_shape

    def generate_test_datasets(self):
        _shape1 = self._input_shape
        _res1 = Dataset(
            np.random.random(_shape1),
            axis_units=["m", "mm"],
            axis_labels=["dim1", "dim 2"],
            axis_ranges=[np.arange(_shape1[0]), _shape1[1] - np.arange(_shape1[1])],
        )
        _shape2 = self._result2_shape
        _res2 = Dataset(
            np.random.random(_shape2),
            axis_units=["m", "Test", None],
            axis_labels=["dim1", "2nd dim", "dim #3"],
            axis_ranges=[12 + np.arange(_shape2[0]), None, None],
        )
        _results = {1: _res1, 2: _res2}
        return _shape1, _shape2, _results

    def create_h5_test_file(self, filename):
        _data_label = get_random_string(12)
        _label = get_random_string(9)
        _data = np.random.random((9, 9, 27))
        _data_labels = {0: "None", 1: None, 2: "Label"}
        _data_units = {0: "u1", 1: "u2", 2: None}
        _plugin_name = get_random_string(7)
        _data_ranges = {
            0: None,
            1: np.arange(9) - 3,
            2: np.linspace(12, -5, num=27),
        }
        with h5py.File(filename, "w") as _file:
            _file.create_group("entry")
            _file.create_group("entry/data")
            _file.create_group("entry/scan")
            _file["entry"].create_dataset("data_label", data=_data_label)
            _file["entry"].create_dataset("plugin_name", data=_plugin_name)
            _file["entry"].create_dataset("label", data=_label)
            _file["entry"].create_dataset("scan_title", data=get_random_string(8))
            _file["entry"].create_dataset("node_id", data=6)
            _file["entry/data"].create_dataset("data", data=_data)
            _file["entry/scan"].create_dataset("scan_dimension", data=2)
            for _dim in range(3):
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "label",
                    data=_data_labels[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "unit",
                    data=_data_units[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "range",
                    data=_data_ranges[_dim],
                )
            for _dim in range(2):
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "range",
                    data=_data_ranges[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "label",
                    data=_data_labels[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "unit",
                    data=_data_units[_dim],
                )
            _meta = {
                "data": _data,
                "data_labels": _data_label,
                "labels": _label,
                "axlabels": _data_labels,
                "axunits": _data_units,
                "axranges": _data_ranges,
                "plugin_name": _plugin_name,
            }
            return _meta

    def create_composites(self):
        RES.update_shapes_from_scan_and_workflow()
        RES._WorkflowResults__composites[1] = Dataset(
            np.zeros(self._scan_n + self._input_shape)
        )
        RES._WorkflowResults__composites[2] = Dataset(
            np.zeros(self._scan_n + self._result2_shape)
        )

    def generate_test_metadata(self):
        _shape1 = self._input_shape
        _res1 = Dataset(
            np.random.random(_shape1),
            axis_units=["m", "mm"],
            axis_labels=["dim1", "dim 2"],
            axis_ranges=[np.arange(_shape1[0]), _shape1[1] - np.arange(_shape1[1])],
        )
        _shape2 = self._result2_shape
        _res2 = Dataset(
            np.random.random(_shape2),
            axis_units=["m", "Test", None],
            axis_labels=["dim1", "2nd dim", "dim #3"],
            axis_ranges=[
                12 + np.arange(_shape2[0]),
                4 + np.arange(_shape2[1]),
                np.arange(_shape2[2]) - 42,
            ],
        )
        _meta1 = {
            "axis_units": _res1.axis_units,
            "axis_labels": _res1.axis_labels,
            "axis_ranges": _res1.axis_ranges,
        }
        _meta2 = {
            "axis_units": _res2.axis_units,
            "axis_labels": _res2.axis_labels,
            "axis_ranges": _res2.axis_ranges,
        }
        return {1: _meta1, 2: _meta2}

    def test_init(self):
        ...

    def test_prepare_files_for_saving__simple(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        RES.prepare_files_for_saving(self._tmpdir, "HDF5")
        _files = os.listdir(self._tmpdir)
        self.assertIn("node_01.h5", _files)
        self.assertIn("node_02.h5", _files)

    def test_prepare_files_for_saving__single_node(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        RES.prepare_files_for_saving(self._tmpdir, "HDF5", single_node=1)
        _files = os.listdir(self._tmpdir)
        self.assertIn("node_01.h5", _files)
        self.assertNotIn("node_02.h5", _files)

    def test_prepare_files_for_saving__w_existing_file_no_overwrite(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        with open(os.path.join(self._tmpdir, "node_01.h5"), "w") as _file:
            _file.write("test")
        with self.assertRaises(FileExistsError):
            RES.prepare_files_for_saving(self._tmpdir, "HDF5")

    def test_prepare_files_for_saving__w_existing_file_w_overwrite(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        with open(os.path.join(self._tmpdir, "test.txt"), "w") as _file:
            _file.write("test")
        RES.prepare_files_for_saving(self._tmpdir, "HDF5", overwrite=True)
        _files = os.listdir(self._tmpdir)
        self.assertIn("node_01.h5", _files)
        self.assertIn("node_02.h5", _files)

    def test_prepare_files_for_saving__w_nonexisting_dir(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        shutil.rmtree(self._tmpdir)
        RES.prepare_files_for_saving(self._tmpdir, "HDF5")
        _files = os.listdir(self._tmpdir)
        self.assertIn("node_01.h5", _files)
        self.assertIn("node_02.h5", _files)

    def test_save_results_to_disk__simple(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        RES.save_results_to_disk(self._tmpdir, "HDF5")
        with h5py.File(os.path.join(self._tmpdir, "node_01.h5"), "r") as f:
            _shape1 = f["entry/data/data"].shape
        with h5py.File(os.path.join(self._tmpdir, "node_02.h5"), "r") as f:
            _shape2 = f["entry/data/data"].shape
        self.assertEqual(_shape1, RES.shapes[1])
        self.assertEqual(_shape2, RES.shapes[2])

    def test_save_results_to_disk__single_node(self):
        RES.update_shapes_from_scan_and_workflow()
        self.create_composites()
        RES.save_results_to_disk(self._tmpdir, "HDF5", node_id=1)
        with h5py.File(os.path.join(self._tmpdir, "node_01.h5"), "r") as f:
            _shape1 = f["entry/data/data"].shape
        self.assertEqual(_shape1, RES.shapes[1])
        self.assertFalse(os.path.exists(os.path.join(self._tmpdir, "node_02.h5")))

    def test_get_result_ranges(self):
        _, _, _data = self.generate_test_datasets()
        for _key, _dset in _data.items():
            RES._WorkflowResults__composites[_key] = _dset
            _ranges = RES.get_result_ranges(_key)
            for _dim, _range in _ranges.items():
                if _range is None:
                    self.assertEqual(_range, _dset.axis_ranges[_dim])
                else:
                    self.assertTrue(np.allclose(_range, _dset.axis_ranges[_dim]))

    def test_get_results(self):
        _tmpres = np.random.random((50, 50))
        RES._WorkflowResults__composites[0] = _tmpres
        _res = RES.get_results(0)
        self.assertTrue(np.equal(_res, _tmpres).all())

    def test_get_results_for_flattened_scan(self):
        _node = 1
        RES.update_shapes_from_scan_and_workflow()
        _ndim = RES.ndims[_node] - SCAN.get_param_value("scan_dim") + 1
        _data = RES.get_results_for_flattened_scan(_node)
        self.assertEqual(_data.ndim, _ndim)
        self.assertEqual(
            _data.shape, (SCAN.n_points,) + TREE.nodes[_node]._result_shape
        )

    def test_get_result_metadata(self):
        _tmpres = np.random.random((50, 50))
        RES._WorkflowResults__composites[0] = Dataset(_tmpres)
        _res = RES.get_result_metadata(0)
        self.assertIsInstance(_res, dict)
        for _key in ["axis_labels", "axis_ranges", "axis_units", "metadata"]:
            self.assertTrue(_key in _res)

    def test_get_result_subset__no_flatten_single_point(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (0, 0, 0, 0, 0)
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice)
        self.assertIsInstance(_res, Real)

    def test_get_result_subset__no_flatten_w_array(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (slice(0, self._scan_n[0]), 0, slice(0, self._scan_n[2]), 0, 0)
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], self._scan_n[2]))

    def test_get_result_subset__no_flatten_w_array_indices(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (np.arange(self._scan_n[0]), [0], np.arange(self._scan_n[2]), 0, 0)
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], 1, self._scan_n[2]))

    def test_get_result_subset__no_flatten_w_array_indices_squeezed(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (np.arange(self._scan_n[0]), [0], np.arange(self._scan_n[2]), 0, 0)
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice, squeeze=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], self._scan_n[2]))

    def test_get_result_subset__flatten_single_point(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (0, 0, 0)
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice, flattened_scan_dim=True)
        self.assertIsInstance(_res, Real)

    def test_get_result_subset__flatten_array(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (slice(0, self._scan_n[0] - 3), 0, slice(0, self._scan_n[2]))
        _node_id = 1
        _res = RES.get_result_subset(_node_id, _slice, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0] - 3, self._scan_n[2]))

    def test_get_result_subset__flatten_array_multidim(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (
            slice(0, self._scan_n[0] - 3),
            0,
            slice(0, self._result2_shape[1] - 1),
        )
        _node_id = 2
        _res = RES.get_result_subset(_node_id, _slice, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(
            _res.shape,
            (self._scan_n[0] - 3, self._result2_shape[1] - 1, self._result2_shape[2]),
        )

    def test_get_result_subset__flatten_array_multidim_with_arrays(self):
        RES.update_shapes_from_scan_and_workflow()
        _slice = (
            np.arange(self._scan_n[0] - 3),
            0,
            np.arange(self._result2_shape[1] - 1),
        )
        _node_id = 2
        _res = RES.get_result_subset(_node_id, _slice, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(
            _res.shape,
            (self._scan_n[0] - 3, self._result2_shape[1] - 1, self._result2_shape[2]),
        )

    def test_shapes__empty(self):
        self.assertEqual(RES.shapes, {})

    def test_shapes__simple(self):
        _shapes = {0: (12, 43), 5: (6, 54), 6: (12,)}
        RES._config["shapes"] = _shapes.copy()
        _res = RES.shapes
        self.assertEqual(_shapes, _res)

    def test_ndims__empty(self):
        self.assertEqual(RES.ndims, {})

    def test_ndims__regular(self):
        RES.update_shapes_from_scan_and_workflow()
        _ndims = RES.ndims
        self.assertEqual(_ndims[1], len(self._input_shape) + len(self._scan_n))
        self.assertEqual(_ndims[2], len(self._result2_shape) + len(self._scan_n))

    def test_update_composite_metadata(self):
        _shape1, _shape2, _results = self.generate_test_datasets()
        self.create_composites()
        RES._WorkflowResults__update_composite_metadata(_results)
        for j in [1, 2]:
            for i in range(0, _results[j].ndim):
                self.assertEqual(
                    RES.get_results(j).axis_labels[i + 3], _results[j].axis_labels[i]
                )
                self.assertEqual(
                    RES.get_results(j).axis_units[i + 3], _results[j].axis_units[i]
                )
                self.assertTrue(
                    np.equal(
                        RES.get_results(j).axis_ranges[i + 3],
                        _results[j].axis_ranges[i],
                    ).all()
                )
        self.assertTrue(RES._config["metadata_complete"])

    def test_store_results(self):
        RES._config["metadata_complete"] = True
        _index = 247
        _shape1, _shape2, _results = self.generate_test_datasets()
        self.create_composites()
        RES._WorkflowResults__update_composite_metadata(_results)

        RES.store_results(_index, _results)
        _scan_indices = SCAN.get_frame_position_in_scan(_index)
        self.assertTrue(
            np.equal(
                _results[1], RES._WorkflowResults__composites[1][_scan_indices]
            ).all()
        )
        self.assertTrue(
            np.equal(
                _results[2], RES._WorkflowResults__composites[2][_scan_indices]
            ).all()
        )

    def test_store_results__no_previous_metadata(self):
        _index = 247
        _shape1, _shape2, _results = self.generate_test_datasets()
        RES._WorkflowResults__composites[1] = Dataset(np.zeros(self._scan_n + _shape1))
        RES._WorkflowResults__composites[2] = Dataset(np.zeros(self._scan_n + _shape2))
        RES._WorkflowResults__update_composite_metadata(_results)
        RES.store_results(_index, _results)
        _scan_indices = SCAN.get_frame_position_in_scan(_index)
        self.assertTrue(
            np.equal(
                _results[1], RES._WorkflowResults__composites[1][_scan_indices]
            ).all()
        )
        self.assertTrue(
            np.equal(
                _results[2], RES._WorkflowResults__composites[2][_scan_indices]
            ).all()
        )
        self.assertTrue(RES._config["metadata_complete"])

    def test_update_frame_metadata(self):
        RES.update_shapes_from_scan_and_workflow()
        _meta = self.generate_test_metadata()
        RES.update_frame_metadata(_meta)
        self.assertTrue(RES._config["metadata_complete"])
        _dim_offset = SCAN.get_param_value("scan_dim")
        for _node in _meta:
            _res = RES.get_results(_node)
            self.assertEqual(
                self._scan_label + tuple(_meta[_node]["axis_labels"].values()),
                tuple(_res.axis_labels.values()),
            )
            self.assertEqual(
                self._scan_unit + tuple(_meta[_node]["axis_units"].values()),
                tuple(_res.axis_units.values()),
            )
            for _dim, _scale in _res.axis_ranges.items():
                if _dim < SCAN.get_param_value("scan_dim"):
                    _range = SCAN.get_range_for_dim(_dim + 1)
                    self.assertTrue(np.equal(_range, _scale).all())
                else:
                    _target = _meta[_node]["axis_ranges"][_dim - _dim_offset]
                    self.assertTrue(np.equal(_target, _scale).all())

    def test_clear_all_results(self):
        RES._config["shapes"] = True
        RES._config["metadata_complete"] = True
        RES.clear_all_results()
        self.assertEqual(RES._config["shapes"], {})
        self.assertFalse(RES._config["metadata_complete"])

    def test_update_shapes_from_scan_and_workflow(self):
        RES.update_shapes_from_scan_and_workflow()
        self.assertEqual(RES.shapes[1], self._scan_n + self._input_shape)
        self.assertEqual(RES.shapes[2], self._scan_n + self._result2_shape)
        self.assertEqual(RES.get_results(1).shape, RES.shapes[1])
        self.assertEqual(RES.get_results(2).shape, RES.shapes[2])
        self.assertEqual(
            RES._config["shapes"].keys(), TREE.get_all_result_shapes().keys()
        )
        self.assertEqual(
            RES._config["node_labels"].keys(), TREE.get_all_result_shapes().keys()
        )
        self.assertEqual(
            RES._config["data_labels"].keys(), TREE.get_all_result_shapes().keys()
        )
        self.assertEqual(
            RES._config["plugin_names"].keys(), TREE.get_all_result_shapes().keys()
        )
        self.assertEqual(
            RES._config["result_titles"].keys(), TREE.get_all_result_shapes().keys()
        )

    def test_update_param_choices_from_label__curr_choice_okay(self):
        _param = get_generic_parameter("selected_results")
        RES._config["labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        RES.update_param_choices_from_labels(_param)
        _choices = _param.choices
        self.assertIn("No selection", _choices)
        for _key, _label in RES.labels.items():
            if len(_label) > 0:
                _item = f"{_label} (node #{_key:03d})"
            else:
                _item = f"(node #{_key:03d})"
            self.assertIn(_item, _choices)

    def test_update_param_choices_from_label__curr_choice_not_okay(self):
        _param = Parameter("test", str, "something", choices=["something"])
        RES._config["labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        RES.update_param_choices_from_labels(_param)
        _choices = _param.choices
        self.assertIn("No selection", _choices)
        for _key, _label in RES.labels.items():
            if len(_label) > 0:
                _item = f"{_label} (node #{_key:03d})"
            else:
                _item = f"(node #{_key:03d})"
            self.assertIn(_item, _choices)

    def test_update_param_choices_from_label__only_node_entries(self):
        _param = get_generic_parameter("selected_results")
        RES._config["node_labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        RES._config["result_titles"] = {
            1: "a (node #001)",
            2: "b (node #002)",
            3: "c (node #003)",
            5: "[Dummy] (node #005)",
        }
        RES.update_param_choices_from_labels(_param, False)
        _choices = _param.choices
        for _label in RES.result_titles.values():
            self.assertIn(_label, _choices)

    def test_update_param_choices_from_label__node_only_bad_choice(self):
        _param = Parameter("test", str, "something", choices=["something"])
        RES._config["node_labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        RES._config["result_titles"] = {
            1: "a (node #001)",
            2: "b (node #002)",
            3: "c (node #003)",
            5: "[Dummy] (node #005)",
        }
        RES.update_param_choices_from_labels(_param, False)
        _choices = _param.choices
        for _label in RES.result_titles.values():
            self.assertIn(_label, _choices)

    def test_source_hash__simple(self):
        _hash = RES.source_hash
        self.assertIsInstance(_hash, int)

    def test_source_hash__change_in_scansetup(self):
        _hash = RES.source_hash
        SCAN.set_param_value("unit_1", "a new unit value")
        _new_hash = RES.source_hash
        self.assertNotEqual(_hash, _new_hash)

    def test_source_hash__change_in_tree(self):
        _hash = RES.source_hash
        TREE.nodes[0].plugin.set_param_value("image_height", 12345)
        _new_hash = RES.source_hash
        self.assertNotEqual(_hash, _new_hash)

    def test_import_data_from_directory__empty_dir(self):
        RES.update_shapes_from_scan_and_workflow()
        RES.import_data_from_directory(self._tmpdir)
        _scan_title = get_random_string(8)
        SCAN.set_param_value("scan_title", _scan_title)
        self.assertEqual(RES.shapes, {})
        self.assertEqual(SCAN.get_param_value("scan_title"), _scan_title)

    def test_import_data_from_directory__with_files(self):
        RES.update_shapes_from_scan_and_workflow()
        _meta11 = self.create_h5_test_file(os.path.join(self._tmpdir, "node_11.h5"))
        _meta5 = self.create_h5_test_file(os.path.join(self._tmpdir, "node_05.h5"))
        RES.import_data_from_directory(self._tmpdir)
        for _id, _local in [[5, _meta5], [11, _meta11]]:
            for _key in ["labels", "data_labels"]:
                self.assertEqual(getattr(RES, _key)[_id], _local[_key])
            for _key in ["shapes", "ndims"]:
                self.assertEqual(
                    getattr(RES, _key)[_id], getattr(_local["data"], _key[:-1])
                )
            _res = RES.get_results(_id)
            self.assertTrue(np.allclose(_res, _local["data"]))
            self.assertEqual(_res.axis_labels, _local["axlabels"])
            self.assertEqual(_res.axis_units, _local["axunits"])
            for _dim in range(_res.ndim):
                if isinstance(_res.axis_ranges[_dim], np.ndarray):
                    self.assertTrue(
                        np.allclose(_res.axis_ranges[_dim], _local["axranges"][_dim])
                    )
                else:
                    self.assertEqual(_res.axis_ranges[_dim], _local["axranges"][_dim])


if __name__ == "__main__":
    unittest.main()
