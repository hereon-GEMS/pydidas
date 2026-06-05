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

from pathlib import Path

import h5py
import numpy as np
import pytest
from qtpy import QtCore

from pydidas_plugins.input_plugins.nxdata_result_loader import NXdataResultLoader

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, FileReadError, UserConfigError
from pydidas.data_io import export_data
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection, create_dataset


PLUGIN_COLLECTION = LocalPluginCollection()
SCAN = ScanContext()

_FILENAME = "test_node.nxs"
_SHAPE = (10, 15)
_N_PER_FILE = 13
_N_FILES = 11
_DATA_SHAPE = (_N_PER_FILE,) + _SHAPE


class __Config:
    def __init__(self, temp_path: Path):
        self.scan_shape: tuple[int, ...] = (3, 4, 5)
        self.data_shape = (11, 13)
        self.dset_key = "entry/test/data"
        self.dataset = create_dataset(ndim=5, shape=self.scan_shape + self.data_shape)
        export_data(temp_path / _FILENAME, self.dataset, dataset=self.dset_key)


@pytest.fixture()
def config(empty_temp_path):
    config = __Config(empty_temp_path)
    SCAN.set_param_value("scan_base_directory", empty_temp_path)
    SCAN.set_param_value("scan_name_pattern", _FILENAME)
    SCAN.set_param_value("scan_dim", 3)
    for _i in range(3):
        SCAN.set_param_value(f"scan_dim{_i}_n_points", config.scan_shape[_i])
    yield config
    SCAN.restore_all_defaults(True)
    # necessary due to use of 'LocalPluginCollection':
    qs = QtCore.QSettings("Hereon", "pydidas")
    qs.remove("unittesting")


@pytest.fixture
def plugin(config) -> NXdataResultLoader:
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("NXdataResultLoader")()
    plugin.set_param_value("nxdata_key", config.dset_key)
    plugin.pre_execute()
    return plugin


def assert_dataset_equality__wo_data(config, data):
    _ref = config.dataset[(0,) * SCAN.ndim]
    assert data.shape == config.data_shape
    assert data.data_label == _ref.data_label
    assert data.data_unit == _ref.data_unit
    assert data.axis_labels == _ref.axis_labels
    assert data.axis_units == _ref.axis_units
    for _ax in range(_ref.ndim):
        assert np.allclose(data.axis_ranges[_ax], _ref.axis_ranges[_ax])


def test_creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("NXdataResultLoader")()
    assert isinstance(plugin, BasePlugin)
    assert plugin.__class__.__name__ == "NXdataResultLoader"


@pytest.mark.parametrize("expected_data_dim", [1, 2, 3])
@pytest.mark.parametrize("multi_frame", ["Stack", "Average"])
@pytest.mark.parametrize("multi_frame_n", [1, 3])
def test_output_data_dim(config, plugin, expected_data_dim, multi_frame, multi_frame_n):
    plugin.set_param_value("expected_data_dim", expected_data_dim)
    SCAN.set_param_value("scan_frames_per_point", multi_frame_n)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    _expected = (multi_frame == "Stack" and multi_frame_n > 1) + expected_data_dim
    assert plugin.output_data_dim == _expected


@pytest.mark.parametrize("index", [0, 5, 155])
def test_input_available(config, plugin, index):
    assert plugin.input_available(index)


def test_pre_execute(config, empty_temp_path):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("NXdataResultLoader")()
    plugin.set_param_value("nxdata_key", config.dset_key)
    plugin.pre_execute()
    assert plugin._config["pre_executed"]
    assert plugin._config["filename"] == empty_temp_path / _FILENAME
    assert isinstance(plugin._config["frame_metadata"], dict)


def test_pre_execute__check_stored_metadata(config, empty_temp_path):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("NXdataResultLoader")()
    plugin.set_param_value("nxdata_key", config.dset_key)
    plugin.pre_execute()
    _data = config.dataset[(0,) * SCAN.ndim]
    assert plugin.output_data_label == _data.data_label
    assert plugin.output_data_unit == _data.data_unit
    for _key, _val in plugin._config["frame_metadata"].items():
        if _key == "axis_ranges":
            for _ax, _range in _val.items():
                assert np.allclose(_data.axis_ranges[_ax], _range)
        elif _key != "metadata":
            assert getattr(_data, _key) == _val


def test_verify_data_shape_valid(config, plugin):
    assert plugin._verify_data_shape_valid() is None


@pytest.mark.parametrize(
    "key, value",
    [
        ["scan_dim0_n_points", 42],
        ["nxdata_key", "entry/no/data"],
        ["scan_base_directory", "random/invalid/dir/"],
        ["scan_name_pattern", "no_such_file.name"],
        ["scan_name_pattern", "no_such_file_with_hash_###.name"],
        ["expected_data_dim", 3],
        ["expected_data_dim", 1],
    ],
)
def test_verify_data_shape_valid__w_invalid_param(config, plugin, key, value):
    _param_source = plugin._SCAN if key.startswith("scan") else plugin
    _param_source.set_param_value(key, value)
    with pytest.raises((UserConfigError, FileReadError)):
        plugin.pre_execute()


def test_update_filepath(config, plugin, empty_temp_path):
    plugin._base_dir = Path("a/b")
    plugin._filename = "abc"
    plugin._config["filename"] = Path("a/b/abc")
    plugin.update_filepath()
    assert plugin._base_dir == empty_temp_path
    assert plugin._filename == _FILENAME
    assert plugin._config["filename"] == empty_temp_path / _FILENAME


