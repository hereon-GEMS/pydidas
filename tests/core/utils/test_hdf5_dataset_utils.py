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


from numbers import Real
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pytest

from pydidas.core import Dataset, FileReadError
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5_dataset_utils import (
    _split_hdf5_file_and_dataset_names,
    convert_data_for_writing_to_hdf5_dataset,
    create_hdf5_dataset,
    create_nx_dataset,
    create_nx_entry_groups,
    create_nxdata_entry,
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
    hdf5_dataset_filter_check,
    read_and_decode_hdf5_dataset,
)


_1d_DSETS = ["/test/data1d", "/test/1d/data"]
_2d_DSETS = ["/test/path/data2d", "/test/other_2d/data"]
_3d_DSETS = ["/3d/data/data", "/data/3d/data"]
_4d_DSETS = ["/test/path/4ddata", "/entry/path/to_4d/data", "/test/ext_data/data"]
# _ALL_DSETS does not include the 1d datasets as the default dim filter is 2
_ALL_DSETS = set(_2d_DSETS + _3d_DSETS + _4d_DSETS)


@pytest.fixture(scope="module")
def hdf5_test_data(temp_path):
    """Set up test data and HDF5 files for tests."""
    if not (temp_path / "hdf5_utils").is_dir():
        (temp_path / "hdf5_utils").mkdir()

    def _fname(identifier: Any) -> Path:
        return temp_path / "hdf5_utils" / f"test_{identifier}.h5"

    _data = np.random.random((10, 10, 10, 10))
    _ref = f"{_fname(1)}:///test/path/4ddata"

    # Create file with dataset
    with h5py.File(_fname("data"), "w") as _file:
        _file.create_group("ext")
        _file["ext"].create_group("path")
        _file["ext/path"].create_dataset("data", data=_data)

    # Create main test file with link to external dataset and datasets
    with h5py.File(_fname(1), "w") as _file:
        for dset in _1d_DSETS:
            _file[dset] = _data[0, 0, 0]
        for dset in _2d_DSETS:
            _file[dset] = _data[0, 0]
        for dset in _3d_DSETS:
            _file[dset] = _data[0]
        for dset in _4d_DSETS:
            if dset == "/test/ext_data/data":
                continue
            _file[dset] = _data
        _file["test/ext_data/data"] = h5py.ExternalLink(
            _fname("data"), "/ext/path/data"
        )

    yield {
        "fname": _fname,
        "ref": _ref,
        "data": _data,
    }


@pytest.fixture
def hdf5_file(temp_path):
    """Create a temporary HDF5 file for tests."""
    if not (temp_path / "hdf5_utils").is_dir():
        (temp_path / "hdf5_utils").mkdir()
    file = h5py.File(temp_path / "hdf5_utils" / "temp_file.h5", "w")
    yield file
    file.close()


@pytest.mark.parametrize("input_value", [123, 42.0, ["entry/data"]])
def test_split_hdf5_file_and_dataset_names__wrong_type(input_value):
    with pytest.raises(TypeError):
        _split_hdf5_file_and_dataset_names(input_value, "test/dset")


@pytest.mark.parametrize("fname", ["/test/testfile.h5", Path("test/testfile.h5")])
def test_split_hdf5_file_and_dataset_names__w_two_entries(fname):
    _dset = "/test/dset"
    _new_name, _new_dset = _split_hdf5_file_and_dataset_names(fname, _dset)
    assert str(fname) == _new_name
    assert _dset == _new_dset


def test_split_hdf5_file_and_dataset_names__joint_file_and_dset():
    _name = "/test/path/testfile.h5"
    _dset = "/test/dset"
    _option = f"{_name}://{_dset}"
    _new_name, _new_dset = _split_hdf5_file_and_dataset_names(_option)
    assert _name == _new_name
    assert _dset == _new_dset


def test_split_hdf5_file_and_dataset_names__only_fname():
    _name = "c:/test/path/testfile.h5"
    with pytest.raises(KeyError):
        _split_hdf5_file_and_dataset_names(_name)


@pytest.mark.parametrize("input_value", [123, 42.0, Path("entry/data")])
def test_get_hdf5_metadata_meta__wrong_type(hdf5_test_data, input_value):
    with pytest.raises(TypeError):
        get_hdf5_metadata(hdf5_test_data["ref"], input_value)


def test_get_hdf5_metadata_meta__other_str(hdf5_test_data):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], "nokey")
    assert _res == dict()


