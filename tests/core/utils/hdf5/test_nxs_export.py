# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import h5py
import numpy as np
import pytest

from pydidas.core import Dataset
from pydidas.core.utils.hdf5 import (
    create_nx_dataset,
    create_nx_entry_groups,
    create_nxdata_entry,
)
from pydidas.core.utils.hdf5.nxs_export import _get_nx_class_for_ndarray


@pytest.fixture
def hdf5_file(temp_path):
    """Create a temporary HDF5 file for tests."""
    if not (temp_path / "hdf5_utils").is_dir():
        (temp_path / "hdf5_utils").mkdir()
    file = h5py.File(temp_path / "hdf5_utils" / "temp_file.h5", "w")
    yield file
    file.close()


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


@pytest.mark.parametrize(
    "arr, expected_val",
    [
        (np.array([1, 2, 3]), "NX_INT"),
        (Dataset([1, 2, 3]), "NX_INT"),
        (np.ones(10, dtype=np.uint8), "NX_INT"),
        (np.array([1.0, 2.0, 3.0]), "NX_FLOAT"),
        (Dataset([1.0, 2.0, 3.0]), "NX_FLOAT"),
        (np.ones(10, dtype=np.float32), "NX_FLOAT"),
        (np.asarray([[0], [1]], dtype=object), "NX_CHAR"),
    ],
)
def test_get_nx_class_for_ndarray(arr, expected_val):
    assert _get_nx_class_for_ndarray(arr) == expected_val


if __name__ == "__main__":
    pytest.main([__file__])
