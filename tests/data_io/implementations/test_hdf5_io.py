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


import h5py
import numpy as np
import pytest

from pydidas.core import Dataset, FileReadError, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import create_nxdata_entry
from pydidas.data_io.implementations.hdf5_io import Hdf5Io


@pytest.fixture()
def config(temp_path):
    fname = temp_path / "test.h5"
    data_shape = (12, 13, 14, 15)
    data_slice = (
        slice(None),
        slice(None),
        slice(None),
        slice(0, 4),
    )
    data = Dataset(
        np.random.random(data_shape),
        axis_labels=["x", "y", "z", "chi"],
        axis_units=["x_unit", "unit4y", "z unit", "deg"],
        axis_ranges=[
            5 * np.arange(data_shape[0]) + 42,
            0.3 * np.arange(data_shape[1]) - 5,
            4 * np.arange(data_shape[2]),
            -42 * np.arange(data_shape[3]) + 127,
        ],
        data_label="test data",
        data_unit="hbar / lightyear",
    )
    with h5py.File(fname, "w") as _file:
        _file["data"] = np.arange(10)
        for _path in ["test/path/res", "entry/data/data"]:
            _local_data = data if _path == "test/path/res" else data[data_slice]
            create_nxdata_entry(_file, _path, _local_data)
    yield {
        "path": temp_path,
        "fname": fname,
        "data": data,
        "data_shape": data_shape,
        "data_slice": data_slice,
    }


def test_class_attributes():
    assert Hdf5Io.extensions_import == HDF5_EXTENSIONS
    assert Hdf5Io.extensions_export == HDF5_EXTENSIONS
    assert Hdf5Io.format_name == "Hdf5"
    for _dim in [1, 2, 3, 4, 5, 6]:
        assert _dim in Hdf5Io.dimensions


def test_import_from_file__no_metadata(config):
    _data = Hdf5Io.import_from_file(config["fname"], import_metadata=False)
    assert np.allclose(_data, config["data"][config["data_slice"]])
    assert _data.data_label == ""
    assert _data.data_unit == ""
    assert "indices" in _data.metadata
    assert "dataset" in _data.metadata


def test_import_from_file__w_metadata(config):
    _data = Hdf5Io.import_from_file(config["fname"])
    _ref_data = config["data"][config["data_slice"]]
    assert np.allclose(_data, _ref_data)
    for _ax in range(_data.ndim):
        for _key in ["axis_labels", "axis_units"]:
            assert getattr(_data, _key)[_ax] == getattr(_ref_data, _key)[_ax]
        assert np.allclose(_data.axis_ranges[_ax], _ref_data.axis_ranges[_ax])
    assert _data.data_label == config["data"].data_label
    assert _data.data_unit == config["data"].data_unit


def test_import_from_file__w_metadata__from_axis_1(config):
    _data = Hdf5Io.import_from_file(config["fname"], dataset="entry/data/axis_1")
    _ref_data = config["data"][config["data_slice"]].axis_ranges[1]
    assert np.allclose(_data, _ref_data)
    assert _data.axis_labels == {0: ""}
    assert _data.axis_units == {0: ""}
    assert np.all(_data.axis_ranges[0] == np.arange(_data.size))
    assert _data.data_label == config["data"].axis_labels[1]
    assert _data.data_unit == config["data"].axis_units[1]


def test_import_from_file__w_metadata_from_root(config):
    _data = Hdf5Io.import_from_file(
        config["fname"], dataset="data", import_metadata=True
    )
    assert "indices" in _data.metadata
    assert "dataset" in _data.metadata
    assert _data.data_label == ""
    assert _data.data_unit == ""
    assert np.allclose(_data, np.arange(10))


def test_import_from_file__wrong_name(temp_path):
    with pytest.raises(FileReadError):
        Hdf5Io.import_from_file(temp_path / "dummy_hdf5_name.h5")


def test_import_from_file__wrong_filetype(config):
    _fname_new = config["path"] / "test2.dat"
    with open(_fname_new, "w") as f:
        f.write("now it's just an ASCII text file.")
    with pytest.raises(FileReadError):
        Hdf5Io.import_from_file(_fname_new)


