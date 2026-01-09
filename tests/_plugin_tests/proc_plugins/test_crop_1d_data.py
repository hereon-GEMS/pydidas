# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import numpy as np
import pytest

import pydidas
from pydidas.core import UserConfigError
from pydidas.plugins import ProcPlugin
from pydidas.unittest_objects import create_dataset


_DATA = create_dataset(5, dtype=float)
_REGISTRY = pydidas.plugins.PluginCollection()


@pytest.fixture
def plugin():
    _plugin_class = _REGISTRY.get_plugin_by_name("Crop1dData")
    _plugin = _plugin_class()
    _plugin.set_param_value("crop_low", 1)
    _plugin.set_param_value("crop_high", 3)
    _plugin.set_param_value("type_selection", "Indices")
    yield _plugin


@pytest.fixture
def data():
    return _DATA.copy()


def test_init(plugin):
    assert isinstance(plugin, ProcPlugin)


@pytest.mark.parametrize("bounds", [[None, None], [0, None], [None, 3], [0, 3]])
def test_pre_execute(plugin, bounds):
    plugin._data = "dummy"
    plugin.set_param_value("crop_low", bounds[0])
    plugin.set_param_value("crop_high", bounds[1])
    if bounds == [None, None]:
        with pytest.raises(UserConfigError):
            plugin.pre_execute()
    else:
        plugin.pre_execute()
        assert plugin._data is None
        assert plugin._config["slices"] is None


def test_get_slices__existing_slices(plugin):
    _defined_slices = (slice(None, None), slice(1, 2))
    plugin._config["slices"] = _defined_slices
    _received_slices = plugin._get_slices()
    assert _received_slices == _defined_slices


@pytest.mark.parametrize("process_data_dim", [6, -6])
def test_get_slices__invalid_data_dim(plugin, data, process_data_dim):
    plugin.set_param_value("process_data_dim", process_data_dim)
    plugin._data = data
    with pytest.raises(UserConfigError):
        plugin._get_slices()


@pytest.mark.parametrize("process_data_dim", [0, 1, 2, 3, 4, -1, -2, -3, -4])
def test_get_slices__valid_data_dim__w_indices(plugin, data, process_data_dim):
    plugin.set_param_value("process_data_dim", process_data_dim)
    plugin._data = data
    _target_slicing_dim = process_data_dim % data.ndim
    _target_slices = (slice(None, None),) * _target_slicing_dim + (slice(1, 4),)
    _received_slices = plugin._get_slices()
    assert _received_slices == _target_slices
    assert plugin._config["slices"] == _target_slices


@pytest.mark.parametrize("proc_dim", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("cropping", [[None, 7], [2, None], [2, 7]])
def test_get_slices__valid_data_dim__w_data_range(plugin, data, proc_dim, cropping):
    crop_low, crop_high = cropping
    plugin.set_param_value("process_data_dim", proc_dim)
    plugin.set_param_value("type_selection", "Axis values")
    _xlow = data.axis_ranges[proc_dim][crop_low] if crop_low is not None else None
    plugin.set_param_value("crop_low", _xlow)
    _xhigh = data.axis_ranges[proc_dim][crop_high] if crop_high is not None else None
    plugin.set_param_value("crop_high", _xhigh)
    plugin._data = data
    if crop_low is None:
        crop_low = 0
    if crop_high is None:
        crop_high = data.shape[proc_dim]
    else:
        # increment the target by one to include the final datapoint
        crop_high += 1
    _target_slices = (slice(None, None),) * proc_dim + (slice(crop_low, crop_high),)
    _received_slices = plugin._get_slices()
    assert _received_slices == _target_slices
    assert plugin._config["slices"] == _target_slices


@pytest.mark.parametrize("proc_dim", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("cropping", [[None, 7], [2, None], [2, 7]])
def test_execute(plugin, data, proc_dim, cropping):
    crop_low, crop_high = cropping
    plugin.set_param_value("process_data_dim", proc_dim)
    plugin.set_param_value("crop_low", crop_low)
    plugin.set_param_value("crop_high", crop_high)
    _new_data, _ = plugin.execute(data)
    if crop_high is not None:
        # increment the target by one to include the final datap
        crop_high += 1
    _slicing = (slice(None, None),) * proc_dim + (slice(crop_low, crop_high),)
    _sliced_data = data[_slicing]
    assert _new_data.shape == _sliced_data.shape
    assert _new_data.axis_labels == _sliced_data.axis_labels
    assert _new_data.axis_units == _sliced_data.axis_units
    for _i_dim, _range in _new_data.axis_ranges.items():
        assert np.allclose(_range, _sliced_data.axis_ranges[_i_dim])


if __name__ == "__main__":
    pytest.main()