@pytest.mark.parametrize("meta_item", ["dtype", "shape", "size", "ndim", "nbytes"])
def test_get_hdf5_metadata_meta__single_item(hdf5_test_data, meta_item):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], meta_item)
    assert _res == getattr(hdf5_test_data["data"], meta_item)


def test_get_hdf5_metadata_meta__no_such_dset(hdf5_test_data):
    with pytest.raises(FileReadError):
        get_hdf5_metadata(hdf5_test_data["ref"] + "/more", "dtype")


@pytest.mark.parametrize(
    "meta_item", [("ndim", "size"), "ndim, size", ["size", "ndim"]]
)
def test_get_hdf5_metadata_meta__multiples(hdf5_test_data, meta_item):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], meta_item)
    assert set(_res.keys()) == {"ndim", "size"}
    assert _res["ndim"] == hdf5_test_data["data"].ndim
    assert _res["size"] == hdf5_test_data["data"].size


def test_hdf5_dataset_filter_check__no_dset():
    assert not hdf5_dataset_filter_check("something")


def test_hdf5_dataset_filter_check__simple(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](2), "w") as _file:
        _file.create_group("test")
        _file["test"].create_dataset("data", data=hdf5_test_data["data"])
        assert hdf5_dataset_filter_check(_file["test/data"])


def test_hdf5_dataset_filter_check__dim(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](2), "w") as _file:
        _file.create_group("test")
        _file["test"].create_dataset("data", data=hdf5_test_data["data"])
        assert not hdf5_dataset_filter_check(_file["test/data"], min_dim=5)


def test_hdf5_dataset_filter_check__size(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](2), "w") as _file:
        _file.create_group("test")
        _file["test"].create_dataset("data", data=hdf5_test_data["data"])
        assert not hdf5_dataset_filter_check(_file["test/data"], min_size=50000)


def test_hdf5_dataset_filter_check__ignore_keys(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](2), "w") as _file:
        _file.create_group("test")
        _file["test"].create_dataset("data", data=hdf5_test_data["data"])
        assert not hdf5_dataset_filter_check(
            _file["test/data"], ignore_keys=("test/data")
        )


def test_get_hdf5_populated_dataset__unknown_extension(hdf5_test_data):
    with pytest.raises(FileReadError):
        get_hdf5_populated_dataset_keys(str(hdf5_test_data["fname"](1)) + ".other")


def test_get_hdf5_populated_dataset__wrong_input_datatype():
    _res = get_hdf5_populated_dataset_keys([1, 2, 3])
    assert _res == []


def test_get_hdf5_populated_dataset_keys__w_str(hdf5_test_data):
    _res = get_hdf5_populated_dataset_keys(hdf5_test_data["fname"](1))
    assert set(_res) == _ALL_DSETS


def test_get_hdf5_populated_dataset_keys__w_Path(hdf5_test_data):
    _res = get_hdf5_populated_dataset_keys(Path(hdf5_test_data["fname"](1)))
    assert set(_res) == _ALL_DSETS


def test_get_hdf5_populated_dataset_keys__min_dim(hdf5_test_data):
    _res = get_hdf5_populated_dataset_keys(Path(hdf5_test_data["fname"](1)), min_dim=3)
    assert set(_res) == set(_4d_DSETS + _3d_DSETS)


def test_get_hdf5_populated_dataset_keys__w_h5py_file(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](1), "r") as _file:
        _res = get_hdf5_populated_dataset_keys(_file)
    assert set(_res) == _ALL_DSETS


def test_get_hdf5_populated_dataset_keys__w_h5py_dset(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"](1), "r") as _file:
        _res = get_hdf5_populated_dataset_keys(_file["test"])
    assert set(_res) == set(k for k in _ALL_DSETS if k.startswith("/test/"))


def test_get_hdf5_populated_dataset_keys_smaller_dim(hdf5_test_data):
    _res = get_hdf5_populated_dataset_keys(hdf5_test_data["fname"](1), min_dim=1)
    assert set(_res) == _ALL_DSETS | set(_1d_DSETS)


@pytest.mark.parametrize("min_size", [5, 50, 500, 5000, 50000])
def test_get_hdf5_populated_dataset_keys__test_sizes(hdf5_test_data, min_size):
    _res = get_hdf5_populated_dataset_keys(
        hdf5_test_data["fname"](1), min_dim=1, min_size=min_size
    )
    _reference = set()
    if min_size <= 10000:
        _reference = _reference | set(_4d_DSETS)
    if min_size <= 1000:
        _reference = _reference | set(_3d_DSETS)
    if min_size <= 100:
        _reference = _reference | set(_2d_DSETS)
    if min_size <= 10:
        _reference = _reference | set(_1d_DSETS)
    assert set(_res) == _reference


def test_convert_data_for_writing_to_hdf5_dataset__None():
    _data = convert_data_for_writing_to_hdf5_dataset(None)
    assert _data == "::None::"
    assert isinstance(_data, str)


def test_convert_data_for_writing_to_hdf5_dataset__data():
    _input = np.random.random((12, 12))
    _data = convert_data_for_writing_to_hdf5_dataset(_input)
    assert np.allclose(_data, _input)
    assert isinstance(_data, np.ndarray)


def test_read_and_decode_hdf5_dataset__string(hdf5_test_data):
    _input = get_random_string(30)
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset)
    assert isinstance(_out, str)
    assert _out == _input