@pytest.mark.parametrize(
    "indices", [((7, 8),), 7, [7], (7,), slice(7, 8), (slice(7, 8),)]
)
def test_import_from_file__w_single_index(config, indices):
    _data = Hdf5Io.import_from_file(
        config["fname"], indices=indices, import_metadata=False
    )
    assert np.allclose(_data, config["data"][(7, *config["data_slice"][1:])])


@pytest.mark.parametrize("indices", [None, (None,), slice(None), (slice(None),)])
def test_import_from_file__w_none_indices(config, indices):
    _data = Hdf5Io.import_from_file(
        config["fname"], indices=indices, import_metadata=False
    )
    assert np.allclose(_data, config["data"][*config["data_slice"]])


def test_import_from_file__w_dset_kw(config):
    with pytest.warns():
        _data = Hdf5Io.import_from_file(
            config["fname"], import_metadata=False, dset="test/path/res"
        )
    assert np.allclose(_data, config["data"])


@pytest.mark.parametrize("_slice", [(25,), (None, 27), (26, 65)])
def test_import_from_file__zeros_dim_results(config, _slice):
    with pytest.raises(UserConfigError):
        Hdf5Io.import_from_file(config["fname"], indices=_slice)


@pytest.mark.parametrize(
    "indices, slicing",
    [
        ((1, 3), (slice(1, 2), slice(3, 4))),
        ((5, None, 3), (slice(5, 6), slice(None), slice(3, 4))),
        (((5, None), None, (None, 3)), (slice(5, None), slice(None), slice(0, 3))),
    ],
)
@pytest.mark.parametrize("squeeze", [True, False])
def test_import_from_file__complex_indexing(config, indices, slicing, squeeze):
    _data = Hdf5Io.import_from_file(
        config["fname"], indices=indices, import_metadata=False, auto_squeeze=squeeze
    )
    _ref = config["data"][config["data_slice"]][slicing]
    if squeeze:
        _ref = _ref.squeeze()
    assert np.allclose(_data, _ref)


def test_import_from_file__w_dataset(config):
    _data = Hdf5Io.import_from_file(
        config["fname"], dataset="test/path/res", import_metadata=False
    )
    assert np.allclose(_data, config["data"])


def test_import_from_file__w_dataset_and_indices(config):
    _data = Hdf5Io.import_from_file(
        config["fname"],
        dataset="test/path/res",
        import_metadata=True,
        indices=(1, 4),
    )
    _ref_data = config["data"][1, 4]
    assert np.allclose(_data, _ref_data)
    assert _data.data_label == _ref_data.data_label
    assert _data.data_unit == _ref_data.data_unit
    for _dim in range(_data.ndim):
        assert _data.axis_labels[_dim] == _ref_data.axis_labels[_dim]
        assert _data.axis_units[_dim] == _ref_data.axis_units[_dim]
        assert np.allclose(_data.axis_ranges[_dim], _ref_data.axis_ranges[_dim])


def test_import_from_file__w_unit_in_label_metadata(config):
    _ref = config["data"].copy()
    _ref.update_axis_label(0, f"{_ref.axis_labels[0]} / {_ref.axis_units[0]}")
    Hdf5Io.export_to_file(config["path"] / "test_unit_label.h5", _ref)
    _data = Hdf5Io.import_from_file(
        config["path"] / "test_unit_label.h5", import_metadata=True
    )
    assert np.allclose(_data, _ref)
    assert _data.axis_labels[0] == config["data"].axis_labels[0]


def test_import_from_file__missing_keys(config):
    Hdf5Io.export_to_file(config["path"] / "w_missing_key.h5", config["data"])
    with h5py.File(config["path"] / "w_missing_key.h5", "r+") as _file:
        del _file["entry/data/axis_0"]
    with pytest.raises(FileReadError):
        Hdf5Io.import_from_file(
            config["path"] / "w_missing_key.h5", import_metadata=True
        )


