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


import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.data_io import export_data
from pydidas.plugins import InputPlugin
from pydidas.unittest_objects import LocalPluginCollection
from pydidas.widgets.plugin_config_widgets import PluginConfigWidgetWithCustomXscale


SCAN = ScanContext()
PLUGIN_COLLECTION = LocalPluginCollection()
_x_unit = get_random_string(3)
_x_label = get_random_string(6)

_X_OFFSET = 4.2
_X_DELTA = 0.5
_DUMMY_SHAPE_1d = (145,)


_CUSTOM_XRANGE = np.arange(_DUMMY_SHAPE_1d[0]) * _X_DELTA + _X_OFFSET


@pytest.fixture
def setup_scan(temp_path):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_dim", 1)
    SCAN.set_param_value("scan_dim0_n_points", 20)
    SCAN.set_param_value("scan_base_directory", temp_path)
    SCAN.set_param_value("scan_name_pattern", "test_#####.txt")
    SCAN.set_param_value("frame_indices_per_scan_point", 1)


@pytest.fixture
def plugin():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("ASCII1dProfileLoader")()
    return plugin


@pytest.fixture(scope="module")
def test_data():
    return Dataset(
        np.random.random((145,)),
        axis_labels=[_x_label],
        axis_units=[_x_unit],
        data_unit="some counts",
        data_label="Test data",
    )


@pytest.fixture(scope="module")
def test_data_multicol():
    _x0_label = "; ".join([f"{i}: {get_random_string((6))}" for i in range(6)])
    return Dataset(
        np.random.random((145, 6)),
        axis_labels=[_x_label, _x0_label],
        axis_units=[_x_unit, ""],
        axis_ranges=[_CUSTOM_XRANGE, np.arange(6)],
        data_unit="some counts",
        data_label="Test data",
    )


@pytest.fixture(scope="module")
def stored_data(temp_path, test_data):
    for _ii in range(20):
        export_data(
            f"{temp_path}/test_{_ii:05d}.txt",
            test_data + _ii,
            overwrite=True,
        )


def test__creation(plugin):
    assert plugin.base_output_data_dim == 1
    assert plugin.plugin_name == "ASCII 1d profile loader"
    assert isinstance(plugin, InputPlugin)
    for key in ["use_custom_xscale", "x0_offset", "x_delta", "x_label", "x_unit"]:
        assert key in plugin.params


def test_pre_execute(plugin):
    plugin._ASCII1dProfileLoader__yslice = 1
    plugin._ASCII1dProfileLoader__xscale_valid = True
    plugin.pre_execute()
    assert plugin._standard_kwargs["roi"] is None
    assert plugin._config["pre_executed"]
    assert plugin._ASCII1dProfileLoader__yslice is None
    assert not plugin._ASCII1dProfileLoader__xscale_valid


@pytest.mark.parametrize("custom_xscale", [True, False])
def test_get_frame(setup_scan, stored_data, test_data, plugin, custom_xscale):
    plugin.set_param_value("use_custom_xscale", custom_xscale)
    plugin.set_param_value("x0_offset", _X_OFFSET)
    plugin.set_param_value("x_delta", _X_DELTA)
    plugin.set_param_value("x_label", _x_label)
    plugin.set_param_value("x_unit", _x_unit)
    plugin.pre_execute()
    _data, kwargs = plugin.get_frame(0)
    _data2, kwargs = plugin.get_frame(1)
    assert isinstance(_data, Dataset)
    assert _data.shape == test_data.shape
    assert np.all(_data == pytest.approx(test_data))
    assert np.all(_data2 == pytest.approx(test_data + 1))
    assert _data.data_unit == test_data.data_unit
    assert _data.data_label == test_data.data_label
    if custom_xscale:
        assert np.all(_data.axis_ranges[0] == pytest.approx(_CUSTOM_XRANGE))
        assert _data.axis_labels[0] == _x_label
        assert _data.axis_units[0] == _x_unit
    else:
        assert np.all(_data.axis_ranges[0] == test_data.axis_ranges[0])
        assert _data.axis_labels[0] == test_data.axis_labels[0]
        assert _data.axis_units[0] == test_data.axis_units[0]


@pytest.mark.parametrize("col_x", [None, 0, 2])
@pytest.mark.parametrize("col_y", [None, 1, 4])
@pytest.mark.parametrize("format", ["txt", "dat", "csv"])
@pytest.mark.parametrize("header", [True, False])
def test_get_frame__multicol__w_written_x_col(
    setup_scan, test_data_multicol, temp_path, plugin, col_x, col_y, format, header
):
    export_data(
        temp_path / f"test_multicol_00.{format}",
        test_data_multicol,
        overwrite=True,
        write_header=header,
    )
    export_data(
        temp_path / f"test_multicol_01.{format}",
        test_data_multicol + 1,
        overwrite=True,
        write_header=header,
    )
    _stored_data = np.column_stack(
        (test_data_multicol.axis_ranges[0], test_data_multicol)
    )
    SCAN.set_param_value("scan_name_pattern", f"test_multicol_##.{format}")
    plugin.set_param_value("x_column", col_x)
    plugin.set_param_value("y_column", col_y)
    plugin.pre_execute()
    if col_y is None:
        with pytest.raises(UserConfigError):
            _ = plugin.get_frame(0)
        return
    _ref_x = (
        test_data_multicol.axis_ranges[0]
        if (header and format in ["txt", "csv"]) or col_x == 0
        else (
            np.arange(test_data_multicol.shape[0])
            if col_x is None
            else test_data_multicol[:, col_x - 1]
        )
    )
    _ref_y = _stored_data[:, col_y]
    _data, _ = plugin.get_frame(0)
    _data_1, _ = plugin.get_frame(1)
    assert np.allclose(_data.axis_ranges[0], _ref_x)
    assert np.allclose(_data, _ref_y)
    assert np.allclose(_data_1, _ref_y + 1)