def test_read_and_decode_hdf5_dataset__group_not_None(hdf5_test_data):
    _input = get_random_string(30)
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset, group="test")
    assert isinstance(_out, str)
    assert _out == _input


def test_read_and_decode_hdf5_dataset__dataset_not_None(hdf5_test_data):
    _input = get_random_string(30)
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset, dataset="Test")
    assert isinstance(_out, str)
    assert _out == _input


def test_read_and_decode_hdf5_dataset__dataset_and_group_not_None(hdf5_test_data):
    _input = get_random_string(30)
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_file, "entry", "test")
    assert isinstance(_out, str)
    assert _out == _input


def test_read_and_decode_hdf5_dataset__None(hdf5_test_data):
    _input = "::None::"
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset)
    assert _out is None


def test_read_and_decode_hdf5_dataset__ndarray(hdf5_test_data):
    _input = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset)
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input)


def test_read_and_decode_hdf5_dataset__ndarray_without_return_dataset(hdf5_test_data):
    _input = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset, return_dataset=False)
    assert isinstance(_out, np.ndarray)
    assert not isinstance(_out, Dataset)
    assert np.allclose(_out, _input)


def test_read_and_decode_hdf5_dataset__list(hdf5_test_data):
    _input = [1, 2, 3]
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset)
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input)


def test_read_and_decode_hdf5_dataset__float(hdf5_test_data):
    _input = 12.4
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _group = _file.create_group("entry")
        _dset = _group.create_dataset("test", data=_input)
        _out = read_and_decode_hdf5_dataset(_dset)
    assert isinstance(_out, Real)
    assert _input == _out


def test_create_hdf5_dataset__w_data(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, data=_input)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input)


def test_create_hdf5_dataset__w_shape(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, shape=_input.shape)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert isinstance(_out, Dataset)
    assert _input.shape == _out.shape


def test_create_hdf5_dataset__w_None(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = None
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, data=_input)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert _out is None


def test_create_hdf5_dataset__w_str(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = get_random_string(20)
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, data=_input)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert _input == _out


def test_create_hdf5_dataset__w_int(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = 42
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, data=_input)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert _input == _out


def test_create_hdf5_dataset__existing_dataset(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = 42
    _input_new = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        create_hdf5_dataset(_file, _group, _dname, data=_input)
        create_hdf5_dataset(_file, _group, _dname, data=_input_new)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input_new)


def test_create_hdf5_dataset__no_group(hdf5_test_data):
    _group = "entry/test"
    _dname = "test_dataset"
    _input = np.random.random((30, 30))
    with h5py.File(hdf5_test_data["fname"]("dummy"), "w") as _file:
        _file.create_group(_group)
        create_hdf5_dataset(_file[_group], None, _dname, data=_input)
        _out = read_and_decode_hdf5_dataset(_file[_group + "/" + _dname])
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input)


def test_create_nx_entry_groups__basic(hdf5_file):
    group_name = "entry/test"
    group_type = "NXdata"
    attributes = {"attr1": "value1", "attr2": "value2"}
    group = create_nx_entry_groups(hdf5_file, group_name, group_type, **attributes)
    assert group_name in hdf5_file
    assert group.attrs["NX_class"] == group_type
    for key, value in attributes.items():
        assert group.attrs[key] == value


def test_create_nx_entry_groups__nested(hdf5_file):
    group_name = "entry/test/nested"
    group_type = "NXentry"
    attributes = {"attr1": "value1"}
    group = create_nx_entry_groups(hdf5_file, group_name, group_type, **attributes)
    assert group_name in hdf5_file
    assert group.attrs["NX_class"] == group_type
    for key, value in attributes.items():
        assert group.attrs[key] == value


