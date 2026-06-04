# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import random
import shutil
import tempfile
import unittest
from numbers import Integral, Real
from pathlib import Path

import h5py
import numpy as np

from pydidas.contexts import (
    DiffractionExperimentContext,
    Scan,
    ScanContext,
)
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5 import read_and_decode_hdf5_dataset
from pydidas.unittest_objects import create_hdf5_results_file
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow import ProcessingResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoMeta
from pydidas.workflow.result_io.processing_result_io_hdf5 import ProcessingResultIoHdf5


TREE = WorkflowTree()
SCAN = ScanContext()
EXP = DiffractionExperimentContext()
RESULTS = ProcessingResults()
META = ProcessingResultIoMeta
H5SAVER = ProcessingResultIoHdf5


class TestProcessingResultIoHdf5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = Path(tempfile.mkdtemp())
        SCAN.restore_all_defaults(confirm=True)
        SCAN.set_param_value("scan_dim", 3)
        for d in range(4):
            SCAN.set_param_value(f"scan_dim{d}_n_points", random.choice([3, 5, 7, 8]))
            SCAN.set_param_value(
                f"scan_dim{d}_delta", random.choice([0.1, 0.5, 1, 1.5])
            )
            SCAN.set_param_value(f"scan_dim{d}_offset", random.choice([-0.1, 0.5, 1]))
            SCAN.set_param_value(f"scan_dim{d}_label", get_random_string(12))
            SCAN.set_param_value(f"scan_dim{d}_unit", get_random_string(3))
        for _key in EXP.params:
            if EXP.params[_key].dtype == Integral:
                EXP.set_param_value(_key, int(100 * np.random.random()))
            elif EXP.params[_key].dtype == Real:
                EXP.set_param_value(_key, np.random.random())
            elif EXP.params[_key].dtype == str:
                EXP.set_param_value(_key, get_random_string(12))
        cls._create_h5_test_file()
        cls._create_h5_squeezed_test_files()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._dir)

    @classmethod
    def _make_scan_with_size1_dim(cls) -> Scan:
        """Return a Scan with dim0 having n_points=1 and dim1 having n_points=5."""
        _scan = Scan()
        _scan.set_param_value("scan_dim", 3)
        _scan.set_param_value("scan_dim0_n_points", 3)
        _scan.set_param_value("scan_dim0_delta", 1.0)
        _scan.set_param_value("scan_dim0_offset", 0.5)
        _scan.set_param_value("scan_dim0_label", "motor0")
        _scan.set_param_value("scan_dim0_unit", "mm")
        _scan.set_param_value("scan_dim1_n_points", 1)
        _scan.set_param_value("scan_dim1_delta", 0.2)
        _scan.set_param_value("scan_dim1_offset", 1.0)
        _scan.set_param_value("scan_dim1_label", "motor1")
        _scan.set_param_value("scan_dim1_unit", "deg")
        _scan.set_param_value("scan_dim2_n_points", 7)
        _scan.set_param_value("scan_dim2_delta", 0.5)
        _scan.set_param_value("scan_dim2_offset", 1.0)
        _scan.set_param_value("scan_dim2_label", "motor2")
        _scan.set_param_value("scan_dim2_unit", "um")
        return _scan

    @classmethod
    def _create_h5_squeezed_test_files(cls):
        """
        Create HDF5 result files with squeezed scan data for import tests.

        Four files are created:
        - import_test_squeezed.h5          : ``squeezed_scan_dims = [1]``
        - import_test_squeezed_empty.h5    : ``squeezed_scan_dims = []``
        - import_test_legacy_squeezed.h5   : no ``squeezed_scan_dims`` key (legacy)
        - import_test_legacy_no_match.h5   : no ``squeezed_scan_dims`` key, shape mismatch
        """
        _scan = cls._make_scan_with_size1_dim()  # shape (3, 1, 7)
        _data = cls._squeezed_import_data = create_dataset(
            5, shape=_scan.shape + (5, 7)
        ).squeeze()
        _mismatched_data = create_dataset(4, shape=(2, 3, 4, 5))

        _scan_dict = _scan.get_param_values_as_dict(filter_types_for_export=True)
        _exp_dict = EXP.get_param_values_as_dict(filter_types_for_export=True)

        cls._import_squeezed_filename = cls._dir / "import_test_squeezed.h5"
        cls._import_squeezed_empty_filename = cls._dir / "import_test_squeezed_empty.h5"
        cls._import_legacy_squeezed_filename = (
            cls._dir / "import_test_legacy_squeezed.h5"
        )
        cls._import_legacy_no_match_filename = (
            cls._dir / "import_test_legacy_no_match.h5"
        )
        for _name, _dset, _extra_kwargs in [
            # New-style file: squeezed_scan_dims=[1] written via the kwarg:
            (cls._import_squeezed_filename, _data, {"squeezed_scan_dims": [1]}),
            # New-style file: squeezed_scan_dims=[] (default — nothing was squeezed)
            (cls._import_squeezed_empty_filename, _data, {}),
            # Legacy file: delete squeezed_scan_dims to simulate a file written by an
            # older pydidas version that never wrote the key.
            (cls._import_legacy_squeezed_filename, _data, {}),
            # Legacy file: no squeezed_scan_dims key; data shape does NOT match (no squeeze).
            (cls._import_legacy_no_match_filename, _mismatched_data, {}),
        ]:
            create_hdf5_results_file(
                _name,
                _dset,
                _scan_dict,
                _exp_dict,
                TREE,
                node_label="Label",
                plugin_name="SomePlugin",
                **_extra_kwargs,
            )

        with h5py.File(cls._import_legacy_squeezed_filename, "r+") as _file:
            del _file["entry/pydidas_config/squeezed_scan_dims"]
        with h5py.File(cls._import_legacy_no_match_filename, "r+") as _file:
            del _file["entry/pydidas_config/squeezed_scan_dims"]

    @classmethod
    def _create_h5_test_file(cls):
        cls._import_test_filename = cls._dir / "import_test.h5"
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
        self._shapes = {
            1: SCAN.shape + (12, 7),
            2: SCAN.shape + (23,),
            3: SCAN.shape + (1, 3, 7),
        }
        self._labels = {1: "Test", 2: "not again", 3: "another"}
        self._datalabels = {1: "Intensity", 2: "Peak height", 3: "Area"}
        self._dataunits = {1: "a.u.", 2: "km", 3: "square inch"}
        self._plugin_names = {1: "A plugin", 2: "Plugin no 2.", 3: "Ye olde plugin"}
        self._filenames = {
            1: "node_01_Test.nxs",
            2: "node_02_not_again.nxs",
            3: "node_03_another.nxs",
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
        self._resdir = self._dir / get_random_string(8)
        H5SAVER.prepare_files_and_directories(self._resdir, _node_infos)

    def get_datasets(self, start_dim=3):
        return {
            _key: create_dataset(len(_shape[start_dim:]), shape=_shape[start_dim:])
            for _key, _shape in self._shapes.items()
        }

    def assert_written_files_are_okay(self, data, metadata):
        for _node_id in self._shapes:
            _fname = self._resdir / self._filenames[_node_id]
            with h5py.File(_fname, "r") as _file:
                self.assertEqual(
                    _file["entry/data"].attrs["title"],
                    metadata[_node_id]["data_label"],
                )
                self.assertEqual(
                    _file["entry/data/data"].attrs["units"],
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
        self.assertTrue(self._resdir.exists())
        self.assertEqual(H5SAVER.get_attribute_dict("shape"), self._shapes)
        self.assertEqual(H5SAVER.get_attribute_dict("node_label"), self._labels)
        for _key in self._shapes:
            _fname = H5SAVER._filenames[_key]
            self.assertEqual(_fname, self._filenames[_key])
            self.assertTrue((self._resdir / _fname).exists())

    def test_create_file_and_populate_metadata(self):
        _node_id = 1
        self.prepare_with_defaults()
        H5SAVER._create_file_and_populate_metadata(_node_id, SCAN, EXP, TREE)
        with h5py.File(self._resdir / self._filenames[1], "r") as _file:
            _data = _file["entry/data/data"]
            self.assertEqual(_data.shape, self._shapes[1])
            self.assertIsInstance(_data, h5py.Dataset)

    def test_update_with_scan_metadata(self):
        self.prepare_with_defaults()
        _datasets = self.get_datasets()
        _metadata = H5SAVER.update_with_scan_metadata(_datasets, SCAN)
        for _key, _metadata in _metadata.items():
            self.assertEqual(_metadata["data_label"], _datasets[_key].data_label)
            self.assertEqual(_metadata["data_unit"], _datasets[_key].data_unit)
            for _dim in range(SCAN.ndim):
                self.assertEqual(_metadata["axis_labels"][_dim], SCAN.axis_labels[_dim])
                self.assertEqual(_metadata["axis_units"][_dim], SCAN.axis_units[_dim])
                self.assertTrue(
                    np.allclose(_metadata["axis_ranges"][_dim], SCAN.axis_ranges[_dim])
                )
            for _dim in range(_datasets[_key].ndim - SCAN.ndim):
                self.assertEqual(
                    _metadata["axis_labels"][_dim + SCAN.ndim],
                    _datasets[_key].axis_labels[_dim],
                )
                self.assertEqual(
                    _metadata["axis_units"][_dim + SCAN.ndim],
                    _datasets[_key].axis_units[_dim],
                )
                self.assertTrue(
                    np.allclose(
                        _metadata["axis_ranges"][_dim + SCAN.ndim],
                        _datasets[_key].axis_ranges[_dim],
                    )
                )

    def test_update_metadata__standard(self):
        self.prepare_with_defaults()
        _data = {
            _key: create_dataset(len(_shape[3:]), shape=_shape[3:])
            for _key, _shape in self._shapes.items()
        }
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
            _fname = self._resdir / self._filenames[_node_id]
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
            _fname = self._resdir / self._filenames[_node_id]
            with h5py.File(_fname, "r") as _file:
                _writtendata = _file["entry/data/data"][()]
            self.assertTrue(np.allclose(_data[_node_id], _writtendata))

    def test_export_frame_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets()
        _index = 5
        _scan_indices = SCAN.get_indices_from_ordinal(_index)
        H5SAVER.export_frame_to_file(_index, _data, SCAN)
        for _node_id in self._shapes:
            _fname = self._resdir / self._filenames[_node_id]
            with h5py.File(_fname, "r") as _file:
                _written_data = _file["entry/data/data"][_scan_indices]
            self.assertTrue(np.allclose(_written_data, _data[_node_id].array))

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
            if _param.dtype == Real:
                self.assertAlmostEqual(_param.value, _exp.get_param_value(_key))
            else:
                self.assertEqual(_param.value, _exp.get_param_value(_key))
        for _key, _param in SCAN.params.items():
            if _param.dtype == Real:
                self.assertAlmostEqual(_param.value, _scan.get_param_value(_key))
            else:
                self.assertEqual(_param.value, _scan.get_param_value(_key))

    def test_import_results_from_file__with_missing_data(self):
        _new_name = self._dir / "import_test_with_None.h5"
        shutil.copy(self._import_test_filename, _new_name)
        with h5py.File(_new_name, "r+") as _file:
            del _file["entry/pydidas_config/scan/scan_dim0_n_points"]
            del _file["entry/pydidas_config/scan/scan_dim0_unit"]
            del _file["entry/pydidas_config/scan/scan_dim0_label"]
        with self.assertRaises(UserConfigError):
            _data, _node_info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
                _new_name
            )

    def test_insert_squeezed_scan_dims__single_dim(self):
        _scan = self._make_scan_with_size1_dim()
        _data = Dataset(
            np.random.random((3, 7, 12)),
            axis_labels={
                0: _scan.axis_labels[0], 1: _scan.axis_labels[2], 2: "data_label"
            },
            axis_units={0: _scan.axis_units[0], 1: _scan.axis_units[2], 2: "data_unit"},
            axis_ranges={
                0: _scan.axis_ranges[0],
                1: _scan.axis_ranges[2],
                2: np.linspace(11, 12, 12),
            },
        )
        _result = H5SAVER._insert_squeezed_scan_dims(_data, _scan, [1])
        self.assertEqual(_result.shape, (3, 1, 7, 12))
        for _dim in [0, 1, 2]:
            self.assertEqual(
                _result.axis_labels[_dim],
                _scan.get_param_value(f"scan_dim{_dim}_label"),
            )
            self.assertEqual(
                _result.axis_units[_dim], _scan.get_param_value(f"scan_dim{_dim}_unit")
            )

    def test_insert_squeezed_scan_dims__multiple_dims(self):
        # 3D scan with size-1 dims at indices 0 and 2
        _scan = Scan()
        _scan.set_param_value("scan_dim", 3)
        _scan.set_param_value("scan_dim0_n_points", 1)
        _scan.set_param_value("scan_dim0_delta", 1.0)
        _scan.set_param_value("scan_dim0_offset", 0.0)
        _scan.set_param_value("scan_dim0_label", "motor0")
        _scan.set_param_value("scan_dim0_unit", "mm")
        _scan.set_param_value("scan_dim1_n_points", 5)
        _scan.set_param_value("scan_dim1_delta", 0.1)
        _scan.set_param_value("scan_dim1_offset", 0.0)
        _scan.set_param_value("scan_dim1_label", "motor1")
        _scan.set_param_value("scan_dim1_unit", "deg")
        _scan.set_param_value("scan_dim2_n_points", 1)
        _scan.set_param_value("scan_dim2_delta", 1.0)
        _scan.set_param_value("scan_dim2_offset", 0.0)
        _scan.set_param_value("scan_dim2_label", "motor2")
        _scan.set_param_value("scan_dim2_unit", "um")
        # Squeezed data has shape (5, 12): only scan dim1 + plugin dim
        _data = Dataset(
            np.random.random((5, 12)),
            axis_labels={0: "motor1_ax", 1: "intensity"},
            axis_units={0: "deg", 1: "a.u."},
            axis_ranges={0: np.linspace(0, 0.4, 5), 1: np.arange(12, dtype=float)},
        )
        _result = H5SAVER._insert_squeezed_scan_dims(_data, _scan, [0, 2])
        # Expected shape: (1, 5, 1, 12) — dim0 and dim2 re-inserted
        self.assertEqual(_result.shape, (1, 5, 1, 12))
        self.assertEqual(_result.axis_labels[0], "motor0")
        self.assertEqual(_result.axis_labels[1], "motor1_ax")
        self.assertEqual(_result.axis_labels[2], "motor2")
        self.assertEqual(_result.axis_labels[3], "intensity")

    def test_insert_squeezed_scan_dims__values_preserved(self):
        # scan shape (3, 1, 7) — dim1 is size-1; squeezed data has shape (3, 7, 8)
        _scan = self._make_scan_with_size1_dim()
        _original = np.random.random((3, 7, 8))
        _data = Dataset(
            _original,
            axis_labels={0: "ax0", 1: "ax1", 2: "ax2"},
            axis_units={0: "u0", 1: "u1", 2: "u2"},
            axis_ranges={
                0: np.linspace(0.5, 2.5, 3),
                1: np.linspace(1.0, 4.0, 7),
                2: np.arange(8, dtype=float),
            },
        )
        _result = H5SAVER._insert_squeezed_scan_dims(_data, _scan, [1])
        self.assertTrue(np.allclose(_result.squeeze(), _original))

    # ------------------------------------------------------------------
    # Tests for update_metadata with squeeze=True
    # ------------------------------------------------------------------

    def test_update_metadata__with_squeeze(self):
        _scan = self._make_scan_with_size1_dim()  # shape (3, 1, 7); dim1 is size-1
        _plugin_shape = (12, 7)
        _full_shape = _scan.shape + _plugin_shape  # (3, 1, 7, 12, 7)
        _node_infos = {
            1: {
                "node_label": "SqueezedNode",
                "data_label": "Intensity",
                "data_unit": "a.u.",
                "shape": _plugin_shape,  # plugin output dims only (no scan dims yet)
                "plugin_name": "SomeProcPlugin",
            }
        }
        _resdir = self._dir / get_random_string(8)
        H5SAVER.prepare_files_and_directories(_resdir, _node_infos, scan_context=_scan)
        # Build a full Dataset (scan dims + plugin dims) for metadata extraction
        _data = Dataset(
            np.random.random(_full_shape),
            axis_labels={i: f"ax{i}" for i in range(len(_full_shape))},
            axis_units={i: f"u{i}" for i in range(len(_full_shape))},
            axis_ranges={
                i: np.arange(_full_shape[i], dtype=float)
                for i in range(len(_full_shape))
            },
        )
        H5SAVER.update_metadata({1: _data}, scan=_scan, squeeze=True)
        _fname = _resdir / H5SAVER._filenames[1]
        with h5py.File(_fname, "r") as _file:
            _squeezed_dims = list(_file["entry/pydidas_config/squeezed_scan_dims"][()])
        self.assertEqual(_squeezed_dims, [1])

    # ------------------------------------------------------------------
    # Tests for export_full_data_to_file with squeeze=True
    # ------------------------------------------------------------------

    def test_export_full_data_to_file__with_squeeze(self):
        _scan = self._make_scan_with_size1_dim()  # shape (3, 1, 7); dim1 is size-1
        _plugin_shape = (12, 7)
        _full_shape = _scan.shape + _plugin_shape  # (3, 1, 7, 12, 7)
        _squeezed_shape = (3, 7) + _plugin_shape  # (3, 7, 12, 7)
        # Pre-allocate with the squeezed shape so the squeezed write fits
        _node_infos = {
            1: {
                "node_label": "SqueezedNode",
                "data_label": "Intensity",
                "data_unit": "a.u.",
                "shape": _squeezed_shape,
                "plugin_name": "SomeProcPlugin",
            }
        }
        _resdir = self._dir / get_random_string(8)
        H5SAVER.prepare_files_and_directories(_resdir, _node_infos, scan_context=_scan)
        _full_data = {1: Dataset(np.random.random(_full_shape))}
        H5SAVER.export_full_data_to_file(_full_data, scan_context=_scan, squeeze=True)
        _fname = _resdir / H5SAVER._filenames[1]
        with h5py.File(_fname, "r") as _file:
            _written = _file["entry/data/data"][()]
            _squeezed_dims = list(_file["entry/pydidas_config/squeezed_scan_dims"][()])
        self.assertEqual(_written.shape, _squeezed_shape)
        self.assertTrue(np.allclose(_written, _full_data[1].squeeze().array))
        self.assertEqual(_squeezed_dims, [1])

    # ------------------------------------------------------------------
    # Tests for import_results_from_file with squeezed dims
    # ------------------------------------------------------------------

    def test_import_results_from_file__with_squeezed_dims_flag(self):
        # Squeezed data stored as (3, 7, 5, 7); after import: (3, 1, 7, 5, 7).
        _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            self._import_squeezed_filename
        )
        self.assertEqual(_data.shape, (3, 1, 7, 5, 7))
        # The re-inserted dim gets its metadata from the scan
        self.assertEqual(_data.axis_labels[1], "motor1")
        self.assertEqual(_data.axis_units[1], "deg")
        # The axis that was at position 0 in the squeezed data stays at position 0
        self.assertEqual(
            _data.axis_labels[0], self._squeezed_import_data.axis_labels[0]
        )

    def test_import_results_from_file__with_empty_squeezed_dims_flag(self):
        # File has squeezed_scan_dims=[] (empty); no re-insertion expected.
        # Squeezed data was stored as (3, 7, 5, 7); shape must stay the same.
        _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            self._import_squeezed_empty_filename
        )
        self.assertEqual(_data.shape, (3, 7, 5, 7))

    def test_import_results_from_file__legacy_squeezed_dims(self):
        # Legacy file has no squeezed_scan_dims key.
        # scan has dim1 with n_points=1; _scan_shape_no_ones=(3, 7).
        # Stored data shape (3, 7, 5, 7) starts with (3, 7) → backward compat re-inserts dim1.
        _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            self._import_legacy_squeezed_filename
        )
        self.assertEqual(_data.shape, (3, 1, 7, 5, 7))
        self.assertEqual(_data.axis_labels[1], "motor1")
        self.assertEqual(_data.axis_units[1], "deg")

    def test_import_results_from_file__legacy_size1_dims_shape_no_match(self):
        # Legacy file: scan has size-1 dim0, but data shape (3, 27) does NOT
        # match the non-size-1 scan prefix (5,) → no re-insertion.
        _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            self._import_legacy_no_match_filename
        )
        self.assertEqual(_data.shape, (2, 3, 4, 5))


if __name__ == "__main__":
    unittest.main()
