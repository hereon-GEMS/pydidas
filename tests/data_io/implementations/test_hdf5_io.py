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
import shutil
import tempfile
import unittest
from numbers import Integral
from pathlib import Path

import h5py
import numpy as np

from pydidas.core import Dataset, FileReadError, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.data_io.implementations.hdf5_io import Hdf5Io


class TestHdf5Io(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())
        cls._fname = cls._path.joinpath("test.h5")
        cls._data_shape = (12, 13, 14, 15)
        cls._data_slice = (
            slice(None, None),
            slice(None, None),
            slice(None, None),
            slice(0, 4),
        )
        cls._data = Dataset(
            np.random.random(cls._data_shape),
            axis_labels=["x", "y", "z", "chi"],
            axis_units=["x_unit", "unit4y", "z unit", "deg"],
            axis_ranges=[
                5 * np.arange(cls._data_shape[0]) + 42,
                0.3 * np.arange(cls._data_shape[1]) - 5,
                4 * np.arange(cls._data_shape[2]),
                -42 * np.arange(cls._data_shape[3]) + 127,
            ],
            data_label="test data",
            data_unit="hbar / lightyear",
        )
        with h5py.File(cls._fname, "w") as _file:
            _file["test/path/data"] = cls._data
            _file["entry/data/data"] = cls._data[cls._data_slice]
            cls._written_shape = _file["entry/data/data"].shape
            for _path in ["test/path", "entry/data"]:
                _local_data = (
                    cls._data if _path == "test/path" else cls._data[cls._data_slice]
                )
                _file[os.path.dirname(_path)].create_dataset(
                    "data_label", data=_local_data.data_label
                )
                _file[os.path.dirname(_path)].create_dataset(
                    "data_unit", data=_local_data.data_unit
                )
                for _ax in range(_local_data.ndim):
                    _group = _file[_path].create_group(f"axis_{_ax}")
                    for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                        _group.create_dataset(
                            _key[5:-1], data=getattr(_local_data, _key)[_ax]
                        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self): ...

    def test_class_extensions(self):
        for _ext in HDF5_EXTENSIONS:
            self.assertIn(_ext, Hdf5Io.extensions_export)
            self.assertIn(_ext, Hdf5Io.extensions_import)

    def test_import_from_file__simple(self):
        _data = Hdf5Io.import_from_file(self._fname, import_pydidas_metadata=False)
        self.assertTrue(np.allclose(_data, self._data[self._data_slice]))

    def test_import_from_file__full(self):
        _data = Hdf5Io.import_from_file(self._fname)
        _ref_data = self._data[self._data_slice]
        self.assertTrue(np.allclose(_data, self._data[self._data_slice]))
        for _ax in range(_data.ndim):
            for _key in ["axis_labels", "axis_units"]:
                self.assertEqual(
                    getattr(_data, _key)[_ax], getattr(_ref_data, _key)[_ax]
                )
            self.assertTrue(
                np.allclose(_data.axis_ranges[_ax], _ref_data.axis_ranges[_ax])
            )
        self.assertEqual(_data.data_label, self._data.data_label)
        self.assertEqual(_data.data_unit, self._data.data_unit)

    def test_import_from_file__wrong_name(self):
        with self.assertRaises(FileReadError):
            Hdf5Io.import_from_file(self._fname.joinpath("dummy"), datatype=np.float64)

    def test_import_from_file__wrong_type(self):
        _fname_new = self._path.joinpath("test2.dat")
        with open(_fname_new, "w") as f:
            f.write("now it's just an ASCII text file.")
        with self.assertRaises(FileReadError):
            Hdf5Io.import_from_file(_fname_new, datatype=np.float64)

    def test_import_from_file__w_single_index(self):
        for _slice in [((7, 8),), [7], (7,)]:
            with self.subTest(slice=_slice):
                _index = _slice[0] if isinstance(_slice[0], Integral) else _slice[0][0]
                _data = Hdf5Io.import_from_file(
                    self._fname, indices=_slice, import_pydidas_metadata=False
                )
                self.assertTrue(
                    np.allclose(_data, self._data[(_index, *self._data_slice[1:])])
                )

    def test_import_from_file__w_none_indices(self):
        _data = Hdf5Io.import_from_file(
            self._fname, indices=None, import_pydidas_metadata=False
        )
        self.assertTrue(np.allclose(_data, self._data[*self._data_slice]))

    def test_import_from_file__w_none_index(self):
        _data = Hdf5Io.import_from_file(
            self._fname, indices=(None,), import_pydidas_metadata=False
        )
        self.assertTrue(np.allclose(_data, self._data[*self._data_slice]))

    def test_import_from_file__zeros_dim_results(self):
        for _slice in [(25,), (None, 27), (26, 65)]:
            with self.subTest(slice=_slice):
                with self.assertRaises(UserConfigError):
                    Hdf5Io.import_from_file(self._fname, indices=_slice)

    def test_import_from_file__2_consecutive_indices(self):
        _data = Hdf5Io.import_from_file(
            self._fname, indices=(1, 3), import_pydidas_metadata=False
        )
        self.assertTrue(np.allclose(_data, self._data[(1, 3, *self._data_slice[2:])]))

    def test_import_from_file__2_separate_slicing_axes(self):
        _data = Hdf5Io.import_from_file(
            self._fname, indices=(5, None, 3), import_pydidas_metadata=False
        )
        self.assertTrue(
            np.allclose(
                _data, self._data[5, self._data_slice[1], 3, self._data_slice[3]]
            )
        )

    def test_complex_indexing(self):
        _data = Hdf5Io.import_from_file(
            self._fname,
            indices=((5, None), None, (None, 3)),
            import_pydidas_metadata=False,
        )
        self.assertTrue(np.allclose(_data, self._data[5:, :, :3, self._data_slice[3]]))

    def test_import_from_file__w_dataset(self):
        _data = Hdf5Io.import_from_file(
            self._fname, dataset="test/path/data", import_pydidas_metadata=False
        )
        self.assertTrue(np.allclose(_data, self._data))

    def test_import_from_file__metadata_was_copied(self):
        _data = Hdf5Io.import_from_file(self._fname, import_pydidas_metadata=False)
        self.assertIn("indices", _data.metadata)
        self.assertIn("dataset", _data.metadata)

    def test_export_to_file__file_exists(self):
        with self.assertRaises(FileExistsError):
            Hdf5Io.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = self._path.joinpath("test_new.h5")
        Hdf5Io.export_to_file(_fname, self._data)
        Hdf5Io.export_to_file(_fname, self._data[:11], overwrite=True)
        _data = Hdf5Io.import_from_file(_fname)
        self.assertEqual(_data.shape, (11,) + self._data_shape[1:])

    def test_export_to_file__w_groupname(self):
        _fname = self._path.joinpath("test_gname.h5")
        Hdf5Io.export_to_file(_fname, self._data, dataset="test/new/new_data")
        _data = Hdf5Io.import_from_file(
            _fname, dataset="test/new/new_data", slicing_axes=[]
        )
        self.assertEqual(_data.shape, self._data_shape)
        self.assertTrue(np.allclose(_data, self._data))


if __name__ == "__main__":
    unittest.main()
