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
from numbers import Real
from pathlib import Path

import h5py
import numpy as np

from pydidas.core import Dataset
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5_dataset_utils import (
    _get_hdf5_file_and_dataset_names,
    convert_data_for_writing_to_hdf5_dataset,
    create_hdf5_dataset,
    create_nx_dataset,
    create_nx_entry_groups,
    create_nxdata_entry,
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
    hdf5_dataset_check,
    read_and_decode_hdf5_dataset,
)


class Test_Hdf5_dataset_utils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        self.file = h5py.File(self._path / "temp_file.h5", "w")

        self._fname = lambda s: self._path.joinpath(f"test{s}.h5")
        self._ref = f"{self._fname(1)}:///test/path/data"
        self._data = np.random.random((10, 10, 10, 10))
        self._fulldsets = [
            "/test/path/data",
            "/test/path/to/data",
            "/test/other/path/data",
        ]
        self._2ddsets = ["/test/path/data2", "/test/other/data"]
        with h5py.File(self._fname("data"), "w") as _file:
            _file.create_group("ext")
            _file["ext"].create_group("path")
            _file["ext/path"].create_dataset("data", data=self._data)
        with h5py.File(self._fname(1), "w") as _file:
            _file.create_group("test")
            _file["test"].create_group("path")
            _file["test/path"].create_group("to")
            _file["test"].create_group("other")
            _file["test/other"].create_group("path")
            for dset in self._fulldsets:
                _file[dset] = self._data
            for dset in self._2ddsets:
                _file[dset] = self._data[0, 0]
            _file["test/other/extdata"] = h5py.ExternalLink(
                self._fname("data"), "/ext/path/data"
            )
        self._fulldsets += ["/test/other/extdata"]

    def tearDown(self):
        # Close and remove the temporary file after tests
        self.file.close()

    def test_get_hdf5_file_and_dataset_names__wrong_type(self):
        _name = 123
        _dset = "/test/dset"
        with self.assertRaises(TypeError):
            _get_hdf5_file_and_dataset_names(_name, _dset)

    def test_get_hdf5_file_and_dataset_names__Path_type(self):
        _name = Path("c:/test/path/testfile.h5")
        _dset = "/test/dset"
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_name, _dset)
        self.assertEqual(_name, Path(_newname))
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names(self):
        _name = "c:/test/path/testfile.h5"
        _dset = "/test/dset"
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_name, _dset)
        self.assertEqual(_name, _newname)
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names__joint_file_and_dset(self):
        _name = "c:/test/path/testfile.h5"
        _dset = "/test/dset"
        _option = f"{_name}://{_dset}"
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_option)
        self.assertEqual(_name, _newname)
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names__only_fname(self):
        _name = "c:/test/path/testfile.h5"
        with self.assertRaises(KeyError):
            _get_hdf5_file_and_dataset_names(_name)

    def test_get_hdf5_metadata_meta__wrong_type(self):
        with self.assertRaises(TypeError):
            get_hdf5_metadata(self._ref, 123)

    def test_get_hdf5_metadata_meta__str(self):
        _res = get_hdf5_metadata(self._ref, "nokey")
        self.assertEqual(_res, dict())

    def test_get_hdf5_metadata_meta__shape(self):
        _shape = get_hdf5_metadata(self._ref, "shape")
        self.assertEqual(_shape, self._data.shape)

    def test_get_hdf5_metadata_meta__dtype(self):
        dtype = get_hdf5_metadata(self._ref, "dtype")
        self.assertEqual(dtype, self._data.dtype)

    def test_get_hdf5_metadata_meta__size(self):
        size = get_hdf5_metadata(self._ref, "size")
        self.assertEqual(size, self._data.size)

    def test_get_hdf5_metadata_meta__ndim(self):
        ndim = get_hdf5_metadata(self._ref, "ndim")
        self.assertEqual(ndim, self._data.ndim)

    def test_get_hdf5_metadata_meta__nbytes(self):
        nbytes = get_hdf5_metadata(self._ref, "nbytes")
        self.assertEqual(nbytes, self._data.nbytes)

    def test_get_hdf5_metadata_meta__wrong_key(self):
        with self.assertRaises(KeyError):
            get_hdf5_metadata(self._ref + "/more", "dtype")

    def test_get_hdf5_metadata_meta__multiples(self):
        _res = get_hdf5_metadata(self._ref, ("ndim", "size"))
        self.assertEqual(_res, dict(ndim=self._data.ndim, size=self._data.size))

    def test_hdf5_dataset_check__no_dset(self):
        self.assertFalse(hdf5_dataset_check("something"))

    def test_hdf5_dataset_check__simple(self):
        with h5py.File(self._fname(2), "w") as _file:
            _file.create_group("test")
            _file["test"].create_dataset("data", data=self._data)
            self.assertTrue(hdf5_dataset_check(_file["test/data"]))

    def test_hdf5_dataset_check__dim(self):
        with h5py.File(self._fname(2), "w") as _file:
            _file.create_group("test")
            _file["test"].create_dataset("data", data=self._data)
            self.assertFalse(hdf5_dataset_check(_file["test/data"], min_dim=5))

    def test_hdf5_dataset_check__size(self):
        with h5py.File(self._fname(2), "w") as _file:
            _file.create_group("test")
            _file["test"].create_dataset("data", data=self._data)
            self.assertFalse(hdf5_dataset_check(_file["test/data"], min_size=50000))

    def test_hdf5_dataset_check__to_ignore(self):
        with h5py.File(self._fname(2), "w") as _file:
            _file.create_group("test")
            _file["test"].create_dataset("data", data=self._data)
            self.assertFalse(
                hdf5_dataset_check(_file["test/data"], to_ignore=("test/data"))
            )

    def test_get_hdf5_populated_dataset__unknown_extension(self):
        with self.assertRaises(TypeError):
            get_hdf5_populated_dataset_keys(self._fname(1) + ".other")

    def test_get_hdf5_populated_dataset__wrong_input_datatype(self):
        _res = get_hdf5_populated_dataset_keys([1, 2, 3])
        self.assertEqual(_res, [])

    def test_get_hdf5_populated_dataset_keys__w_str(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1))
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys__w_Path(self):
        _res = get_hdf5_populated_dataset_keys(Path(self._fname(1)))
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys__min_dim(self):
        _res = get_hdf5_populated_dataset_keys(Path(self._fname(1)), min_dim=3)
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_get_hdf5_populated_dataset_keys__w_h5py_file(self):
        with h5py.File(self._fname(1), "r") as _file:
            _res = get_hdf5_populated_dataset_keys(_file)
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys__w_h5py_dset(self):
        with h5py.File(self._fname(1), "r") as _file:
            _res = get_hdf5_populated_dataset_keys(_file["test"])
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys_smaller_dim(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1), min_dim=1)
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys_larger_size(self):
        _res = get_hdf5_populated_dataset_keys(
            self._fname(1), min_dim=1, min_size=50000
        )
        self.assertEqual(set(_res), set())

    def test_get_hdf5_populated_dataset_keys__medium_size(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1), min_dim=1, min_size=1000)
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_convert_data_for_writing_to_hdf5_dataset__None(self):
        _data = convert_data_for_writing_to_hdf5_dataset(None)
        self.assertEqual(_data, "::None::")
        self.assertIsInstance(_data, str)

    def test_convert_data_for_writing_to_hdf5_dataset__data(self):
        _input = np.random.random((12, 12))
        _data = convert_data_for_writing_to_hdf5_dataset(_input)
        self.assertTrue(np.allclose(_data, _input))
        self.assertIsInstance(_data, np.ndarray)

    def test_read_and_decode_hdf5_dataset__string(self):
        _input = get_random_string(30)
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset)
        self.assertIsInstance(_out, str)
        self.assertEqual(_out, _input)

    def test_read_and_decode_hdf5_dataset__group_not_None(self):
        _input = get_random_string(30)
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset, group="test")
        self.assertIsInstance(_out, str)
        self.assertEqual(_out, _input)

    def test_read_and_decode_hdf5_dataset__dataset_not_None(self):
        _input = get_random_string(30)
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset, dataset="Test")
        self.assertIsInstance(_out, str)
        self.assertEqual(_out, _input)

    def test_read_and_decode_hdf5_dataset__dataset_and_group_not_None(self):
        _input = get_random_string(30)
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_file, "entry", "test")
        self.assertIsInstance(_out, str)
        self.assertEqual(_out, _input)

    def test_read_and_decode_hdf5_dataset__None(self):
        _input = "::None::"
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset)
        self.assertIsNone(_out)

    def test_read_and_decode_hdf5_dataset__ndarray(self):
        _input = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset)
        self.assertIsInstance(_out, Dataset)
        self.assertTrue(np.allclose(_out, _input))

    def test_read_and_decode_hdf5_dataset__ndarray_without_return_dataset(self):
        _input = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset, return_dataset=False)
        self.assertIsInstance(_out, np.ndarray)
        self.assertFalse(isinstance(_out, Dataset))
        self.assertTrue(np.allclose(_out, _input))

    def test_read_and_decode_hdf5_dataset__list(self):
        _input = [1, 2, 3]
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset)
        self.assertIsInstance(_out, Dataset)
        self.assertTrue(np.allclose(_out, _input))

    def test_read_and_decode_hdf5_dataset__float(self):
        _input = 12.4
        with h5py.File(self._fname("dummy"), "w") as _file:
            _group = _file.create_group("entry")
            _dset = _group.create_dataset("test", data=_input)
            _out = read_and_decode_hdf5_dataset(_dset)
        self.assertIsInstance(_out, Real)
        self.assertEqual(_input, _out)

    def test_create_hdf5_dataset__w_data(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, data=_input)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertIsInstance(_out, Dataset)
        self.assertTrue(np.allclose(_out, _input))

    def test_create_hdf5_dataset__w_shape(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, shape=_input.shape)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertIsInstance(_out, Dataset)
        self.assertEqual(_input.shape, _out.shape)

    def test_create_hdf5_dataset__w_None(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = None
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, data=_input)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertIsNone(_out)

    def test_create_hdf5_dataset__w_str(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = get_random_string(20)
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, data=_input)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertEqual(_input, _out)

    def test_create_hdf5_dataset__w_int(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = 42
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, data=_input)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertEqual(_input, _out)

    def test_create_hdf5_dataset__existing_dataset(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = 42
        _input_new = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            create_hdf5_dataset(_file, _group, _dname, data=_input)
            create_hdf5_dataset(_file, _group, _dname, data=_input_new)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertIsInstance(_out, Dataset)
        self.assertTrue(np.allclose(_out, _input_new))

    def test_create_hdf5_dataset__no_group(self):
        _group = "entry/test"
        _dname = "test_dataset"
        _input = np.random.random((30, 30))
        with h5py.File(self._fname("dummy"), "w") as _file:
            _file.create_group(_group)
            create_hdf5_dataset(_file[_group], None, _dname, data=_input)
            _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
        self.assertIsInstance(_out, Dataset)
        self.assertTrue(np.allclose(_out, _input))

    def test_create_nx_entry_groups__basic(self):
        group_name = "entry/test"
        group_type = "NXdata"
        attributes = {"attr1": "value1", "attr2": "value2"}
        group = create_nx_entry_groups(self.file, group_name, group_type, **attributes)
        self.assertIn(group_name, self.file)
        self.assertEqual(group.attrs["NX_class"], group_type)
        for key, value in attributes.items():
            self.assertEqual(group.attrs[key], value)

    def test_create_nx_entry_groups__nested(self):
        group_name = "entry/test/nested"
        group_type = "NXentry"
        attributes = {"attr1": "value1"}
        group = create_nx_entry_groups(self.file, group_name, group_type, **attributes)
        self.assertIn(group_name, self.file)
        self.assertEqual(group.attrs["NX_class"], group_type)
        for key, value in attributes.items():
            self.assertEqual(group.attrs[key], value)

    def test_create_nx_entry_groups__no_attributes(self):
        group_name = "entry/test"
        group_type = "NXdata"
        group = create_nx_entry_groups(self.file, group_name, group_type)
        self.assertIn(group_name, self.file)
        self.assertEqual(group.attrs["NX_class"], group_type)

    def test_create_nx_entry_groups__w_existing_group(self):
        group_name = "entry/test/group/name"
        group_type = "NXentry"
        group = create_nx_entry_groups(self.file, group_name, group_type)
        group2 = create_nx_entry_groups(self.file, group_name, group_type)
        self.assertEqual(group, group2)

    def test_create_nx_entry_groups__w_existing_group_different_type(self):
        group_name = "entry/test/group/name"
        group_type = "NXentry"
        _ = create_nx_entry_groups(self.file, group_name, group_type)
        with self.assertRaises(ValueError):
            create_nx_entry_groups(self.file, group_name, "AnotherEntry")

    def test_create_nxdata_entry__basic(self):
        name = "entry/test"
        data = np.random.random((10, 10))
        attributes = {"attr1": "value1", "attr2": "value2"}
        group = create_nxdata_entry(self.file, name, data, **attributes)
        self.assertIn(name, self.file)
        self.assertEqual(group.attrs["NX_class"], "NXdata")
        for key, value in attributes.items():
            self.assertEqual(group.attrs[key], value)

    def test_create_nxdata_entry__w_axes(self):
        name = "entry/test"
        data = Dataset(
            np.random.random((10, 10)),
            axis_labels=["x", "y"],
            axis_units=["m", "s"],
            axis_ranges=[np.arange(10), np.arange(10)],
        )
        attributes = {"attr1": "value1"}
        group = create_nxdata_entry(self.file, name, data, **attributes)
        self.assertIn(name, self.file)
        self.assertEqual(group.attrs["NX_class"], "NXdata")
        for key, value in attributes.items():
            self.assertEqual(group.attrs[key], value)
        for dim in range(data.ndim):
            self.assertIn(f"axis_{dim}_repr", group)
            self.assertTrue(
                np.allclose(group[f"axis_{dim}_repr"][()], data.axis_ranges[dim])
            )
            axis_group = group[f"axis_{dim}"]
            self.assertEqual(axis_group["label"][()].decode(), data.axis_labels[dim])
            self.assertEqual(axis_group["unit"][()].decode(), data.axis_units[dim])
            self.assertTrue(np.allclose(axis_group["range"][()], data.axis_ranges[dim]))

    def test_create_nx_dataset__basic(self):
        group = self.file.create_group("entry")
        name = "test_dataset"
        data = np.random.random((10, 10))
        dataset = create_nx_dataset(group, name, data)
        self.assertIn(name, group)
        self.assertTrue(np.array_equal(dataset[()], data))

    def test_create_nx_dataset__w_attributes(self):
        group = self.file.create_group("entry")
        name = "test_dataset"
        data = np.random.random((10, 10))
        attributes = {"units": "meters", "long_name": "Test Dataset"}
        dataset = create_nx_dataset(group, name, data, **attributes)
        self.assertIn(name, group)
        self.assertTrue(np.array_equal(dataset[()], data))
        for key, value in attributes.items():
            self.assertEqual(dataset.attrs[key], value)


if __name__ == "__main__":
    unittest.main()
