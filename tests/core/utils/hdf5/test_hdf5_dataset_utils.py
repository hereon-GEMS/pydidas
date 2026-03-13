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
from pydidas.core.utils.hdf5 import (
    convert_data_for_writing_to_hdf5_dataset,
    create_hdf5_dataset,
    get_generic_dataset,
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
    read_and_decode_hdf5_dataset,
    verify_hdf5_dset_exists_in_file,
)
from pydidas.core.utils.hdf5.hdf5_dataset_utils import (
    _dataset_selection_valid_check,
    _split_hdf5_file_and_dataset_names,
)


_scalar_DSETS = ["/test/scalar/data", "/entry/scalar/data"]
_1d_DSETS = ["/test/data1d", "/test/1d/data"]
_2d_DSETS = ["/test/path/data2d", "/test/other_2d/data"]
_3d_DSETS = ["/3d/data/data", "/data/3d/data"]
_4d_DSETS = ["/test/path/4ddata", "/entry/path/to_4d/data", "/test/ext_data/data"]
_NXS_DSETS = {"/test/path/nxsdata": 2, "/nx_entry/data": 3, "/entry/nxs_data_4d": 4}
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
        for _dset in _scalar_DSETS:
            _file[_dset] = -1
        for _dset in _1d_DSETS:
            _file[_dset] = _data[0, 0, 0]
        for _dset in _2d_DSETS:
            _file[_dset] = _data[0, 0]
        for _dset in _3d_DSETS:
            _file[_dset] = _data[0]
        for _dset in _4d_DSETS:
            if _dset == "/test/ext_data/data":
                continue
            _file[_dset] = _data
        _file["test/ext_data/data"] = h5py.ExternalLink(
            _fname("data"), "/ext/path/data"
        )
    with h5py.File(_fname("nxs"), "w") as _file:
        for _dset, _ndim in _NXS_DSETS.items():
            _parent, _name = os.path.split(_dset)
            _file.create_group(_parent)
            _file[_parent].attrs["NX_class"] = "NXdata"
            _file[_parent].attrs["signal"] = _name
            _file[_parent].attrs["axes"] = ["ax0", "ax1", "ax2", "ax3"]
            for _i in range(_ndim):
                _file[_parent].attrs[f"ax{_i}_indices"] = _i
                _file[_parent].create_dataset(f"ax{_i}", data=np.ones(_data.shape[_i]))
            _file[_dset] = _data[(slice(0, 1),) * (4 - _ndim)].squeeze()
        _parent = _file.create_group("invalid/nxdata/signal")
        _parent.attrs["NX_class"] = "NXdata"
        _parent.attrs["signal"] = "random"
        _parent.attrs["axes"] = ["ax0", "ax1", "ax2", "ax3"]
        for _i in range(_ndim):
            _parent.attrs[f"ax{_i}_indices"] = _i
            _parent.create_dataset(f"ax{_i}", data=np.ones(_data.shape[_i]))
        _parent.create_dataset("other_signal", data=np.ones(_data.shape))

    yield {
        "fname": _fname(1),
        "nxs_fname": _fname("nxs"),
        "ref": _ref,
        "data": _data,
    }


