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

import os
import shutil
import tempfile
import unittest
from numbers import Real
from pathlib import Path

import h5py
import numpy as np
from qtpy import QtWidgets

from pydidas import unittest_objects
from pydidas.contexts import DiffractionExperiment
from pydidas.contexts.diff_exp import DiffractionExperimentContext
from pydidas.contexts.scan import Scan, ScanContext
from pydidas.core import Dataset, Parameter, UserConfigError, get_generic_parameter
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.unittest_objects import (
    DummyLoader,
    DummyProc,
    DummyProcNewDataset,
    create_hdf5_results_file,
)
from pydidas.workflow import (
    ProcessingResults,
    ProcessingTree,
    WorkflowTree,
)
from pydidas.workflow.result_io import ProcessingResultIoMeta
from pydidas_qtcore import PydidasQApplication


SAVER = ProcessingResultIoMeta
PLUGINS = PluginCollection()
SCAN = ScanContext()
TREE = WorkflowTree()
EXP = DiffractionExperimentContext()


class TestProcessingResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _path = Path(unittest_objects.__file__).parent
        if _path not in PLUGINS.registered_paths:
            PLUGINS.find_and_register_plugins(_path)
        _app = QtWidgets.QApplication.instance()
        if _app is None:
            _ = PydidasQApplication([])
        cls._EXP = DiffractionExperimentContext()
        cls._EXP.set_param_value("xray_wavelength", 1)

    @classmethod
    def tearDownClass(cls):
        PLUGINS.unregister_plugin_path(Path(unittest_objects.__file__).parent)

    def setUp(self):
        self.set_up_scan()
        self.set_up_tree()
        self._plugin_metadata = {
            1: {
                "axis_units": {0: "m", 1: "mm"},
                "axis_labels": {0: "dim1", 1: "dim 2"},
                "axis_ranges": {
                    0: np.arange(self._input_shape[0]),
                    1: self._input_shape[1] - np.arange(self._input_shape[1]),
                },
                "data_label": "Test",
                "data_unit": "u1",
            },
            2: {
                "axis_units": {0: "m", 1: "Test", 2: "", 3: "spam!"},
                "axis_labels": {0: "dim1", 1: "2nd dim", 2: "dim #3", 3: "42"},
                "axis_ranges": {
                    0: 12 + np.arange(self._new_shape[0]),
                    1: np.arange(self._new_shape[1]),
                    2: np.array([42]),
                    3: 4 + 0.5 * np.arange(self._new_shape[3]),
                },
                "data_label": "New dataset",
                "data_unit": "u2",
            },
        }
        SAVER.set_active_savers_and_title([])
        self._tmpdir = Path(tempfile.mkdtemp())

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
            SCAN.set_param_value(f"scan_dim{_dim}_n_points", self._scan_n[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_offset", self._scan_offsets[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_delta", self._scan_delta[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_unit", self._scan_unit[_dim])
            SCAN.set_param_value(f"scan_dim{_dim}_label", self._scan_label[_dim])

    def set_up_tree(self):
        self._input_shape = (127, 324)
        self._new_shape = (12, 3, 1, 5)
        self._node_labels = {1: "Test plugin 1", 2: "Test plugin 2"}
        TREE.clear()
        TREE.create_and_add_node(DummyLoader())
        TREE.nodes[0].plugin.set_param_value("image_height", self._input_shape[0])
        TREE.nodes[0].plugin.set_param_value("image_width", self._input_shape[1])
        _proc1 = DummyProc()
        _proc1.set_param_value("label", self._node_labels[1])
        _proc2 = DummyProcNewDataset(output_shape=self._new_shape)
        _proc2.set_param_value("label", self._node_labels[2])
        TREE.create_and_add_node(_proc1)
        TREE.create_and_add_node(_proc2, parent=TREE.root)
        TREE.prepare_execution()

    def generate_test_datasets(self) -> tuple[tuple, tuple, dict]:
        _res1 = Dataset(np.random.random(self._input_shape), **self._plugin_metadata[1])
        _res2 = Dataset(np.random.random(self._new_shape), **self._plugin_metadata[2])
        _results = {1: _res1, 2: _res2}
        return self._input_shape, self._new_shape, _results

    def get_test_metadata_with_scan(self) -> dict:
        _scan_meta = [SCAN.get_metadata_for_dim(i) for i in range(SCAN.ndim)]
        _scan_ax_meta = {
            "axis_labels": {i: _item[0] for i, _item in enumerate(_scan_meta)},
            "axis_units": {i: _item[1] for i, _item in enumerate(_scan_meta)},
            "axis_ranges": {i: _item[2] for i, _item in enumerate(_scan_meta)},
        }
        _new_metadata = {}
        for _node_id, _meta in self._plugin_metadata.items():
            _node_metadata = _new_metadata[_node_id] = {}
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _node_metadata[_key] = {
                    _i: _k
                    for _i, _k in enumerate(
                        list(_scan_ax_meta[_key].values()) + list(_meta[_key].values())
                    )
                }
            _node_metadata["data_unit"] = _meta["data_unit"]
            _node_metadata["data_label"] = _meta["data_label"]
        return _new_metadata

    def get_node_output_filename(self, node_id: int, extension: str = "h5") -> str:
        _label = self._node_labels[node_id].replace(" ", "_")
        return f"node_{node_id:02d}_{_label}.{extension}"

    def get_node_output_path(self, node_id: int, extension: str = "h5") -> Path:
        return self._tmpdir.joinpath(self.get_node_output_filename(node_id, extension))

    def create_standard_workflow_results(self) -> ProcessingResults:
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        res._create_composites()
        return res

    def create_h5_test_file(
        self, node_id: int, workflow_results_instance: ProcessingResults
    ):
        create_hdf5_results_file(
            self.get_node_output_path(node_id),
            workflow_results_instance._composites[node_id],
            workflow_results_instance._SCAN,
            workflow_results_instance._EXP,
            workflow_results_instance._TREE,
            node_label=workflow_results_instance._config["node_labels"][node_id],
            plugin_name=workflow_results_instance._config["plugin_names"][node_id],
            node_id=node_id,
        )

    def test_init__plain(self):
        res = ProcessingResults()
        self.assertIsInstance(res, ProcessingResults)
        self.assertIsInstance(res._SCAN, Scan)
        self.assertIsInstance(res._EXP, DiffractionExperiment)
        self.assertIsInstance(res._TREE, ProcessingTree)

    def test_init__with_contexts(self):
        _local_scan = Scan()
        _local_exp = DiffractionExperiment()
        _local_tree = ProcessingTree()
        res = ProcessingResults(
            scan_context=_local_scan,
            diffraction_exp_context=_local_exp,
            workflow_tree=_local_tree,
        )
        self.assertNotEqual(id(SCAN), id(res._SCAN))
        self.assertNotEqual(id(EXP), id(res._EXP))
        self.assertNotEqual(id(TREE), id(res._TREE))

    def test_clear_all_results(self):
        res = ProcessingResults()
        res._config["shapes"] = {1: (1, 2, 3), 2: (4, 5, 6)}
        res._config["plugin_names"] = {1: "a", 2: "b"}
        res._config["node_labels"] = {1: "c", 2: "d"}
        res._config["result_tiles"] = {1: "e", 2: "f"}
        res._config["plugin_res_metadata"] = self._plugin_metadata.copy()
        res._config["metadata_complete"] = True
        res._config["exported"] = True
        res._config["shapes_set"] = True
        res.clear_all_results()
        for _key in [
            "shapes",
            "plugin_names",
            "node_labels",
            "result_titles",
            "plugin_res_metadata",
        ]:
            self.assertEqual(res._config[_key], {})
        for _key in ["metadata_complete", "composites_created", "shapes_set"]:
            self.assertFalse(res._config[_key])

    def test_prepare_new_results(self):
        res = ProcessingResults()
        res._TREE.prepare_execution()
        res.prepare_new_results()
        for _key in ["plugin_names", "node_labels", "result_titles"]:
            self.assertNotEqual(res._config[_key][1], "")
            self.assertNotEqual(res._config[_key][2], "")
        self.assertEqual(res._config["shapes"], {})
        self.assertEqual(res._config["plugin_res_metadata"][1], {})
        self.assertEqual(res._config["plugin_res_metadata"][2], {})
        self.assertEqual(hash(res._config["frozen_SCAN"]), hash(res._SCAN))
        self.assertNotEqual(id(res._config["frozen_SCAN"]), id(res._SCAN))
        self.assertEqual(hash(res._config["frozen_EXP"]), hash(res._EXP))
        self.assertNotEqual(id(res._config["frozen_EXP"]), id(res._EXP))
        for _id, _node in res._TREE.nodes.items():
            self.assertEqual(hash(res._config["frozen_TREE"].nodes[_id]), hash(_node))
        self.assertNotEqual(id(res._config["frozen_TREE"]), id(res._TREE))

    def test_store_frame_shapes(self):
        res = ProcessingResults()
        res.prepare_new_results()
        _shapes = {1: self._input_shape, 2: self._new_shape}
        res.store_frame_shapes(_shapes)
        _full_shapes = {
            1: SCAN.shape + self._input_shape,
            2: SCAN.shape + self._new_shape,
        }
        self.assertEqual(res._config["shapes"], _full_shapes)
        self.assertTrue(res._config["shapes_set"])

    def test_store_frame_shapes__wrong_nodes(self):
        res = ProcessingResults()
        res.prepare_new_results()
        _shapes = {1: self._input_shape, 3: self._new_shape}
        with self.assertRaises(UserConfigError):
            res.store_frame_shapes(_shapes)

    def test_store_frame_metadata(self):
        res = ProcessingResults()
        res.prepare_new_results()
        _meta = self._plugin_metadata.copy()
        _full_meta = self.get_test_metadata_with_scan()
        res.store_frame_metadata(_meta)
        self.assertTrue(res._config["metadata_complete"])
        for _node, _node_metadata in _full_meta.items():
            _stored_meta = res._config["plugin_res_metadata"][_node]
            for _key, _val in _node_metadata.items():
                _ref = _stored_meta[_key]
                if _key == "axis_ranges":
                    for _dim, _range in _val.items():
                        self.assertTrue(np.allclose(_range, _ref[_dim]))
                else:
                    self.assertEqual(_val, _ref)
        self.assertEqual(res._config["shapes"][1], SCAN.shape + self._input_shape)
        self.assertEqual(res._config["shapes"][2], SCAN.shape + self._new_shape)
        self.assertTrue(res._config["shapes_set"])

    def test_store_results__w_frame_metadata(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_shapes({1: self._input_shape, 2: self._new_shape})
        res.store_frame_metadata(self._plugin_metadata)
        _index = 247
        _shape1, _shape2, _results = self.generate_test_datasets()
        res.store_results(_index, _results)
        _scan_indices = SCAN.get_frame_position_in_scan(_index)
        self.assertTrue(np.allclose(_results[1], res._composites[1][_scan_indices]))
        self.assertTrue(np.allclose(_results[2], res._composites[2][_scan_indices]))

    def test_store_results__no_previous_metadata(self):
        res = ProcessingResults()
        res.prepare_new_results()
        _index = 247
        _shape1, _shape2, _results = self.generate_test_datasets()
        res.store_results(_index, _results)
        _scan_indices = SCAN.get_frame_position_in_scan(_index)
        self.assertTrue(np.allclose(_results[1], res._composites[1][_scan_indices]))
        self.assertTrue(np.allclose(_results[2], res._composites[2][_scan_indices]))
        self.assertTrue(res._config["metadata_complete"])

    def test_store_results__w_composites(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_shapes({1: self._input_shape, 2: self._new_shape})
        res._create_composites()
        _index = 247
        _shape1, _shape2, _results = self.generate_test_datasets()
        res.store_results(_index, _results)
        _scan_indices = SCAN.get_frame_position_in_scan(_index)
        self.assertTrue(np.allclose(_results[1], res._composites[1][_scan_indices]))
        self.assertTrue(np.allclose(_results[2], res._composites[2][_scan_indices]))

    def test_create_composites(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_shapes({1: self._input_shape, 2: self._new_shape})
        res._create_composites()
        self.assertEqual(res._composites[1].shape, SCAN.shape + self._input_shape)
        self.assertEqual(res._composites[2].shape, SCAN.shape + self._new_shape)

    def test_create_composites__shapes_unset(self):
        res = ProcessingResults()
        res.prepare_new_results()
        with self.assertRaises(UserConfigError):
            res._create_composites()

    def test_shapes(self):
        res = ProcessingResults()
        res.prepare_new_results()
        _shapes = {1: self._input_shape, 2: self._new_shape}
        res.store_frame_shapes(_shapes)
        self.assertEqual(
            res.shapes,
            {
                1: SCAN.shape + self._input_shape,
                2: SCAN.shape + self._new_shape,
            },
        )

    def test_shapes__empty(self):
        res = ProcessingResults()
        self.assertEqual(res.shapes, {})

    def test_node_labels(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        self.assertEqual(
            res.node_labels,
            {
                1: TREE.nodes[1].plugin.get_param_value("label"),
                2: TREE.nodes[2].plugin.get_param_value("label"),
            },
        )

    def test_node_labels__empty(self):
        res = ProcessingResults()
        self.assertEqual(res.node_labels, {})

    def test_data_labels__empty_composites(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        self.assertEqual(res.data_labels, {})

    def test_data_labels__w_composites(self):
        res = self.create_standard_workflow_results()
        self.assertEqual(
            res.data_labels,
            {
                1: self._plugin_metadata[1]["data_label"],
                2: self._plugin_metadata[2]["data_label"],
            },
        )

    def test_data_units__empty_composites(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        self.assertEqual(res.data_units, {})

    def test_data_units__w_composites(self):
        res = self.create_standard_workflow_results()
        self.assertEqual(
            res.data_units,
            {
                1: self._plugin_metadata[1]["data_unit"],
                2: self._plugin_metadata[2]["data_unit"],
            },
        )

    def test_ndims__empty_composites(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        self.assertEqual(res.ndims, {})

    def test_ndims__w_composites(self):
        res = self.create_standard_workflow_results()
        self.assertEqual(
            res.ndims,
            {
                1: SCAN.ndim + len(self._input_shape),
                2: SCAN.ndim + len(self._new_shape),
            },
        )

    def test_frozen_tree(self):
        res = ProcessingResults()
        res.prepare_new_results()
        self.assertEqual(res.frozen_tree.export_to_string(), TREE.export_to_string())

    def test_frozen_exp(self):
        res = ProcessingResults()
        res.prepare_new_results()
        self.assertEqual(res.frozen_exp.param_values, EXP.param_values)

    def test_frozen_scan(self):
        res = ProcessingResults()
        res.prepare_new_results()
        self.assertEqual(res.frozen_scan.param_values, SCAN.param_values)

    def test_source_hash(self):
        res = ProcessingResults()
        res.prepare_new_results()
        self.assertEqual(hash(TREE), hash(res._TREE))
        self.assertEqual(res.source_hash, hash((hash(SCAN), hash(TREE), hash(EXP))))

    def test_source_hash__custom_contexts(self):
        _local_scan = Scan()
        _local_exp = DiffractionExperiment()
        _local_tree = ProcessingTree()
        res = ProcessingResults(
            scan_context=_local_scan,
            diffraction_exp_context=_local_exp,
            workflow_tree=_local_tree,
        )
        self.assertEqual(
            res.source_hash,
            hash((hash(_local_scan), hash(_local_tree), hash(_local_exp))),
        )

    def test_result_titles(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        self.assertEqual(
            res.result_titles,
            {
                1: TREE.nodes[1].plugin.result_title,
                2: TREE.nodes[2].plugin.result_title,
            },
        )

    def test_get_result_ranges(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        res._create_composites()
        _ranges = res.get_result_ranges(1)
        _ref = dict(
            enumerate(
                [SCAN.get_range_for_dim(i) for i in range(SCAN.ndim)]
                + list(self._plugin_metadata[1]["axis_ranges"].values())
            )
        )
        for _dim, _range in _ranges.items():
            self.assertTrue(np.allclose(_range, _ref[_dim]))

    def test_get_result_ranges__no_such_node(self):
        res = ProcessingResults()
        res.prepare_new_results()
        res.store_frame_metadata(self._plugin_metadata)
        with self.assertRaises(UserConfigError):
            _ranges = res.get_result_ranges(42)

    def test_get_results(self):
        res = self.create_standard_workflow_results()
        _res = res.get_results(1)
        self.assertEqual(_res.shape, SCAN.shape + self._input_shape)

    def test_get_results__wrong_node_id(self):
        res = ProcessingResults()
        with self.assertRaises(UserConfigError):
            res.get_results(3)

    def test_get_results_for_flattened_scan(self):
        res = self.create_standard_workflow_results()
        _res = res.get_results_for_flattened_scan(1)
        self.assertEqual(_res.shape, (np.prod(SCAN.shape),) + self._input_shape)

    def test_get_results_for_flattened_scan__wrong_node_id(self):
        res = self.create_standard_workflow_results()
        with self.assertRaises(UserConfigError):
            _res = res.get_results_for_flattened_scan(42)

    def test_get_results_for_flattened_scan__w_squeeze(self):
        res = self.create_standard_workflow_results()
        _res = res.get_results_for_flattened_scan(1, squeeze=True)
        _res2 = res.get_results_for_flattened_scan(2, squeeze=True)
        self.assertEqual(
            _res.shape,
            tuple(_i for _i in (np.prod(SCAN.shape),) + self._input_shape if _i > 1),
        )
        self.assertEqual(
            _res2.shape,
            tuple(_i for _i in (np.prod(SCAN.shape),) + self._new_shape if _i > 1),
        )

    def test_get_result_subset__wrong_node_id(self):
        res = self.create_standard_workflow_results()
        _slice = (0, 0, 0, 0, 0)
        with self.assertRaises(UserConfigError):
            _res = res.get_result_subset(42, *_slice)

    def test_get_result_subset__no_flatten_single_point(self):
        res = self.create_standard_workflow_results()
        _slice = (0, 0, 0, 0, 0)
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slice)
        self.assertIsInstance(_res, Real)

    def test_get_result_subset__no_flatten_w_array(self):
        res = self.create_standard_workflow_results()
        _slice = (slice(0, self._scan_n[0]), 0, slice(0, self._scan_n[2]), 0, 0)
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slice)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], self._scan_n[2]))

    def test_get_result_subset__no_flatten_w_array_indices(self):
        res = self.create_standard_workflow_results()
        _slice = (np.arange(self._scan_n[0]), [0], np.arange(1, self._scan_n[2] - 1))
        _res = res.get_result_subset(1, *_slice)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(
            _res.shape, (self._scan_n[0], 1, self._scan_n[2] - 2) + self._input_shape
        )

    def test_get_result_subset__no_flatten_w_array_indices_squeezed(self):
        res = self.create_standard_workflow_results()
        _slices = (np.arange(self._scan_n[0]), [0], np.arange(self._scan_n[2]), 0, 0)
        _ref_shape = res._composites
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slices, squeeze=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], self._scan_n[2]))

    def test_get_result_subset__ndarray_and_slice(self):
        res = self.create_standard_workflow_results()
        _slices = (
            np.arange(self._scan_n[0]),
            0,
            np.arange(self._scan_n[2] - 2),
            (0, 2, 3),
            0,
        )
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slices)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0], self._scan_n[2] - 2, 3))

    def test_get_result_subset__flatten_single_point(self):
        res = self.create_standard_workflow_results()
        _slices = (0, 0, 0)
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slices, flattened_scan_dim=True)
        self.assertIsInstance(_res, Real)

    def test_get_result_subset__flatten_array(self):
        res = self.create_standard_workflow_results()
        _slice = (slice(0, self._scan_n[0] - 3), 0, slice(0, self._scan_n[2]))
        _node_id = 1
        _res = res.get_result_subset(_node_id, *_slice, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0] - 3, self._scan_n[2]))

    def test_get_result_subset__flatten_array_multidim(self):
        res = self.create_standard_workflow_results()
        _slices = (
            slice(0, self._scan_n[0] - 3),
            slice(0, self._new_shape[0] - 1),
            1,
            0,
            slice(1, self._new_shape[3] - 1),
        )
        _node_id = 2
        _res = res.get_result_subset(_node_id, *_slices, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(
            _res.shape,
            (self._scan_n[0] - 3, self._new_shape[0] - 1, self._new_shape[3] - 2),
        )

    def test_get_result_subset__flatten_array_multidim_with_arrays(self):
        res = self.create_standard_workflow_results()
        _slices = (
            np.arange(self._scan_n[0] - 3),
            0,
            0,
            0,
            np.arange(self._new_shape[3] - 1),
        )
        _node_id = 2
        _res = res.get_result_subset(_node_id, *_slices, flattened_scan_dim=True)
        self.assertIsInstance(_res, np.ndarray)
        self.assertEqual(_res.shape, (self._scan_n[0] - 3, self._new_shape[3] - 1))

    def test_get_result_metadata__wrong_id(self):
        res = self.create_standard_workflow_results()
        with self.assertRaises(UserConfigError):
            res.get_result_metadata(3)

    def test_get_result_metadata(self):
        res = self.create_standard_workflow_results()
        _tmp_array = np.random.random((50, 50))
        res._composites[0] = Dataset(
            _tmp_array,
            axis_labels=[chr(_i + 97) for _i in range(_tmp_array.ndim)],
            axis_units=["unit_" + chr(_i + 97) for _i in range(_tmp_array.ndim)],
            metadata={"spam": "eggs"},
            axis_ranges={0: 2 + 0.4 * np.arange(50), 1: -3 * np.arange(50)},
        )
        _metadata = res.get_result_metadata(0)
        self.assertIsInstance(_metadata, dict)
        for _key in ["axis_labels", "axis_units", "metadata"]:
            self.assertEqual(_metadata[_key], getattr(res._composites[0], _key))
        for _dim in range(2):
            self.assertTrue(
                np.allclose(
                    _metadata["axis_ranges"][_dim], res._composites[0].axis_ranges[_dim]
                )
            )

    def test_get_result_metadata__use_scan_timeline(self):
        res = self.create_standard_workflow_results()
        _curr_meta_info = {"spam": "eggs"}
        _tmp_array = np.random.random(SCAN.shape + (50, 50))
        res._composites[0] = Dataset(
            _tmp_array,
            axis_labels=[chr(_i + 97) for _i in range(_tmp_array.ndim)],
            axis_units=["unit_" + chr(_i + 97) for _i in range(_tmp_array.ndim)],
            metadata=_curr_meta_info,
        )
        _metadata = res.get_result_metadata(0, use_scan_timeline=True)
        self.assertIsInstance(_metadata, dict)
        self.assertEqual(_metadata["metadata"], _curr_meta_info)
        for _key in ["axis_labels", "axis_units"]:
            _entries = list(_metadata[_key].values())[1:]
            _ref = list(getattr(res._composites[0], _key).values())[SCAN.ndim :]
            self.assertEqual(_entries, _ref)

    def test_prepare_files_for_saving__setup_incomplete(self):
        res = self.create_standard_workflow_results()
        for _key in ["shapes_set", "metadata_complete"]:
            res._config["shapes_set"] = _key != "shapes_set"
            res._config["metadata_complete"] = _key != "metadata_complete"
            with self.assertRaises(UserConfigError):
                res.prepare_files_for_saving(self._tmpdir, "HDF5")

    def test_prepare_files_for_saving__simple(self):
        res = self.create_standard_workflow_results()
        res.prepare_files_for_saving(self._tmpdir, "HDF5")
        _files = os.listdir(self._tmpdir)
        for _id in res._composites:
            self.assertIn(self.get_node_output_filename(_id), _files)

    def test_prepare_files_for_saving__single_node(self):
        res = self.create_standard_workflow_results()
        res.prepare_files_for_saving(self._tmpdir, "HDF5", single_node=1)
        _files = os.listdir(self._tmpdir)
        self.assertIn(self.get_node_output_filename(1), _files)
        self.assertNotIn(self.get_node_output_filename(2), _files)

    def test_prepare_files_for_saving__w_existing_file_no_overwrite(self):
        res = self.create_standard_workflow_results()
        res.prepare_files_for_saving(self._tmpdir, "HDF5", single_node=1)
        with open(
            self._tmpdir.joinpath(self.get_node_output_filename(1)), "w"
        ) as _file:
            _file.write("test")
        with self.assertRaises(UserConfigError):
            res.prepare_files_for_saving(self._tmpdir, "HDF5")

    def test_prepare_files_for_saving__w_existing_file_w_overwrite(self):
        res = self.create_standard_workflow_results()
        with open(
            self._tmpdir.joinpath(self.get_node_output_filename(1)), "w"
        ) as _file:
            _file.write("test")
        res.prepare_files_for_saving(self._tmpdir, "HDF5", overwrite=True)
        _files = os.listdir(self._tmpdir)
        for _id in res._composites:
            self.assertIn(self.get_node_output_filename(_id), _files)

    def test_prepare_files_for_saving__w_non_existing_dir(self):
        res = self.create_standard_workflow_results()
        shutil.rmtree(self._tmpdir)
        res.prepare_files_for_saving(self._tmpdir, "HDF5")
        _files = os.listdir(self._tmpdir)
        for _id in res._composites:
            self.assertIn(self.get_node_output_filename(_id), _files)

    def test_save_results_to_disk__simple(self):
        res = self.create_standard_workflow_results()
        res.save_results_to_disk(self._tmpdir, "HDF5")
        with h5py.File(self.get_node_output_path(1), "r") as f:
            _shape1 = f["entry/data/data"].shape
        with h5py.File(self.get_node_output_path(2), "r") as f:
            _shape2 = f["entry/data/data"].shape
        self.assertEqual(_shape1, res.shapes[1])
        self.assertEqual(_shape2, res.shapes[2])

    def test_save_results_to_disk__single_node(self):
        res = self.create_standard_workflow_results()
        res.save_results_to_disk(self._tmpdir, "HDF5", node_id=1)
        with h5py.File(self.get_node_output_path(1), "r") as f:
            _shape1 = f["entry/data/data"].shape
        self.assertEqual(_shape1, res.shapes[1])
        self.assertFalse(self.get_node_output_path(2).is_file())

    def test_update_param_choices_from_label__curr_choice_okay(self):
        _param = get_generic_parameter("selected_results")
        res = ProcessingResults()
        res._config["labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        res.update_param_choices_from_labels(_param)
        _choices = _param.choices
        self.assertIn("No selection", _choices)
        for _key, _label in res.node_labels.items():
            if len(_label) > 0:
                _item = f"{_label} (node #{_key:03d})"
            else:
                _item = f"(node #{_key:03d})"
            self.assertIn(_item, _choices)

    def test_update_param_choices_from_label__curr_choice_not_okay(self):
        _param = Parameter("test", str, "something", choices=["something"])
        res = ProcessingResults()
        res._config["labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        res.update_param_choices_from_labels(_param)
        _choices = _param.choices
        self.assertIn("No selection", _choices)
        for _key, _label in res.node_labels.items():
            if len(_label) > 0:
                _item = f"{_label} (node #{_key:03d})"
            else:
                _item = f"(node #{_key:03d})"
            self.assertIn(_item, _choices)

    def test_update_param_choices_from_label__only_node_entries(self):
        _param = get_generic_parameter("selected_results")
        res = ProcessingResults()
        res._config["node_labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        res._config["result_titles"] = {
            1: "a (node #001)",
            2: "b (node #002)",
            3: "c (node #003)",
            5: "[Dummy] (node #005)",
        }
        res.update_param_choices_from_labels(_param, False)
        _choices = _param.choices
        for _label in res.result_titles.values():
            self.assertIn(_label, _choices)

    def test_update_param_choices_from_label__node_only_bad_choice(self):
        res = ProcessingResults()
        _param = Parameter("test", str, "something", choices=["something"])
        res._config["node_labels"] = {1: "a", 2: "b", 3: "c", 5: ""}
        res._config["result_titles"] = {
            1: "a (node #001)",
            2: "b (node #002)",
            3: "c (node #003)",
            5: "[Dummy] (node #005)",
        }
        res.update_param_choices_from_labels(_param, False)
        _choices = _param.choices
        for _label in res.result_titles.values():
            self.assertIn(_label, _choices)

    def test_get_node_result_metadata_string(self):
        res = self.create_standard_workflow_results()
        _node_info = res.get_node_result_metadata_string(2, use_scan_timeline=False)
        _ndim_scan = len([_dim for _dim in range(SCAN.ndim) if SCAN.shape[_dim] > 1])
        _ndim_data = len(
            [_dim for _dim in range(len(self._new_shape)) if self._new_shape[_dim] > 1]
        )
        for _dim in range(_ndim_scan):
            self.assertIn(f"Axis #{_dim:02d} (scan):", _node_info)
        for _dim in range(_ndim_scan, _ndim_scan + _ndim_data):
            self.assertIn(f"Axis #{_dim:02d} (data):", _node_info)
        self.assertNotIn(f"Axis #{(_ndim_scan + _ndim_data):02d} (data):", _node_info)

    def test_get_node_result_metadata_string__w_scan_timeline(self):
        res = self.create_standard_workflow_results()
        _node_info = res.get_node_result_metadata_string(1, use_scan_timeline=True)
        self.assertIn("Axis #00 (scan):", _node_info)
        for _dim in range(1, 1 + len(self._input_shape)):
            self.assertIn(f"Axis #{_dim:02d} (data):", _node_info)

    def test_get_node_result_metadata_string__no_squeeze(self):
        res = self.create_standard_workflow_results()
        _node_info = res.get_node_result_metadata_string(
            2, use_scan_timeline=False, squeeze_results=False
        )
        for _dim in range(SCAN.ndim):
            self.assertIn(f"Axis #{_dim:02d} (scan):", _node_info)
        for _dim in range(SCAN.ndim, SCAN.ndim + len(self._new_shape)):
            self.assertIn(f"Axis #{_dim:02d} (data):", _node_info)
        self.assertNotIn(
            f"Axis #{(SCAN.ndim + len(self._new_shape)):02d} (data):", _node_info
        )

    def test_import_data_from_directory__empty_dir(self):
        _scan_title = get_random_string(8)
        SCAN.set_param_value("scan_title", _scan_title)
        res = ProcessingResults()
        res.import_data_from_directory(self._tmpdir)
        self.assertEqual(res.shapes, {})
        self.assertEqual(res._SCAN.get_param_value("scan_title"), _scan_title)

    def test_import_data_from_directory__with_files(self):
        res = self.create_standard_workflow_results()
        res._composites[1][:] = np.random.random(res._composites[1].shape)
        res._composites[2][:] = np.random.random(res._composites[2].shape)
        self.create_h5_test_file(1, res)
        self.create_h5_test_file(2, res)
        res.import_data_from_directory(self._tmpdir)
        self.assertEqual(
            res._config["shapes"],
            {1: SCAN.shape + self._input_shape, 2: SCAN.shape + self._new_shape},
        )
        self.assertEqual(
            res._config["node_labels"],
            {1: self._node_labels[1], 2: self._node_labels[2]},
        )
        self.assertEqual(
            res._config["plugin_names"],
            {1: TREE.nodes[1].plugin.plugin_name, 2: TREE.nodes[2].plugin.plugin_name},
        )
        self.assertEqual(
            res._config["result_titles"],
            {
                1: TREE.nodes[1].plugin.result_title,
                2: TREE.nodes[2].plugin.result_title,
            },
        )
        for _id in res._composites:
            for _dim in range(SCAN.ndim, res._composites[_id].ndim):
                _ref = self._plugin_metadata[_id]["axis_ranges"][_dim - SCAN.ndim]
                self.assertTrue(
                    np.allclose(res._composites[_id].axis_ranges[_dim], _ref)
                )
            self.assertIn(_id, res._config["plugin_res_metadata"])
            _stored_metadata = res._config["plugin_res_metadata"][_id]
            self.assertIsInstance(_stored_metadata, dict)
            self.assertEqual(
                set(_stored_metadata.keys()),
                {"axis_labels", "axis_units", "axis_ranges", "data_unit", "data_label"},
            )


if __name__ == "__main__":
    unittest.main()
