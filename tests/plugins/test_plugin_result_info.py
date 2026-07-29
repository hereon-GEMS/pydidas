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

import numpy as np
import pytest

from pydidas.plugins.plugin_result_info import PluginResultInfo


_CUSTOM_SHAPE = (100, 1, 200, 50)
_DEFAULT_VALUES = {
    "label": "",
    "node_id": None,
    "plugin_name": "",
    "result_title": "",
    "axis_ranges": {},
}
_CUSTOM_VALUES = {
    "label": "test",
    "node_id": 7,
    "plugin_name": "TestPlugin",
    "result_title": "Test Result",
    "axis_ranges": {_i: np.arange(_val) for _i, _val in enumerate(_CUSTOM_SHAPE)},
}


def test_init__w_default():
    _info = PluginResultInfo()
    for _key, _val in _DEFAULT_VALUES.items():
        assert getattr(_info, _key) == _val
    assert _info.export_shape == ()


def test_init__w_customs():
    _info = PluginResultInfo(**_CUSTOM_VALUES)
    for _key, _val in _CUSTOM_VALUES.items():
        assert getattr(_info, _key) == _val
    assert _info.export_shape == _CUSTOM_SHAPE


@pytest.mark.parametrize("key, val", [(_k, _v) for _k, _v in _CUSTOM_VALUES.items()])
def test_init__w_partial_keys(key, val):
    _info = PluginResultInfo(**{key: val})
    for _key, _val in _CUSTOM_VALUES.items():
        if _key == key == "axis_ranges":
            for _ax, _arr in _val.items():
                assert np.allclose(_info.axis_ranges[_ax], _arr)
        elif _key == key:
            assert getattr(_info, _key) == _val
        else:
            assert getattr(_info, _key) == _DEFAULT_VALUES[_key]


@pytest.mark.parametrize(
    "shape, expected_export",
    [
        ((), ()),
        ((1, 1, 1), ()),
        ((100,), (100,)),
        ((1, 100, 1, 200, 1), (100, 200)),
        ((100, 200, 50), (100, 200, 50)),
        ((1, 1, 100, 200), (100, 200)),
        ((100, 200, 1, 1), (100, 200)),
        ((1,), ()),
    ],
)
@pytest.mark.parametrize("squeeze", [True, False])
def test_export_shape__w_various_shapes(shape, expected_export, squeeze):
    _ax_ranges = {_i: np.arange(_n) for _i, _n in enumerate(shape)}
    _info = PluginResultInfo(axis_ranges=_ax_ranges, squeeze=squeeze)
    if squeeze:
        assert _info.export_shape == expected_export
    else:
        assert _info.export_shape == shape


@pytest.mark.parametrize("node_id", [None, 0, 2, -1])
def test_node_id__w_different_values(node_id):
    info = PluginResultInfo(node_id=node_id)
    if node_id is None:
        assert info.node_id is None
    else:
        assert info.node_id == node_id


def test__modify_shape_after_initialization():
    _ax_ranges = {_i: np.arange(_n) for _i, _n in enumerate((100, 200))}
    _info = PluginResultInfo(axis_ranges=_ax_ranges)
    assert _info.export_shape == (100, 200)
    _new_shape = (1, 200, 1, 50, 1)
    _new_ax_ranges = {_i: np.arange(_n) for _i, _n in enumerate(_new_shape)}
    _info.axis_ranges = _new_ax_ranges
    assert _info.export_shape == _new_shape
    _info.squeeze = True
    assert _info.export_shape == (200, 50)


def test_axis_ranges_setter():
    _info = PluginResultInfo(**_CUSTOM_VALUES)
    _new_ranges = {0: np.arange(24), 1: np.arange(42), 2: np.arange(75)}
    _info.axis_ranges = _new_ranges
    for _dim, _arr in _new_ranges.items():
        assert np.allclose(_arr, _info.axis_ranges[_dim])
    assert _info.shape == (24, 42, 75)


def test_dataset_metadata_setter():
    _info = PluginResultInfo()
    _metadata = {
        "data_label": "Test Label",
        "data_unit": "Test Unit",
        "axis_labels": {0: "X", 1: "Y"},
        "axis_units": {0: "mm", 1: "mm"},
        "axis_ranges": {0: np.arange(100), 1: np.arange(200)},
    }
    _info.dataset_metadata = _metadata
    for _key, _val in _metadata.items():
        assert getattr(_info, _key) == _val
    assert _info.shape == (100, 200)


@pytest.mark.parametrize("prop", ["data_label", "data_unit"])
def test_dataset_metadata__w_str_fields(prop):
    _info = PluginResultInfo(**_CUSTOM_VALUES)
    _metadata = {prop: "Test Value"}
    _info.dataset_metadata = _metadata
    assert getattr(_info, prop) == "Test Value"
    assert _info.axis_labels == {}
    assert _info.axis_units == {}
    assert _info.axis_ranges == {}
    assert _info.shape == ()


@pytest.mark.parametrize("prop", ["axis_labels", "axis_units"])
def test_dataset_metadata__w_dict_fields(prop):
    _info = PluginResultInfo(**_CUSTOM_VALUES)
    _metadata = {prop: {0: "Test Value 0 ", 1: "Test Value 1"}}
    _info.dataset_metadata = _metadata
    assert getattr(_info, prop) == _metadata[prop]
    assert _info.data_label == ""
    assert _info.data_unit == ""
    assert _info.axis_ranges == {}
    assert _info.shape == ()
    if prop == "axis_labels":
        assert _info.axis_units == {}
    if prop == "axis_units":
        assert _info.axis_labels == {}


def test_dataset_metadata__w_axis_ranges():
    _info = PluginResultInfo(**_CUSTOM_VALUES)
    _metadata = {"axis_ranges": {0: np.arange(42), 1: np.arange(123)}}
    _info.dataset_metadata = _metadata
    assert getattr(_info, "axis_ranges") == _metadata["axis_ranges"]
    assert _info.data_label == ""
    assert _info.data_unit == ""
    assert _info.axis_labels == {}
    assert _info.axis_units == {}
    assert _info.shape == (42, 123)


@pytest.mark.parametrize("scan_ndim", [1, 2, 3])
def test_result_ndim(scan_ndim):
    _info = PluginResultInfo(scan_ndim=scan_ndim, **_CUSTOM_VALUES)
    assert _info.result_ndim == len(_CUSTOM_SHAPE) - scan_ndim


@pytest.mark.parametrize("scan_ndim", [1, 2, 3])
def test_result_shape(scan_ndim):
    _expected_shape = _CUSTOM_SHAPE[scan_ndim:]
    _info = PluginResultInfo(scan_ndim=scan_ndim, **_CUSTOM_VALUES)
    assert _info.result_shape == _expected_shape


def test_dataclass__equality():
    _info1 = PluginResultInfo(**_CUSTOM_VALUES)
    _info2 = PluginResultInfo(**_CUSTOM_VALUES)
    assert _info1 == _info2


def test_dataclass__inequality():
    _info1 = PluginResultInfo(label="Test1")
    _info2 = PluginResultInfo(label="Test2")
    assert _info1 != _info2


def test_copy():
    _info1 = PluginResultInfo(**_CUSTOM_VALUES)
    _info2 = _info1.copy()
    assert _info1 == _info2
    assert _info1 is not _info2


if __name__ == "__main__":
    pytest.main([__file__])
