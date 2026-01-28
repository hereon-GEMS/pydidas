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

import os
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pytest

from pydidas.core import Dataset, FileReadError, UserConfigError
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
    verify_hdf5_dset_exists_in_file,
)


_1d_DSETS = ["/test/data1d", "/test/1d/data"]
_2d_DSETS = ["/test/path/data2d", "/test/other_2d/data"]
_3d_DSETS = ["/3d/data/data", "/data/3d/data"]
_4d_DSETS = ["/test/path/4ddata", "/entry/path/to_4d/data", "/test/ext_data/data"]
# _ALL_DSETS does not include the 1d datasets as the default dim filter is 2
_ALL_DSETS = set(_2d_DSETS + _3d_DSETS + _4d_DSETS)
_DSETS_OF_MIN_DIM = {
    1: set(_1d_DSETS + _2d_DSETS + _3d_DSETS + _4d_DSETS),
    2: set(_2d_DSETS + _3d_DSETS + _4d_DSETS),
    3: set(_3d_DSETS + _4d_DSETS),
    4: set(_4d_DSETS),
    5: set(),
}


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
        "fname": _fname(1),
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


@pytest.mark.parametrize(
    "fname, dset",
    [
        ("test/testfile.h5", "/test/dset"),
        (Path("test/testfile.h5"), "/test/dset"),
        ("test/testfile.h5:///test/dset", None),
    ],
)
def test_split_hdf5_file_and_dataset_names__w_dset_arg(fname, dset):
    _new_name, _new_dset = _split_hdf5_file_and_dataset_names(fname, dset)
    assert Path(_new_name) == Path("test/testfile.h5")
    assert _new_dset == "/test/dset"


def test_split_hdf5_file_and_dataset_names__only_fname():
    with pytest.raises(KeyError):
        _split_hdf5_file_and_dataset_names("/test/path/testfile.h5", None)


@pytest.mark.parametrize("meta_item", ["dtype", "shape", "size", "ndim", "nbytes"])
def test_get_hdf5_metadata_meta__single_item(hdf5_test_data, meta_item):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], meta_item)
    assert _res == getattr(hdf5_test_data["data"], meta_item)


@pytest.mark.parametrize(
    "meta_item", [("ndim", "size"), "ndim, size", ["size", "ndim"]]
)
def test_get_hdf5_metadata_meta__multiples(hdf5_test_data, meta_item):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], meta_item)
    assert set(_res.keys()) == {"ndim", "size"}
    assert _res["ndim"] == hdf5_test_data["data"].ndim
    assert _res["size"] == hdf5_test_data["data"].size


@pytest.mark.parametrize("input_value", [123, 42.0, Path("entry/data")])
def test_get_hdf5_metadata_meta__wrong_type(hdf5_test_data, input_value):
    with pytest.raises(TypeError):
        get_hdf5_metadata(hdf5_test_data["ref"], input_value)


def test_get_hdf5_metadata_meta__other_str(hdf5_test_data):
    _res = get_hdf5_metadata(hdf5_test_data["ref"], "nokey")
    assert _res == dict()


def test_get_hdf5_metadata_meta__no_such_dset(hdf5_test_data):
    with pytest.raises(FileReadError):
        get_hdf5_metadata(hdf5_test_data["ref"] + "/more", "dtype")


def test_hdf5_dataset_filter_check__no_dset():
    assert not hdf5_dataset_filter_check("something")


@pytest.mark.parametrize("min_dim", [1, 2, 3, 4, 5])
def test_hdf5_dataset_filter_check__dim(hdf5_test_data, min_dim):
    with h5py.File(hdf5_test_data["fname"], "r") as _file:
        assert hdf5_dataset_filter_check(_file[_4d_DSETS[0]], min_dim=min_dim) == (
            min_dim <= 4
        )


