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


import os
import random
import shutil
import tempfile
import unittest
from numbers import Integral, Real

import h5py
import numpy as np

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string, read_and_decode_hdf5_dataset
from pydidas.unittest_objects import create_hdf5_results_file
from pydidas.workflow import WorkflowResults, WorkflowTree
from pydidas.workflow.result_io import WorkflowResultIoMeta
from pydidas.workflow.result_io.workflow_result_io_hdf5 import WorkflowResultIoHdf5


TREE = WorkflowTree()
SCAN = ScanContext()
EXP = DiffractionExperimentContext()
RESULTS = WorkflowResults()
META = WorkflowResultIoMeta
H5SAVER = WorkflowResultIoHdf5


class TestWorkflowResultIoHdf5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp()
        SCAN.restore_all_defaults(confirm=True)
        SCAN.set_param_value("scan_dim", 2)
        for d in range(4):
            SCAN.set_param_value(f"scan_dim{d}_n_points", random.choice([3, 5, 7, 8]))
            SCAN.set_param_value(
                f"scan_dim{d}_delta", random.choice([0.1, 0.5, 1, 1.5])
            )
            SCAN.set_param_value(f"scan_dim{d}_offset", random.choice([-0.1, 0.5, 1]))
            SCAN.set_param_value(f"scan_dim{d}_label", get_random_string(12))
        for _key in EXP.params:
            if EXP.params[_key].dtype == Integral:
                EXP.set_param_value(_key, int(100 * np.random.random()))
            elif EXP.params[_key].dtype == Real:
                EXP.set_param_value(_key, np.random.random())
            elif EXP.params[_key].dtype == str:
                EXP.set_param_value(_key, get_random_string(12))
        cls._create_h5_test_file()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._dir)

    @classmethod
    def _create_h5_test_file(cls):
        cls._import_test_filename = os.path.join(cls._dir, "import_test.h5")
        cls._data = Dataset(
            np.random.random((9, 9, 27)),
            data_label=get_random_string(12),
            data_unit=get_random_string(3),
            axis_labels={0: "None", 1: None, 2: "Label"},
            axis_units={0: "u1", 1: "u2", 2: None},
            axis_ranges={
                0: np.arange(9),
                1: np.arange(9) - 3,
                2: np.linspace(12, -5, num=27),
            },
        )
        cls._io_node_label = get_random_string(9)
        cls._import_plugin_name = get_random_string(8)
        create_hdf5_results_file(
            cls._import_test_filename,
            cls._data,
            SCAN.get_param_values_as_dict(filter_types_for_export=True),
            EXP.get_param_values_as_dict(filter_types_for_export=True),
            TREE,
            node_label=cls._io_node_label,
            plugin_name=cls._import_plugin_name,
        )

    def setUp(self): ...

    def tearDown(self): ...

    def prepare_with_defaults(self):
        _scan_shape = tuple(
            SCAN.get_param_value(f"scan_dim{i}_n_points") for i in range(3)
        )
        self._shapes = {
            1: _scan_shape + (12, 7),
            2: _scan_shape + (23,),
            3: _scan_shape + (1, 3, 7),
        }
        self._labels = {1: "Test", 2: "not again", 3: "another"}
        self._datalabels = {1: "Intensity", 2: "Peak height", 3: "Area"}
        self._dataunits = {1: "a.u.", 2: "km", 3: "square inch"}
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
                "data_unit": self._dataunits[_node],
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
        dataset.data_label = get_random_string(12)
        dataset.data_unit = get_random_string(3)
        for _axis in _labels:
            dataset.update_axis_label(_axis, _labels[_axis])
            dataset.update_axis_unit(_axis, _units[_axis])
            dataset.update_axis_range(_axis, _ranges[_axis])
        return dataset, _labels, _units, _ranges

    def assert_written_files_are_okay(self, data, metadata):
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                self.assertEqual(
                    read_and_decode_hdf5_dataset(_file["entry/data_label"]),
                    metadata[_node_id]["data_label"],
                )
                self.assertEqual(
                    read_and_decode_hdf5_dataset(_file["entry/data_unit"]),
                    metadata[_node_id]["data_unit"],
                )
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
        H5SAVER._create_file_and_populate_metadata(_node_id, SCAN, EXP, TREE)
        with h5py.File(os.path.join(self._resdir, self._filenames[1]), "r") as _file:
            _data = _file["entry/data/data"]
            self.assertEqual(_data.shape, self._shapes[1])
            self.assertIsInstance(_data, h5py.Dataset)

    def test_update_metadata__standard(self):
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
                data_label=_data[_key].data_label,
                data_unit=_data[_key].data_unit,
            )
            for _key, _item in _data.items()
        }
        H5SAVER.update_metadata(_metadata)
        self.assert_written_files_are_okay(_data, _metadata)

    def test_export_full_data_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets(start_dim=0)
        H5SAVER.export_full_data_to_file(_data, SCAN)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                _writtendata = _file["entry/data/data"][()]
            self.assertTrue(np.allclose(_data[_node_id], _writtendata))

    def test_export_full_data_to_file__same_dataset(self):
        self.prepare_with_defaults()
        _data = self.get_datasets(start_dim=1)
        H5SAVER.export_full_data_to_file(_data, SCAN)
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
        _index = 5
        _scanindex = SCAN.get_frame_position_in_scan(_index)
        H5SAVER.export_frame_to_file(_index, _data, SCAN)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, "r") as _file:
                _written_data = _file["entry/data/data"][_scanindex]
            self.assertTrue(np.allclose(_written_data, _data[_node_id]))

    def test_import_results_from_file(self):
        _data, _node_info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            self._import_test_filename
        )
        self.assertEqual(_node_info["node_label"], self._io_node_label)
        self.assertEqual(_data.data_label, self._data.data_label)
        for _ax in range(_data.ndim):
            self.assertEqual(self._data.axis_labels[_ax], _data.axis_labels[_ax])
            self.assertEqual(self._data.axis_units[_ax], _data.axis_units[_ax])
            if isinstance(self._data.axis_ranges[_ax], np.ndarray):
                self.assertTrue(
                    np.allclose(self._data.axis_ranges[_ax], _data.axis_ranges[_ax])
                )
            else:
                self.assertEqual(self._data.axis_ranges[_ax], _data.axis_ranges[_ax])
        for _key, _param in EXP.params.items():
            self.assertEqual(_param.value, _exp.get_param_value(_key))
        for _key, _param in SCAN.params.items():
            self.assertEqual(_param.value, _scan.get_param_value(_key))

    def test_import_results_from_file__with_missing_data(self):
        _new_name = os.path.join(self._dir, "import_test_with_None.h5")
        shutil.copy(self._import_test_filename, _new_name)
        with h5py.File(_new_name, "r+") as _file:
            del _file["entry/pydidas_config/scan/scan_dim0_n_points"]
            del _file["entry/pydidas_config/scan/scan_dim0_unit"]
            del _file["entry/pydidas_config/scan/scan_dim0_label"]
        with self.assertRaises(UserConfigError):
            _data, _node_info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
                _new_name
            )


if __name__ == "__main__":
    unittest.main()