@pytest.fixture(scope="module")
def hdf5_external_test_data(hdf5_test_data, temp_path):
    """Extend the test data with additional datasets for testing."""
    # Get the main filename
    _fname = temp_path / "hdf5_utils" / "large_file_test.h5"
    _ext_fname = _fname.parent / "test_external_data.h5"
    _all_dsets = []

    # Create external data file with 5 datasets
    with h5py.File(_ext_fname, "w") as _ext_file:
        _group = _ext_file.create_group("ext_test")
        _group.create_dataset("ext_data_1d", data=np.random.random(10))
        _group.create_dataset("ext_data_2d", data=np.random.random((8, 8)))
        _group.create_dataset("ext_data_3d", data=np.random.random((5, 5, 5)))
        _group.create_dataset("ext_data_scalar", data=42.0)
        _group.create_dataset("ext_data_large", data=np.random.random((15, 15)))
        _group2 = _ext_file.create_group("ext/nested/group")
        _group2.create_dataset("nested_data", data=np.random.random((3, 3)))
        _group2.create_dataset("nested_data_2", data=np.random.random((4, 4)))

    with h5py.File(_fname, "w") as _file:
        for _i in range(2):
            for _j in range(2):
                _group_name = f"/root/stem_{_i}/branch_{_j}"
                _group = _file.create_group(_group_name)
                for _k in range(2):
                    _group.create_dataset(f"data_{_k}", data=np.ones((3, 2, 4)))
                    _all_dsets.append(f"{_group_name}/data_{_k}")

        # Add external links to the nested structure
        ext_links_group = _file.create_group("/external_links")
        ext_links_group["group"] = h5py.ExternalLink(
            _ext_fname.name, "/ext/nested/group"
        )
        _all_dsets.append("/external_links/group/nested_data")
        _all_dsets.append("/external_links/group/nested_data_2")
        for _key in ["1d", "2d", "3d", "scalar", "large"]:
            ext_links_group[f"link_to_{_key}"] = h5py.ExternalLink(
                _ext_fname.name, f"/ext_test/ext_data_{_key}"
            )
            _all_dsets.append(f"/external_links/link_to_{_key}")
    # Add external file path to test data
    hdf5_test_data["ext_ref_fname"] = _ext_fname
    hdf5_test_data["ext_fname"] = _fname
    hdf5_test_data["ext_all_dsets"] = set(_all_dsets)
    yield hdf5_test_data


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
    assert not _dataset_selection_valid_check("something")


@pytest.mark.parametrize("min_dim", [1, 2, 3, 4, 5])
def test_hdf5_dataset_filter_check__dim(hdf5_test_data, min_dim):
    with h5py.File(hdf5_test_data["fname"], "r") as _file:
        assert _dataset_selection_valid_check(
            _file[_4d_DSETS[0]], dict(min_dim=min_dim)
        ) == (min_dim <= 4)


def test_hdf5_dataset_filter_check__ignore_keys(hdf5_test_data):
    with h5py.File(hdf5_test_data["fname"], "r") as _file:
        assert "4ddata" in _file["/test/path/"].keys()
        assert not _dataset_selection_valid_check(
            _file["/test/path/4ddata"], dict(ignore_keys="/test/path")
        )


def test_get_hdf5_populated_dataset__w_external_link(hdf5_external_test_data):
    _res = get_hdf5_populated_dataset_keys(
        hdf5_external_test_data["ext_fname"], min_dim=0
    )
    assert set(_res) == hdf5_external_test_data["ext_all_dsets"]


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


@pytest.mark.parametrize("nxsignal_only", [True, False])
@pytest.mark.parametrize("min_dim", [1, 3])
def test_get_hdf5_populated_dataset_keys__nxsignal_only(
    hdf5_test_data, nxsignal_only, min_dim
):
    _res = get_hdf5_populated_dataset_keys(
        hdf5_test_data["nxs_fname"], nxdata_signal_only=nxsignal_only, min_dim=min_dim
    )
    _expected = set(k for k, v in _NXS_DSETS.items() if v >= min_dim)
    if nxsignal_only:
        assert set(_res) == _expected
    else:
        if min_dim <= 1:
            for _dset, _ndim in _NXS_DSETS.items():
                _parent = os.path.split(_dset)[0]
                _expected.update([f"{_parent}/ax{_i}" for _i in range(_ndim)])
            _expected.update([f"/invalid/nxdata/signal/ax{_i}" for _i in range(4)])
        _expected.add("/invalid/nxdata/signal/other_signal")
        assert set(_res) == set(_expected)


def test_get_hdf5_populated_dataset_keys__with_ignore_exception(hdf5_test_data):
    _res = get_hdf5_populated_dataset_keys(
        hdf5_test_data["fname"],
        ignore_keys=["/data/3d/"],
        ignore_key_exceptions=("/data/3d/data",),
    )
    assert "/data/3d/data" in _res


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


def test_verify_hdf5_dset_exists_in_file(hdf5_test_data):
    verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], _3d_DSETS[0])


