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


import time
from datetime import datetime
from unittest.mock import PropertyMock, patch

import h5py
import numpy as np
import pytest

from pydidas.core import Dataset, Parameter
from pydidas.core.exceptions import UserConfigError
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.utils.hdf5 import (
    nxs_create_recursive_groups,
    nxs_write_dataset,
    nxs_write_nxdata,
)
from pydidas.core.utils.hdf5.hdf5_dataset_utils import read_and_decode_hdf5_dataset
from pydidas.core.utils.hdf5.nxs_export import (
    nxs_create_nxentry,
    nxs_export_context,
    nxs_param_config_for_dset,
    nxs_recursive_update_default_attr,
    nxs_update_nxroot_timestamp,
    nxs_write_root_metadata,
)
from pydidas.core.utils.str_utils import get_random_string
from pydidas.version import VERSION


@pytest.fixture
def hdf5_file(temp_path):
    """Create a temporary HDF5 file for tests."""
    if not (temp_path / "hdf5_utils").is_dir():
        (temp_path / "hdf5_utils").mkdir()
    file = h5py.File(temp_path / "hdf5_utils" / "temp_file.h5", "w")
    yield file
    file.close()


def random_context() -> ObjectWithParameterCollection:
    """Create a random context object for testing."""
    _context = ObjectWithParameterCollection()
    for _n in range(10):
        _dtype = np.random.choice([int, float, str])
        if _dtype is int:
            _default = int(50 * np.random.random())
        elif _dtype is float:
            _default = np.round(np.random.random(), 6)
        else:
            _default = get_random_string(6)
        _param = Parameter(
            f"param{_n}",
            _dtype,
            _default,
            name=f"Parameter {_n}",
            unit=get_random_string(3),
            tooltip=f"Parameter {_n}",
        )
        _context.add_param(_param)
    return _context


def test_nxs_create_recursive_groups__basic(hdf5_file):
    _group_name = "test/test2"
    _group_type = "NXdata"
    attributes = {"attr1": "value1", "attr2": "value2"}
    _group = nxs_create_recursive_groups(
        hdf5_file, _group_name, _group_type, **attributes
    )
    assert hdf5_file.attrs.get("default") == "test"
    assert _group_name in hdf5_file
    assert _group.attrs["NX_class"] == _group_type
    for key, value in attributes.items():
        assert _group.attrs[key] == value


def test_nxs_create_recursive_groups__nested(hdf5_file):
    _group_name = "entry/test/nested"
    _group_type = "NXentry"
    attributes = {"attr1": "value1"}
    _group = nxs_create_recursive_groups(
        hdf5_file, _group_name, _group_type, **attributes
    )
    assert _group_name in hdf5_file
    assert _group.attrs["NX_class"] == _group_type
    for key, value in attributes.items():
        assert _group.attrs[key] == value


def test_nxs_create_recursive_groups__no_attributes(hdf5_file):
    _group_name = "entry/test"
    _group_type = "NXdata"
    _group = nxs_create_recursive_groups(hdf5_file, _group_name, _group_type)
    assert _group_name in hdf5_file
    assert _group.attrs["NX_class"] == _group_type


def test_nxs_create_recursive_groups__w_existing_group(hdf5_file):
    _group_name = "entry/test/group/name"
    _group_type = "NXentry"
    _group = nxs_create_recursive_groups(hdf5_file, _group_name, _group_type)
    _group2 = nxs_create_recursive_groups(hdf5_file, _group_name, _group_type)
    assert _group == _group2


def test_nxs_create_recursive_groups__in_existing_group(hdf5_file):
    _group_name = "entry/test/"
    _group_type = "NXdummy"
    _group = nxs_create_recursive_groups(hdf5_file, _group_name, _group_type)
    _group2 = nxs_create_recursive_groups(_group, "some/data", "NXdata")
    assert hdf5_file["entry"].attrs["NX_class"] == "NXentry"
    assert hdf5_file["entry/test"].attrs["NX_class"] == "NXdummy"
    assert hdf5_file["entry/test/some"].attrs["NX_class"] == "NXentry"
    assert hdf5_file["entry/test/some/data"].attrs["NX_class"] == "NXdata"


def test_nxs_create_recursive_groups__w_nxclass(hdf5_file):
    _test_data = [
        ["entry", "NXtest"],
        ["entry/data", "NXdata"],
        ["entry/instrument", "NXinstrument"],
        ["entry/coll", "NXcollection"],
        ["entry/coll/params", "NXparameters"],
    ]
    for _key, _group in _test_data:
        _ = nxs_create_recursive_groups(hdf5_file, _key, group_type=_group)
    for _key, _group in _test_data:
        assert hdf5_file[_key].attrs["NX_class"] == _group


