# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path

import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin, Input1dXRangeMixin, InputPlugin
from pydidas.widgets.plugin_config_widgets import PluginConfigWidgetWithCustomXscale


SCAN = ScanContext()
_X_UNIT = get_random_string(3)
_X_LABEL = get_random_string(6)
_X_OFFSET = 4.2
_X_DELTA = 0.5
_DUMMY_SHAPE_1d = (145,)
_CUSTOM_XRANGE = np.arange(_DUMMY_SHAPE_1d[0]) * _X_DELTA + _X_OFFSET


class TestInputPlugin(Input1dXRangeMixin, InputPlugin):
    output_data_label = "Test data"
    output_data_unit = "some counts"

    def get_frame(self, index, **kwargs):
        _frame = Dataset(
            np.zeros(_DUMMY_SHAPE_1d, dtype=np.uint16) + index,
            axis_labels=["det x0"],
            axis_units=["pixxxel"],
            data_unit=self.output_data_unit,
            data_label=self.output_data_label,
        )
        return _frame, kwargs

    def update_filename_string(self):
        pass


@pytest.fixture
def setup_scan():
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", "test_#####.h5")
    SCAN.set_param_value("scan_base_directory", Path())
    SCAN.set_param_value("frame_indices_per_scan_point", 1)


def test__creation():
    plugin = TestInputPlugin()
    assert plugin.base_output_data_dim == 1
    assert plugin.has_unique_parameter_config_widget
    for key in ["use_custom_xscale", "x0_offset", "x_delta", "x_label", "x_unit"]:
        assert key in plugin.params
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input(setup_scan):
    plugin = TestInputPlugin()
    plugin.pre_execute()
    assert plugin._config["xrange"] is None
    assert plugin._config["pre_executed"]


@pytest.mark.parametrize("ordinal", [0, 7, 55])
@pytest.mark.parametrize("frame_indices", [1, 2, 4, 8])
@pytest.mark.parametrize("custom_xscale", [True, False])
@pytest.mark.parametrize("handling", ["Average", "Stack"])
def test_execute(setup_scan, ordinal, frame_indices, custom_xscale, handling):
    _ref_range = _CUSTOM_XRANGE if custom_xscale else np.arange(_DUMMY_SHAPE_1d[0])
    SCAN.set_param_value("scan_multi_frame_handling", handling)
    SCAN.set_param_value("scan_frames_per_point", frame_indices)
    plugin = TestInputPlugin()
    plugin.set_param_value("use_custom_xscale", custom_xscale)
    plugin.set_param_value("x0_offset", _X_OFFSET)
    plugin.set_param_value("x_delta", _X_DELTA)
    plugin.set_param_value("x_label", _X_LABEL)
    plugin.set_param_value("x_unit", _X_UNIT)
    plugin.pre_execute()
    _data, _kwargs = plugin.execute(ordinal)
    assert isinstance(_data, Dataset)
    assert (
        _data.shape == _DUMMY_SHAPE_1d
        if handling == "Average"
        else (frame_indices,) + _DUMMY_SHAPE_1d
    )
    _dim_data = 0
    if handling == "Stack" and frame_indices > 1:
        _dim_data += 1
        assert all(
            _data[i].mean() == pytest.approx(ordinal + i) for i in range(frame_indices)
        )
        assert _data.axis_labels[0] == "image number"
        assert _data.axis_units[0] == ""
    else:
        assert _data.mean() == pytest.approx(ordinal + (frame_indices - 1) / 2)
    assert _data.axis_labels[_dim_data] == (_X_LABEL if custom_xscale else "det x0")
    assert _data.axis_units[_dim_data] == (_X_UNIT if custom_xscale else "pixxxel")
    assert np.all(_data.axis_ranges[_dim_data] == _ref_range)
    assert _data.data_unit == plugin.output_data_unit
    assert _data.data_label == plugin.output_data_label


def test_get_parameter_config_widget():
    plugin = TestInputPlugin()
    _widget = plugin.get_parameter_config_widget()
    assert _widget == PluginConfigWidgetWithCustomXscale


if __name__ == "__main__":
    pytest.main()