def test_verify_hdf5_dset_exists_in_file__group_not_dset(hdf5_test_data):
    _dset = os.path.dirname(_3d_DSETS[0])
    with pytest.raises(UserConfigError):
        verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], _dset)


def test_verify_hdf5_dset_exists_in_file__wrong_key(hdf5_test_data):
    with pytest.raises(UserConfigError):
        verify_hdf5_dset_exists_in_file(hdf5_test_data["fname"], "no/dataset")


@pytest.mark.parametrize(
    "datasets, expected",
    [
        (  # NeXus standard path is returned:
            ["/entry/other/data", "/entry/data/data", "/something/else"],
            "/entry/data/data",
        ),
        (  # Eiger standard path is returned:
            ["/entry/other/data", "/entry/data/data_000001", "/something"],
            "/entry/data/data_000001",
        ),
        (  # LAMBDA detector standard path is returned:
            ["/entry/other/data", "/entry/instrument/detector/data"],
            "/entry/instrument/detector/data",
        ),
        # Priority order tests
        (  # NeXus path prioritized over Eiger path
            ["/entry/data/data", "/entry/data/data_000001"],
            "/entry/data/data",
        ),
        (  # Eiger path prioritized over LAMBDA path
            ["/entry/data/data_000001", "/entry/instrument/detector/data"],
            "/entry/data/data_000001",
        ),
        (  # LAMBDA path prioritized over arbitrary first item
            ["/some/random/data", "/entry/instrument/detector/data"],
            "/entry/instrument/detector/data",
        ),
        (  # NeXus prioritized with all standard paths present
            [
                "/entry/instrument/detector/data",
                "/entry/data/data_000001",
                "/entry/data/data",
                "/other/data",
            ],
            "/entry/data/data",
        ),
        # Fallback behavior
        (  # First item returned if no standard paths match
            ["/custom/data", "/other/path", "/third/item"],
            "/custom/data",
        ),
        (  # Single standard dataset
            ["/entry/data/data"],
            "/entry/data/data",
        ),
        (  # Single non-standard dataset
            ["/my/custom/dataset"],
            "/my/custom/dataset",
        ),
        # Case sensitivity
        (  # Path matching is case-sensitive (finds correct case)
            ["/Entry/Data/Data", "/entry/data/data"],
            "/entry/data/data",
        ),
        (  # Case mismatch doesn't match standard paths
            ["/Entry/Data/Data", "/other/path"],
            "/Entry/Data/Data",
        ),
        # Path matching precision
        (  # Trailing slashes don't match standards
            ["/entry/data/data/", "/other/data"],
            "/entry/data/data/",
        ),
        (  # Substrings of standard paths don't match
            ["/entry/data", "/other/data"],
            "/entry/data",
        ),
        (  # NeXus-like path with different entry name doesn't match
            ["/my_entry/data/data", "/other/path"],
            "/my_entry/data/data",
        ),
        # Special characters
        (  # Path separators must be exact (forward slashes)
            ["/entry\\data\\data", "/entry/data/data"],
            "/entry/data/data",
        ),
    ],
)
def test_get_generic_dataset(datasets, expected) -> None:
    """Test get_generic_dataset with various inputs and expected outputs."""
    result = get_generic_dataset(datasets)
    assert result == expected


@pytest.mark.parametrize(
    "datasets, expected",
    [
        (["/entry/data/data", "/other/path"], "/entry/data/data"),
        (("/entry/data/data", "/other/path"), "/entry/data/data"),
        ({"/entry/data/data", "/other/path"}, "/entry/data/data"),
    ],
)
def test_get_generic_dataset__input_types(datasets, expected) -> None:
    """Test get_generic_dataset with different input sequence types."""
    result = get_generic_dataset(datasets)
    assert result == expected


def test_get_generic_dataset__empty_list_raises_error() -> None:
    """Test that empty list raises ValueError."""
    with pytest.raises(ValueError):
        get_generic_dataset([])


if __name__ == "__main__":
    pytest.main([__file__])