@pytest.mark.parametrize("col_x", [None, 0, 2])
@pytest.mark.parametrize("col_y", [1, 4])
@pytest.mark.parametrize("format", ["txt", "dat", "csv"])
def test_get_frame__multicol__no_written_x_col(
    setup_scan, test_data_multicol, temp_path, plugin, col_x, col_y, format
):
    export_data(
        temp_path / f"test_multicol_11.{format}",
        test_data_multicol,
        overwrite=True,
        x_column=False,
    )
    SCAN.set_param_value("scan_name_pattern", f"test_multicol_11.{format}")
    plugin.set_param_value("x_column", col_x)
    plugin.set_param_value("y_column", col_y)
    plugin.pre_execute()
    _data, _ = plugin.get_frame(11)
    if col_x is None:
        assert np.allclose(_data.axis_ranges[0], np.arange(_data.size))
    else:
        assert np.allclose(_data.axis_ranges[0], test_data_multicol[:, col_x])
    assert np.allclose(_data, test_data_multicol[:, col_y])


def test_get_frame__w_custom_x_column(setup_scan, test_data, stored_data, plugin):
    _x0, _x_delta = 42, 1.234
    _x_label, _x_unit = get_random_string(6), get_random_string(3)
    plugin.set_param_value("use_custom_xscale", True)
    plugin.set_param_value("x0_offset", _x0)
    plugin.set_param_value("x_delta", _x_delta)
    plugin.set_param_value("x_label", _x_label)
    plugin.set_param_value("x_unit", _x_unit)
    plugin.pre_execute()
    _data, _ = plugin.get_frame(11)
    assert np.allclose(_data.axis_ranges[0], np.arange(_data.size) * _x_delta + _x0)
    assert _data.axis_labels[0] == _x_label
    assert _data.axis_units[0] == _x_unit
    assert np.allclose(_data, test_data + 11)
    assert plugin._ASCII1dProfileLoader__xscale_valid


@pytest.mark.parametrize("ordinal", [0, 7])
@pytest.mark.parametrize("frame_indices", [1, 2, 4])
@pytest.mark.parametrize("custom_xscale", [True, False])
@pytest.mark.parametrize("handling", ["Average", "Stack"])
def test_execute(
    plugin,
    stored_data,
    test_data,
    setup_scan,
    ordinal,
    frame_indices,
    custom_xscale,
    handling,
):
    _ref_range = _CUSTOM_XRANGE if custom_xscale else np.arange(_DUMMY_SHAPE_1d[0])
    SCAN.set_param_value("scan_multi_frame_handling", handling)
    SCAN.set_param_value("scan_frames_per_point", frame_indices)
    plugin.set_param_value("use_custom_xscale", custom_xscale)
    plugin.set_param_value("x0_offset", _X_OFFSET)
    plugin.set_param_value("x_delta", _X_DELTA)
    plugin.set_param_value("x_label", _x_label)
    plugin.set_param_value("x_unit", _x_unit)
    plugin.pre_execute()
    _data, _kwargs = plugin.execute(ordinal)
    assert isinstance(_data, Dataset)
    assert (
        _data.shape == test_data.shape
        if handling == "Average"
        else (frame_indices,) + test_data.shape
    )
    _dim_data = 0
    if handling == "Stack" and frame_indices > 1:
        _dim_data += 1
        assert all(
            _data[i] == pytest.approx(test_data + ordinal + i)
            for i in range(frame_indices)
        )
        assert _data.axis_labels[0] == "image number"
        assert _data.axis_units[0] == ""
    else:
        _offset = (
            (ordinal + frame_indices) * (ordinal + frame_indices - 1) / 2
            - ordinal * (ordinal - 1) / 2
        ) / frame_indices
        assert _data == pytest.approx(_offset + test_data)
    assert _data.axis_labels[_dim_data] == (
        _x_label if custom_xscale else test_data.axis_labels[0]
    )
    assert _data.axis_units[_dim_data] == (
        _x_unit if custom_xscale else test_data.axis_units[0]
    )
    assert np.all(_data.axis_ranges[_dim_data] == _ref_range)
    assert _data.data_unit == plugin.output_data_unit
    assert _data.data_label == plugin.output_data_label


def test_get_parameter_config_widget(plugin):
    _widget = plugin.get_parameter_config_widget()
    assert _widget == PluginConfigWidgetWithCustomXscale


if __name__ == "__main__":
    pytest.main()