def test_import_from_file__group_instead_of_dataset(config):
    Hdf5Io.export_to_file(config["path"] / "w_group_not_dataset.h5", config["data"])
    with h5py.File(config["path"] / "w_group_not_dataset.h5", "r+") as _file:
        del _file["entry/data/axis_0"]
        _file["entry/data"].create_group("axis_0")
    _data = Hdf5Io.import_from_file(
        config["path"] / "w_group_not_dataset.h5", import_metadata=True
    )
    assert _data.axis_labels == {
        _i: ("" if _i == 0 else _v) for _i, _v in config["data"].axis_labels.items()
    }
    assert _data.axis_units == {
        _i: ("" if _i == 0 else _v) for _i, _v in config["data"].axis_units.items()
    }


@pytest.mark.parametrize("dataset", ["entry/data/data", "entry/data/axis_1_repr"])
def test_import_from_file__w_legacy_data(config, dataset):
    _ref = config["data"].copy()
    Hdf5Io.export_to_file(config["path"] / "w_legacy_data.h5", _ref, overwrite=True)
    with h5py.File(config["path"] / "w_legacy_data.h5", "r+") as _file:
        for _i in range(_ref.ndim):
            _file.move(
                f"entry/data/axis_{_i}",
                f"entry/data/axis_{_i}_repr",
            )
            # _file["entry/data"].attrs["axes"] = [
            #     f"axis_{_i}_repr" for _i in range(_ref.ndim)
            # ]
            _file["entry/data/"].create_group(f"axis_{_i}")
            _file[f"entry/data/axis_{_i}"].create_dataset(
                "range", data=_ref.axis_ranges[_i]
            )
            _file[f"entry/data/axis_{_i}"].create_dataset(
                "label", data=_ref.axis_labels[_i]
            )
            _file[f"entry/data/axis_{_i}"].create_dataset(
                "unit", data=_ref.axis_units[_i]
            )
        # deliberately remove a label
        del _file["entry/data/axis_0/label"]
    _data = Hdf5Io.import_from_file(
        config["path"] / "w_legacy_data.h5", import_metadata=True, dataset=dataset
    )
    _data_ref = _ref if dataset == "entry/data/data" else _ref.axis_ranges[1]
    assert np.allclose(_data, _data_ref)
    if dataset == "entry/data/data":
        for _i in range(_data_ref.ndim):
            assert np.allclose(_data.axis_ranges[_i], _ref.axis_ranges[_i])
            assert _data.axis_units[_i] == _ref.axis_units[_i]
            assert _data.axis_labels[_i] == ("" if _i == 0 else _ref.axis_labels[_i])
    elif dataset == "entry/data/axis_1":
        assert _data.data_label == _ref.axis_labels[1]
        assert _data.data_unit == _ref.axis_units[1]
        assert _data.axis_labels == {0: ""}
        assert _data.axis_units == {0: ""}
        assert np.allclose(_data.axis_ranges[0], np.arange(_data.size))


def test_export_to_file__wrong_structure(config):
    with pytest.raises(UserConfigError):
        Hdf5Io.export_to_file(
            config["fname"], config["data"], dataset="data", overwrite=True
        )


def test_export_to_file__file_exists(config):
    with pytest.raises(FileExistsError):
        Hdf5Io.export_to_file(config["fname"], config["data"])


def test_export_to_file_file_exists_and_overwrite(config):
    _fname = config["path"].joinpath("test_new.h5")
    Hdf5Io.export_to_file(_fname, config["data"])
    Hdf5Io.export_to_file(_fname, config["data"][:11], overwrite=True)
    _data = Hdf5Io.import_from_file(_fname)
    assert _data.shape == (11,) + config["data_shape"][1:]


def test_export_to_file_w_groupname(config):
    _fname = config["path"].joinpath("test_gname.h5")
    Hdf5Io.export_to_file(_fname, config["data"], dataset="test/new/new_data")
    _data = Hdf5Io.import_from_file(
        _fname, dataset="test/new/new_data", slicing_axes=[]
    )
    assert _data.shape == config["data_shape"]
    assert np.allclose(_data, config["data"])


if __name__ == "__main__":
    pytest.main()
