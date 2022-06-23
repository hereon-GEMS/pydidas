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
import tempfile
import os
import shutil
import random

import h5py
import numpy as np

from pydidas.core import Dataset
from pydidas.experiment import SetupScan
from pydidas.core.utils import (
    get_random_string,
    create_hdf5_dataset,
    read_and_decode_hdf5_dataset,
)
from pydidas.workflow.result_savers import WorkflowResultSaverMeta
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.workflow.result_savers.workflow_result_saver_hdf5 import (
    WorkflowResultSaverHdf5,
)


TREE = WorkflowTree()
SCAN = SetupScan()
RESULTS = WorkflowResults()
META = WorkflowResultSaverMeta
H5SAVER = WorkflowResultSaverHdf5


class TestWorkflowResultSaverHdf5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp()
        cls._create_h5_test_file()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._dir)

    @classmethod
    def _create_h5_test_file(cls):
        cls._import_test_filename = os.path.join(cls._dir, "import_test.h5")
        cls._import_data_label = get_random_string(12)
        cls._import_label = get_random_string(9)
        cls._import_data = np.random.random((9, 9, 27))
        cls._import_data_ax_labels = {0: "None", 1: None, 2: "Label"}
        cls._import_data_units = {0: "u1", 1: "u2", 2: None}
        cls._import_plugin_name = get_random_string(8)
        cls._import_title = get_random_string(10)
        cls._import_data_ranges = {
            0: np.arange(9),
            1: np.arange(9) - 3,
            2: np.linspace(12, -5, num=27),
        }
        with h5py.File(cls._import_test_filename, "w") as _file:
            _file.create_group("entry")
            _file.create_group("entry/data")
            _file.create_group("entry/scan")
            _file["entry"].create_dataset("data_label", data=cls._import_data_label)
            _file["entry"].create_dataset("label", data=cls._import_label)
            _file["entry"].create_dataset("plugin_name", data=cls._import_plugin_name)
            _file["entry/data"].create_dataset("data", data=cls._import_data)
            _file["entry"].create_dataset("title", data=cls._import_title)
            _file["entry/scan"].create_dataset("scan_dimension", data=SCAN.ndim)
            for _dim in range(3):
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "label",
                    data=cls._import_data_ax_labels[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "unit",
                    data=cls._import_data_units[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/data/axis_{_dim}",
                    "range",
                    data=cls._import_data_ranges[_dim],
                )
            for _dim in range(2):
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "range",
                    data=cls._import_data_ranges[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "label",
                    data=cls._import_data_ax_labels[_dim],
                )
                create_hdf5_dataset(
                    _file,
                    f"entry/scan/dim_{_dim}",
                    "unit",
                    data=cls._import_data_units[_dim],
                )

    def setUp(self):
        SCAN.set_param_value("scan_dim", 3)
        for d in range(1, 4):
            SCAN.set_param_value(f"n_points_{d}", random.choice([3, 5, 7, 8]))
            SCAN.set_param_value(f"delta_{d}", random.choice([0.1, 0.5, 1, 1.5]))
            SCAN.set_param_value(f"offset_{d}", random.choice([-0.1, 0.5, 1]))
            SCAN.set_param_value(f"scan_label_{d}", get_random_string(12))

    def tearDown(self):
        ...

    def prepare_with_defaults(self):
        _scan_shape = tuple(SCAN.get_param_value(f"n_points_{i}") for i in [1, 2, 3])
        self._shapes = {
            1: _scan_shape + (12, 7),
            2: _scan_shape + (23,),
            3: _scan_shape + (1, 3, 7),
        }
        self._labels = {1: "Test", 2: "not again", 3: "another"}
        self._datalabels = {1: "Intensity", 2: "Peak height", 3: "Area"}
        self._plugin_names = {1: "A plugin", 2: "Plugin no 2.", 3: "Ye olde plugin"}
        self._filenames = {
            1: "node_01_Test.h5",
            2: "node_02_not_again.h5",
            3: "node_03_another.h5",
        }
        _node_infos = {
            _node: {
                "node_label": self._labels[_node],
                "data_label": self._datalabels[_node],
                "shape": self._shapes[_node],
                "plugin_name": self._plugin_names[_node],
            }
            for _node in self._shapes.keys()
        }
        self._resdir = os.path.join(self._dir, get_random_string(8))
        H5SAVER.prepare_files_and_directories(self._resdir, _node_infos)

    def get_datasets(self, start_dim=3):
        return {
            _key: Dataset(np.random.random(_shape[start_dim:]))
            for _key, _shape in self._shapes.items()
        }

    def populate_metadata(self, dataset):
        _labels = {_key: get_random_string(8) for _key in dataset.axis_labels}
        _units = {_key: get_random_string(3) for _key in dataset.axis_units}
        _ranges = {
            _key: random.random() * np.arange(_len) + random.random()
            for _key, _len in enumerate(dataset.shape)
        }
        for _axis in _labels:
            dataset.update_axis_labels(_axis, _labels[_axis])
            dataset.update_axis_units(_axis, _units[_axis])
            dataset.update_axis_ranges(_axis, _ranges[_axis])
        return dataset, _labels, _units, _ranges

    def assert_written_files_are_okay(self, data, metadata):
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                for _ax in range(3, data[_node_id].ndim):
                    _axentry = _file[f"entry/data/axis_{_ax}"]
                    self.assertEqual(
                        read_and_decode_hdf5_dataset(_axentry["label"]),
                        metadata[_node_id]["axis_labels"][_ax - 3],
                    )
                    self.assertEqual(
                        read_and_decode_hdf5_dataset(_axentry["unit"]),
                        metadata[_node_id]["axis_units"][_ax - 3],
                    )
                    self.assertEqual(
                        read_and_decode_hdf5_dataset(_axentry["range"]),
                        metadata[_node_id]["axis_ranges"][_ax - 3],
                    )

    def test_class(self):
        self.assertEqual(H5SAVER.__class__, META)

    def test_prepare_files_and_directories(self):
        self.prepare_with_defaults()
        self.assertTrue(os.path.exists(self._resdir))
        self.assertEqual(H5SAVER.get_attribute_dict("shape"), self._shapes)
        self.assertEqual(H5SAVER.get_attribute_dict("node_label"), self._labels)
        for _key in self._shapes:
            _fname = H5SAVER._filenames[_key]
            self.assertEqual(_fname, self._filenames[_key])
            self.assertTrue(os.path.exists(os.path.join(self._resdir, _fname)))

    def test_create_file_and_populate_metadata(self):
        _node_id = 1
        self.prepare_with_defaults()
        H5SAVER._create_file_and_populate_metadata(_node_id)
        with (h5py.File(os.path.join(self._resdir, self._filenames[1]), "r") as _file):
            _data = _file["entry/data/data"]
            self.assertEqual(_data.shape, self._shapes[1])
            self.assertIsInstance(_data, h5py.Dataset)

    def test_update_node_metadata__with_None(self):
        self.prepare_with_defaults()
        _data = {
            _key: Dataset(np.random.random(_shape[3:]))
            for _key, _shape in self._shapes.items()
        }
        _data1 = _data[1]
        H5SAVER.update_node_metadata(1, _data1)

    def test_update_node_metadata__with_entries(self):
        self.prepare_with_defaults()
        _data = {
            _key: Dataset(np.random.random(_shape[3:]))
            for _key, _shape in self._shapes.items()
        }
        _data[1], _labels, _units, _ranges = self.populate_metadata(_data[1])
        H5SAVER.update_node_metadata(1, _data[1])
        _fname = os.path.join(self._resdir, self._filenames[1])
        with h5py.File(_fname, "r") as _file:
            for _ax in [3, 4]:
                _axentry = _file[f"entry/data/axis_{_ax}"]
                self.assertEqual(
                    read_and_decode_hdf5_dataset(_axentry["label"]), _labels[_ax - 3]
                )
                self.assertEqual(
                    read_and_decode_hdf5_dataset(_axentry["unit"]), _units[_ax - 3]
                )
                self.assertTrue(
                    np.allclose(
                        read_and_decode_hdf5_dataset(_axentry["range"]),
                        _ranges[_ax - 3],
                    )
                )

    def test_update_frame_metadata__standard(self):
        self.prepare_with_defaults()
        _data = {
            _key: Dataset(np.random.random(_shape[3:]))
            for _key, _shape in self._shapes.items()
        }
        for _key in _data:
            _data[_key], _, _, _ = self.populate_metadata(_data[_key])
        _metadata = {
            _key: dict(
                axis_units=_item.axis_units,
                axis_labels=_item.axis_labels,
                axis_ranges=_item.axis_ranges,
            )
            for _key, _item in _data.items()
        }
        H5SAVER.update_frame_metadata(_metadata)
        self.assert_written_files_are_okay(_data, _metadata)

    def test_write_metadata_to_files(self):
        self.prepare_with_defaults()
        _data = self.get_datasets()
        _metadata = {}
        for _node_id in self._shapes:
            _data[_node_id], _labels, _units, _ranges = self.populate_metadata(
                _data[_node_id]
            )
            _metadata[_node_id] = dict(labels=_labels, units=_units, ranges=_ranges)
        H5SAVER.write_metadata_to_files(_data)
        self.assert_written_files_are_okay(_data, _metadata)

    def test_export_full_data_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets(start_dim=0)
        H5SAVER.export_full_data_to_file(_data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                _writtendata = _file["entry/data/data"][()]
            self.assertTrue(np.allclose(_data[_node_id], _writtendata))

    def test_export_full_data_to_file__same_dataset(self):
        self.prepare_with_defaults()
        _data = self.get_datasets(start_dim=1)
        H5SAVER.export_full_data_to_file(_data)
        _data = self.get_datasets(start_dim=0)
        H5SAVER.export_full_data_to_file(_data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                _writtendata = _file["entry/data/data"][()]
            self.assertTrue(np.allclose(_data[_node_id], _writtendata))

    def test_export_frame_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets()
        _index = 23
        _scanindex = SCAN.get_frame_position_in_scan(_index)
        H5SAVER.export_frame_to_file(_index, _data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                _written_data = _file["entry/data/data"][_scanindex]
            self.assertTrue(np.allclose(_written_data, _data[_node_id]))

    def test_import_results_from_file(self):
        _data, _node_info, _scan = H5SAVER.import_results_from_file(
            self._import_test_filename
        )
        self.assertEqual(_node_info["node_label"], self._import_label)
        self.assertEqual(_node_info["data_label"], self._import_data_label)
        for _ax in range(_data.ndim):
            self.assertEqual(self._import_data_ax_labels[_ax], _data.axis_labels[_ax])
            self.assertEqual(self._import_data_units[_ax], _data.axis_units[_ax])
            if isinstance(self._import_data_ranges[_ax], np.ndarray):
                self.assertTrue(
                    np.allclose(self._import_data_ranges[_ax], _data.axis_ranges[_ax])
                )
            else:
                self.assertEqual(self._import_data_ranges[_ax], _data.axis_ranges[_ax])
        self.assertEqual(_scan["scan_title"], self._import_title)
        self.assertEqual(_scan["scan_dim"], 2)
        _ranges = self._import_data_ranges
        for _dim in [0, 1]:
            _label = self._import_data_ax_labels[_dim]
            _label = _label if _label is not None else ""
            self.assertEqual(
                _scan[_dim],
                {
                    "scan_label": _label,
                    "unit": self._import_data_units[_dim],
                    "delta": _ranges[_dim][1] - _ranges[_dim][0],
                    "offset": _ranges[_dim][0],
                    "n_points": _ranges[_dim].size,
                },
            )

    def test_import_results_from_file__with_None(self):
        _new_name = os.path.join(self._dir, "import_test_with_None.h5")
        shutil.copy(self._import_test_filename, _new_name)
        with h5py.File(_new_name, "r+") as _file:
            del _file["entry/scan/dim_0/range"]
            create_hdf5_dataset(_file, "entry/scan/dim_0", "range", data=None)
            del _file["entry/scan/dim_0/unit"]
            create_hdf5_dataset(_file, "entry/scan/dim_0", "unit", data=None)
            del _file["entry/scan/dim_0/label"]
            create_hdf5_dataset(_file, "entry/scan/dim_0", "label", data=None)
        _data, _node_info, _scan = H5SAVER.import_results_from_file(_new_name)
        self.assertEqual(_scan[0]["delta"], 1)
        self.assertEqual(_scan[0]["offset"], 0)
        self.assertEqual(_scan[0]["n_points"], _data.shape[0])


if __name__ == "__main__":
    unittest.main()