def test_nxs_create_recursive_groups__update_existing_attr(hdf5_file):
    _test_data = [
        ["entry/data", "NXtest", {"updated": False, "value": "A"}],
        ["entry/data", "NXtest", {"updated": True, "value2": "B"}],
    ]
    for _key, _group, _attrs in _test_data:
        _ = nxs_create_recursive_groups(hdf5_file, _key, group_type=_group, **_attrs)
    assert hdf5_file["entry/data"].attrs == {
        "NX_class": "NXtest",
        "updated": True,
        "value": "A",
        "value2": "B",
    }


def test_nxs_create_recursive_groups__w_existing_group_different_type(hdf5_file):
    _group_name = "entry/test/group/name"
    _group_type = "NXentry"
    _ = nxs_create_recursive_groups(hdf5_file, _group_name, _group_type)
    with pytest.raises(ValueError):
        nxs_create_recursive_groups(hdf5_file, _group_name, "AnotherEntry")


def test_nxs_recursive_update_default_attr(hdf5_file):
    _group_name = "entry2/test/group/name"
    _group = hdf5_file.create_group(_group_name)
    _group.create_dataset("default_value", data="The default")
    nxs_recursive_update_default_attr(hdf5_file, _group_name + "/default_value")
    assert hdf5_file.attrs["default"] == "entry2"
    assert hdf5_file["entry2"].attrs["default"] == "test"
    assert hdf5_file["entry2/test"].attrs["default"] == "group"
    assert hdf5_file["entry2/test/group"].attrs["default"] == "name"
    assert hdf5_file["entry2/test/group/name"].attrs["default"] == "default_value"


def test_nxs_recursive_update_default_attr__in_group(hdf5_file):
    _group_name = "entry2/test/group/name"
    _group = hdf5_file.create_group(_group_name)
    _group.create_dataset("default_value", data="The default")
    _root = hdf5_file["entry2/test"]
    nxs_recursive_update_default_attr(_root, _group_name + "/default_value")
    assert hdf5_file.attrs.get("default") is None
    assert hdf5_file["entry2"].attrs.get("default") is None
    assert hdf5_file["entry2/test"].attrs["default"] == "group"
    assert hdf5_file["entry2/test/group"].attrs["default"] == "name"
    assert hdf5_file["entry2/test/group/name"].attrs["default"] == "default_value"


def test_nxs_recursive_update_default_attr__w_nonexisting_key(hdf5_file):
    _group_name = "entry2/test/group/name"
    _group = hdf5_file.create_group(_group_name)
    _group.create_dataset("default_value", data="The default")
    _root = hdf5_file["entry2/test"]
    with pytest.raises(UserConfigError):
        nxs_recursive_update_default_attr(_root, "dummy")


def test_nxs_write_nxdata__basic(hdf5_file):
    _name = "entry/test"
    data = np.random.random((10, 10))
    attributes = {"attr1": "value1", "attr2": "value2"}
    _group = nxs_write_nxdata(hdf5_file, _name, data, **attributes)
    assert _name in hdf5_file
    assert _group.attrs["NX_class"] == "NXdata"
    for key, value in attributes.items():
        assert _group.attrs[key] == value


def test_nxs_write_nxdata__w_axes(hdf5_file):
    _name = "entry/test"
    data = Dataset(
        np.random.random((10, 10)),
        axis_labels=["x", "y"],
        axis_units=["m", "s"],
        axis_ranges=[np.arange(10), np.arange(10)],
    )
    attributes = {"attr1": "value1"}
    _group = nxs_write_nxdata(hdf5_file, _name, data, **attributes)
    assert _name in hdf5_file
    assert _group.attrs["NX_class"] == "NXdata"
    for key, value in attributes.items():
        assert _group.attrs[key] == value
    for dim in range(data.ndim):
        assert f"axis_{dim}" in _group
        assert np.allclose(_group[f"axis_{dim}"][()], data.axis_ranges[dim])
        _ax = _group[f"axis_{dim}"]
        assert _ax.attrs["long_name"] == data.axis_labels[dim]
        assert _ax.attrs["units"] == data.axis_units[dim]
        assert np.allclose(_ax[()], data.axis_ranges[dim])


def test_nxs_write_dataset__basic(hdf5_file):
    _group = hdf5_file.create_group("entry")
    _name = "test_dataset"
    test_data = [np.random.random((10, 10)), "a test string", 1, 12.2]
    for data in test_data:
        if _name in _group:
            del _group[_name]
        dataset = nxs_write_dataset(_group, _name, data)
        assert _name in _group
        if isinstance(data, str):
            assert dataset[()].decode() == data
        else:
            assert np.array_equal(dataset[()], data)