def test_hdf5_dataset_filter_check__ignore_keys(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"], "r") as _file:
        assert "4ddata" in _file["/test/path/"].keys()
        assert not hdf5_dataset_filter_check(
            _file["/test/path/4ddata"], ignore_keys=("test/path")
        )


def test_get_hdf5_populated_dataset__unknown_extension(hdf5_test_data):
    with pytest.raises(FileReadError):
        get_hdf5_populated_dataset_keys(str(hdf5_test_data["fname"]) + ".other")


def test_get_hdf5_populated_dataset__wrong_input_datatype():
    _res = get_hdf5_populated_dataset_keys([1, 2, 3])
    assert _res == []


@pytest.mark.parametrize("as_type", [str, Path, h5py.File])
def test_get_hdf5_populated_dataset_keys(hdf5_test_data, as_type):
    if as_type == h5py.File:
        with h5py.File(hdf5_test_data["fname"], "r") as _file:
            _res = get_hdf5_populated_dataset_keys(_file)
    else:
        _res = get_hdf5_populated_dataset_keys(as_type(hdf5_test_data["fname"]))
    assert set(_res) == _ALL_DSETS


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_get_hdf5_populated_dataset_keys__min_dim(hdf5_test_data, n):
    _res = get_hdf5_populated_dataset_keys(Path(hdf5_test_data["fname"]), min_dim=n)
    assert set(_res) == _DSETS_OF_MIN_DIM[n]


def test_get_hdf5_populated_dataset_keys__w_h5py_dset(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"], "r") as _file:
        _res = get_hdf5_populated_dataset_keys(_file["test"])
    assert set(_res) == set(k for k in _ALL_DSETS if k.startswith("/test/"))


@pytest.mark.parametrize("min_size", [5, 50, 500, 5000, 50000])
def test_get_hdf5_populated_dataset_keys__test_sizes(hdf5_test_data, min_size):
    _res = get_hdf5_populated_dataset_keys(
        hdf5_test_data["fname"], min_dim=1, min_size=min_size
    )
    _reference = _DSETS_OF_MIN_DIM[int(np.log10(min_size).__ceil__())]
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


@pytest.mark.parametrize(
    "data, expected",
    [
        ["Spam, Ham & Eggs"] * 2,
        ["::None::", None],
        [42, 42],
        [[1, 2, 3], np.asarray([1, 2, 3])],
        [np.random.random((30, 30))] * 2,
        [3.14, 3.14],
    ],
)
@pytest.mark.parametrize("return_dataset", [True, False])
def test_read_and_decode_hdf5_dataset(hdf5_file, data, expected, return_dataset):
    _group = hdf5_file.create_group("entry")
    _dset = _group.create_dataset("test", data=data)
    _out = read_and_decode_hdf5_dataset(_dset, return_dataset=return_dataset)
    assert isinstance(_out, type(expected))
    if isinstance(_out, np.ndarray):
        assert np.allclose(_out, expected)
        assert isinstance(_out, Dataset) == return_dataset
    else:
        assert _out == expected


@pytest.mark.parametrize("group", ["entry", None])
@pytest.mark.parametrize("dataset", ["test", None])
def test_read_and_decode_hdf5_dataset__group_and_dataset(hdf5_file, group, dataset):
    _input = get_random_string(30)
    _group = hdf5_file.create_group("entry")
    _dset = _group.create_dataset("test", data=_input)
    if None in (group, dataset):
        with pytest.raises(UserConfigError):
            read_and_decode_hdf5_dataset(hdf5_file, group=group, dataset=dataset)
        _out = read_and_decode_hdf5_dataset(_dset, group=group, dataset=dataset)
    else:
        _out = read_and_decode_hdf5_dataset(hdf5_file, group=group, dataset=dataset)
    assert isinstance(_out, str)
    assert _out == _input


@pytest.mark.parametrize(
    "dset_kws",
    [
        {"data": np.random.random((10, 10))},
        {"shape": (10, 10)},
        {"data": None},
        {"data": 42},
        {"data": "A test string"},
    ],
)
def test_create_hdf5_dataset__w_data(hdf5_file, dset_kws):
    _group = "entry/test"
    _dset = "test_dataset"
    create_hdf5_dataset(hdf5_file, _dset, group=_group, **dset_kws)
    _out = read_and_decode_hdf5_dataset(hdf5_file[_group + "/" + _dset])
    if dset_kws.get("data") is not None and isinstance(dset_kws["data"], np.ndarray):
        assert isinstance(_out, Dataset)
        assert np.allclose(_out, dset_kws["data"])
    elif dset_kws.get("data") is not None:
        assert _out == dset_kws["data"]
    if dset_kws.get("shape") is not None:
        assert _out.shape == dset_kws["shape"]
    if dset_kws.get("data", "default") is None:
        assert _out is None


def test_create_hdf5_dataset__existing_dataset(hdf5_file):
    _group = "entry/test"
    _dset = "test_dataset"
    _input = 42
    _input_new = np.random.random((30, 30))
    create_hdf5_dataset(hdf5_file, _dset, group=_group, data=_input)
    create_hdf5_dataset(hdf5_file, _dset, group=_group, data=_input_new)
    _out = read_and_decode_hdf5_dataset(hdf5_file[_group + "/" + _dset])
    assert isinstance(_out, Dataset)
    assert np.allclose(_out, _input_new)


def test_create_hdf5_dataset__no_group(hdf5_file):
    _group = "entry/test"
    _dset = "test_dataset"
    _input = np.random.random((30, 30))
    hdf5_file.create_group(_group)
    create_hdf5_dataset(hdf5_file[_group], _dset, data=_input)
    _out = read_and_decode_hdf5_dataset(hdf5_file[_group + "/" + _dset])
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


def test_verify_hdf5_dset_exists_in_file(hdf5_test_data):
    verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], _3d_DSETS[0])


def test_verify_hdf5_dset_exists_in_file__group_not_dset(hdf5_test_data):
    _dset = os.path.dirname(_3d_DSETS[0])
    with pytest.raises(UserConfigError):
        verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], _dset)


def test_verify_hdf5_dset_exists_in_file__wrong_key(hdf5_test_data):
    with pytest.raises(UserConfigError):
        verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], "no/dataset")


if __name__ == "__main__":
    pytest.main([__file__])
