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


import pytest

from pydidas.plugins.plugin_result_info import PluginResultInfo


_DEFAULT_VALUES = {
    "label": "",
    "node_id": None,
    "plugin_name": "",
    "result_title": "",
    "result_metadata": {},
    "shape": (),
}
_CUSTOM_VALUES = {
    "label": "test",
    "node_id": 7,
    "plugin_name": "TestPlugin",
    "result_title": "Test Result",
    "result_metadata": {"key1": True, "b": "test"},
    "shape": (100, 1, 200, 50),
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
    assert _info.export_shape == _CUSTOM_VALUES["shape"]  # type : ignore[type]


@pytest.mark.parametrize("key, val", [(_k, _v) for _k, _v in _CUSTOM_VALUES.items()])
def test_init__w_partial_keys(key, val):
    _info = PluginResultInfo(**{key: val})
    for _key, _val in _CUSTOM_VALUES.items():
        if _key == key:
            assert getattr(_info, _key) == _val
        else:
            assert getattr(_info, _key) == _DEFAULT_VALUES[_key]


def test_metadata_independence():
    """Test that metadata dictionaries are independent between instances."""
    _info1 = PluginResultInfo()
    _info2 = PluginResultInfo()

    _info1.result_metadata["key"] = "value1"
    assert "key" not in _info2.result_metadata
    assert _info2.result_metadata == {}


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
    _info = PluginResultInfo(shape=shape, squeeze=squeeze)
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


def test_metadata__with_complex_values():
    metadata = {
        "string": "value",
        "int": 42,
        "float": 3.14,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "none": None,
    }
    info = PluginResultInfo(result_metadata=metadata)
    assert info.result_metadata == metadata


def test__modify_metadata_outside_dataclass():
    metadata = {
        "string": "value",
        "int": 42,
    }
    _info = PluginResultInfo(result_metadata=metadata)
    _meta = _info.result_metadata
    _meta["string"] = "new value"
    assert _info.result_metadata == _meta


def test__modify_shape_after_initialization():
    _info = PluginResultInfo(shape=(100, 200))
    assert _info.export_shape == (100, 200)
    _new_shape = (1, 200, 1, 50, 1)
    _info.shape = _new_shape
    assert _info.export_shape == _new_shape
    _info.squeeze = True
    assert _info.export_shape == (200, 50)


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
    assert _info1.result_metadata is not _info2.result_metadata
    _info2.result_metadata["key1"] = False
    assert _info1.result_metadata['key1'] is True



if __name__ == "__main__":
    pytest.main([__file__])