def test_nxs_write_dataset__w_None(hdf5_file):
    _group = hdf5_file.create_group("entry")
    _name = "test_dataset"
    dataset = nxs_write_dataset(_group, _name, None)
    assert _name in _group
    assert dataset[()] == b"::None::"


def test_nxs_write_dataset__replace_existing(hdf5_file):
    _group = hdf5_file.create_group("entry")
    _test_data = np.random.random((10, 10))
    _new_test_data = np.random.random((5, 2))
    _ = nxs_write_dataset(_group, "test", _test_data)
    _dset = nxs_write_dataset(_group, "test", _new_test_data)
    assert "test" in _group
    assert np.array_equal(_dset[()], _new_test_data)


def test_nxs_write_dataset__w_dict(hdf5_file):
    _group = hdf5_file.create_group("entry")
    _name = "test_dataset"
    attrs = {"attr1": "value1", "attr2": "value2"}
    test_data = [
        {"data": np.random.random((10, 10))},
        {"shape": (10, 10)},
    ]
    for data in test_data:
        if _name in _group:
            del _group[_name]
        dataset = nxs_write_dataset(_group, _name, data, **attrs)
        assert _name in _group
        assert np.array_equal(dataset[()].shape, (10, 10))
        for key, value in attrs.items():
            assert dataset.attrs[key] == value


def test_nxs_write_dataset__w_attributes(hdf5_file):
    _group = hdf5_file.create_group("entry")
    _name = "test_dataset"
    data = np.random.random((10, 10))
    attributes = {"units": "meters", "long_name": "Test Dataset"}
    dataset = nxs_write_dataset(_group, _name, data, **attributes)
    assert _name in _group
    assert np.array_equal(dataset[()], data)
    for key, value in attributes.items():
        assert dataset.attrs[key] == value


@pytest.mark.parametrize("name", ["", "p_name"])
@pytest.mark.parametrize("unit", ["", "m/s"])
@pytest.mark.parametrize("value", ["", "val"])
def test_nxs_param_config_for_dset(name, unit, value):
    _param = Parameter("test", str, value, name=name, tooltip="Spam & eggs", unit=unit)
    _val, _config = nxs_param_config_for_dset(_param)
    _expected_description = f"Spam & eggs ({'unit: m/s, ' if unit else ''}type: str)"
    assert _val == value
    assert _config.get("description") == _expected_description
    assert _config.get("long_name") == (name if name else None)
    assert _config.get("units") == (unit if unit else None)


def test_nxs_param_config_for_dset__no_tooltip():
    _param = Parameter("test", str, "a", name="The name")
    with patch.object(
        type(_param), "tooltip", new_callable=PropertyMock
    ) as mock_tooltip:
        mock_tooltip.return_value = ""
        _val, _config = nxs_param_config_for_dset(_param)
        assert _config.get("description") is None


def test_nxs_export_context(hdf5_file):
    _ctx = random_context()
    nxs_export_context(hdf5_file, _ctx, "test/entry")
    assert hdf5_file.attrs.get("default") == "test"
    assert hdf5_file.attrs.get("NX_class") == "NXroot"
    assert hdf5_file["test"].attrs.get("NX_class") == "NXentry"
    assert hdf5_file["test/entry"].attrs.get("NX_class") == "NXparameters"
    for _key, _param in _ctx.params.items():
        assert f"test/entry/{_key}" in hdf5_file
        _dset = hdf5_file[f"test/entry/{_key}"]
        _val = read_and_decode_hdf5_dataset(_dset)
        assert _val == _param.value


def test_nxs_create_nxentry(hdf5_file):
    _ = nxs_create_nxentry(hdf5_file, "entry1")
    assert hdf5_file.attrs.get("default") == "entry1"
    assert hdf5_file["entry1"].attrs.get("NX_class") == "NXentry"
    assert hdf5_file["entry1/program_name"].attrs.get("version") == VERSION
    assert hdf5_file["entry1/program_name"][()].decode() == "pydidas"
    _ = nxs_create_nxentry(hdf5_file, "entry2")
    assert hdf5_file.attrs.get("default") == "entry2"


def test_nxs_create_nxentry__existing_entry(hdf5_file):
    _entry = nxs_create_nxentry(hdf5_file)
    _new_entry = nxs_create_nxentry(hdf5_file)
    assert _entry == _new_entry


def test_update_nxroot_timestamp(hdf5_file):
    nxs_write_root_metadata(hdf5_file)
    hdf5_file.attrs["file_update_time"] = "test"
    nxs_update_nxroot_timestamp(hdf5_file)
    _time_str = hdf5_file.attrs["file_update_time"]
    _epoch = datetime.fromisoformat(_time_str).timestamp()
    assert np.allclose(_epoch, time.time(), atol=5)


if __name__ == "__main__":
    pytest.main([__file__])