@pytest.mark.parametrize("index", [0, 5, 100, 999])
def test_get_filename(config, plugin, empty_temp_path, index):
    assert plugin.get_filename(index) == empty_temp_path / _FILENAME


@pytest.mark.parametrize("frame_index", [0, 12, 24])
def test_get_frame(config, plugin, frame_index):
    _frame, _ = plugin.get_frame(frame_index)
    _scan_pos = plugin._SCAN.get_indices_from_ordinal(frame_index)
    _ref = config.dataset[*_scan_pos]
    assert _frame.data_unit == _ref.data_unit
    assert _frame.data_label == _ref.data_label
    for _ax in [0, 1]:
        assert _frame.axis_labels[_ax] == _ref.axis_labels[_ax]
        assert _frame.axis_units[_ax] == _ref.axis_units[_ax]
        assert np.allclose(_frame.axis_ranges[_ax], _ref.axis_ranges[_ax])
    assert np.allclose(_frame.array, _ref.array)


# ---------------------------------------------------------------------------
# Integration tests — InputPlugin base method contract
# ---------------------------------------------------------------------------


def test_execute__raises_without_pre_execute():
    """execute() must raise UserConfigError when pre_execute has not been called."""
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("NXdataResultLoader")()
    with pytest.raises(UserConfigError):
        plugin.execute(0)


@pytest.mark.parametrize("ordinal", [0, 7, 59])
def test_execute__w_single_frame(config, plugin, ordinal):
    _scan_pos = SCAN.get_indices_from_ordinal(ordinal)
    _data, _ = plugin.execute(ordinal)
    assert isinstance(_data, Dataset)
    assert np.allclose(_data.array, config.dataset[*_scan_pos].array)
    assert_dataset_equality__wo_data(config, _data)


@pytest.mark.parametrize("n_frames", [2, 3])
def test_execute__w_multi_frame__stack(config, plugin, n_frames):
    """Stack handling returns (n_frames, *data_shape)."""
    SCAN.set_param_value("scan_frames_per_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", n_frames)
    SCAN.set_param_value("scan_multi_frame_handling", "Stack")
    _data, _ = plugin.execute(0)
    assert _data.shape == (n_frames,) + config.data_shape
    assert _data.axis_labels[0] == "image number"
    assert_dataset_equality__wo_data(config, _data[0])


@pytest.mark.parametrize("n_frames", [2, 3])
@pytest.mark.parametrize(
    "param_value, func", [["Average", "mean"], ["Maximum", "max"], ["Sum", "sum"]]
)
def test_execute__multi_frame__1dim_output(config, plugin, n_frames, param_value, func):
    SCAN.set_param_value("scan_frames_per_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", n_frames)
    SCAN.set_param_value("scan_multi_frame_handling", param_value)
    _data, _ = plugin.execute(0)
    _ref = config.dataset[0, 0, 0:n_frames]
    _method = getattr(_ref, func)
    _expected = _method(axis=0)
    assert _data.shape == config.data_shape
    assert np.allclose(_data.array, _expected)
    assert_dataset_equality__wo_data(config, _data)


# ---------------------------------------------------------------------------
# read_multi_image — batch efficiency path
# ---------------------------------------------------------------------------


def test_read_multi_image__stack(config, plugin):
    SCAN.set_param_value("scan_multi_frame_handling", "Stack")
    _frame_indices = [4, 6, 7]
    _data, _ = plugin.read_multi_image(_frame_indices)
    assert _data.shape == (3,) + config.data_shape
    for _i, _fi in enumerate(_frame_indices):
        _scan_pos = SCAN.get_indices_from_ordinal(_fi)
        assert np.allclose(_data[_i], config.dataset[*_scan_pos].array, atol=1e-5)


@pytest.mark.parametrize(
    "param_value, func", [["Average", "mean"], ["Maximum", "max"], ["Sum", "sum"]]
)
def test_read_multi_image__1d_output(config, plugin, param_value, func):
    """Averaged batch result equals element-wise mean of requested frames."""
    SCAN.set_param_value("scan_multi_frame_handling", param_value)
    _frame_indices = [4, 6, 7]
    _scan_pos = [SCAN.get_indices_from_ordinal(_i) for _i in _frame_indices]
    _ref = np.array([config.dataset[*_pos] for _pos in _scan_pos])
    _method = getattr(_ref, func)
    _expected = _method(axis=0)
    _data, _kwargs = plugin.read_multi_image(_frame_indices)
    assert _data.shape == config.data_shape
    assert np.allclose(_data.array, _expected)
    assert_dataset_equality__wo_data(config, _data)
    assert _kwargs["frames"] == _frame_indices


# ---------------------------
# Non-conformant NXdata files
# ---------------------------


def test_pre_execute__no_axis_datasets(config, empty_temp_path, plugin):
    with h5py.File(empty_temp_path / _FILENAME, "r+") as _f:
        del _f["entry/test/axis_0"]
        del _f["entry/test/axis_1"]
        del _f["entry/test/axis_2"]
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


def test_pre_execute__no_nxdata_key(config, empty_temp_path, plugin):
    with h5py.File(empty_temp_path / _FILENAME, "r+") as _f:
        del _f["entry/test/"].attrs["NX_class"]
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


def test_pre_execute__axes_without_attributes(config, empty_temp_path, plugin):
    with h5py.File(empty_temp_path / _FILENAME, "r+") as _f:
        for _key in _f["entry/test/"].attrs:
            del _f["entry/test/"].attrs[_key]
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


if __name__ == "__main__":
    pytest.main([__file__])