def test_create_nx_entry_groups__no_attributes(hdf5_file):
    group_name = "entry/test"
    group_type = "NXdata"
    group = create_nx_entry_groups(hdf5_file, group_name, group_type)
    assert group_name in hdf5_file
    assert group.attrs["NX_class"] == group_type


def test_create_nx_entry_groups__w_existing_group(hdf5_file):
    group_name = "entry/test/group/name"
    group_type = "NXentry"
    group = create_nx_entry_groups(hdf5_file, group_name, group_type)
    group2 = create_nx_entry_groups(hdf5_file, group_name, group_type)
    assert group == group2


def test_create_nx_entry_groups__w_nxclass(hdf5_file):
    _cases = [
        ["entry", "NXtest"],
        ["entry/data", "NXdata"],
        ["entry/instrument", "NXinstrument"],
    ]

    for _key, _group in _cases:
        _ = create_nx_entry_groups(hdf5_file, _key, group_type=_group)
    for _key, _group in _cases:
        assert hdf5_file[_key].attrs["NX_class"] == _group


def test_create_nx_entry_groups__w_existing_group_different_type(hdf5_file):
    group_name = "entry/test/group/name"
    group_type = "NXentry"
    _ = create_nx_entry_groups(hdf5_file, group_name, group_type)
    with pytest.raises(ValueError):
        create_nx_entry_groups(hdf5_file, group_name, "AnotherEntry")


def test_create_nxdata_entry__basic(hdf5_file):
    name = "entry/test"
    data = np.random.random((10, 10))
    attributes = {"attr1": "value1", "attr2": "value2"}
    group = create_nxdata_entry(hdf5_file, name, data, **attributes)
    assert name in hdf5_file
    assert group.attrs["NX_class"] == "NXdata"
    for key, value in attributes.items():
        assert group.attrs[key] == value


def test_create_nxdata_entry__w_axes(hdf5_file):
    name = "entry/test"
    data = Dataset(
        np.random.random((10, 10)),
        axis_labels=["x", "y"],
        axis_units=["m", "s"],
        axis_ranges=[np.arange(10), np.arange(10)],
    )
    attributes = {"attr1": "value1"}
    group = create_nxdata_entry(hdf5_file, name, data, **attributes)
    assert name in hdf5_file
    assert group.attrs["NX_class"] == "NXdata"
    for key, value in attributes.items():
        assert group.attrs[key] == value
    for dim in range(data.ndim):
        assert f"axis_{dim}" in group
        assert np.allclose(group[f"axis_{dim}"][()], data.axis_ranges[dim])
        _ax = group[f"axis_{dim}"]
        assert _ax.attrs["long_name"] == data.axis_labels[dim]
        assert _ax.attrs["units"] == data.axis_units[dim]
        assert np.allclose(_ax[()], data.axis_ranges[dim])


def test_create_nx_dataset__basic(hdf5_file):
    group = hdf5_file.create_group("entry")
    name = "test_dataset"
    test_data = [np.random.random((10, 10)), "a test string", 1, 12.2]
    for data in test_data:
        if name in group:
            del group[name]
        dataset = create_nx_dataset(group, name, data)
        assert name in group
        if isinstance(data, str):
            assert dataset[()].decode() == data
        else:
            assert np.array_equal(dataset[()], data)


def test_create_nx_dataset__w_dict(hdf5_file):
    group = hdf5_file.create_group("entry")
    name = "test_dataset"
    attrs = {"attr1": "value1", "attr2": "value2"}
    test_data = [
        {"data": np.random.random((10, 10))},
        {"shape": (10, 10)},
    ]
    for data in test_data:
        if name in group:
            del group[name]
        dataset = create_nx_dataset(group, name, data, **attrs)
        assert name in group
        assert np.array_equal(dataset[()].shape, (10, 10))
        for key, value in attrs.items():
            assert dataset.attrs[key] == value


def test_create_nx_dataset__w_attributes(hdf5_file):
    group = hdf5_file.create_group("entry")
    name = "test_dataset"
    data = np.random.random((10, 10))
    attributes = {"units": "meters", "long_name": "Test Dataset"}
    dataset = create_nx_dataset(group, name, data, **attributes)
    assert name in group
    assert np.array_equal(dataset[()], data)
    for key, value in attributes.items():
        assert dataset.attrs[key] == value
