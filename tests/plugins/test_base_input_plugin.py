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

import os
import pickle
import shutil
import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.data_io import export_data, import_data
from pydidas.plugins import InputPlugin
from pydidas.unittest_objects import create_plugin_class


_DUMMY_SHAPE = (130, 140)

SCAN = ScanContext()


class TestInputPlugin(InputPlugin):
    def __init__(self, filename=""):
        InputPlugin.__init__(self)
        self.filename_string = str(filename)

    def get_frame(self, index, **kwargs):
        _frame = Dataset(np.zeros(_DUMMY_SHAPE, dtype=np.uint16) + index)
        kwargs["indices"] = (_frame,)
        return _frame, kwargs

    def read_frame(self, index, **kwargs):
        return import_data(self.filename_string, **kwargs)

    def update_filename_string(self):
        pass


@pytest.fixture(scope="module")
def temp_dir_w_file():
    """Fixture to create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    _fname = temp_dir / "test.h5"
    with h5py.File(_fname, "w") as f:
        f["entry/data/data"] = np.repeat(
            np.arange(30, dtype=np.uint16), np.prod(_DUMMY_SHAPE)
        ).reshape((30,) + _DUMMY_SHAPE)
    yield temp_dir
    shutil.rmtree(temp_dir)
    SCAN.restore_all_defaults(True)


@pytest.fixture
def reset_scan():
    SCAN.restore_all_defaults(True)


def test_is_basic_plugin__baseclass():
    for _plugin in [InputPlugin, InputPlugin()]:
        assert _plugin.is_basic_plugin()


def test_is_basic_plugin__subclass():
    class TestPlugin(InputPlugin):
        pass

    for _plugin in [TestPlugin, TestPlugin()]:
        assert not _plugin.is_basic_plugin()


def test_create_base_plugin():
    plugin = create_plugin_class(INPUT_PLUGIN)
    assert isinstance(plugin(), InputPlugin)


def test_class_attributes():
    plugin = create_plugin_class(INPUT_PLUGIN)
    for att in (
        "plugin_type",
        "plugin_name",
        "default_params",
        "generic_params",
        "input_data_dim",
        "output_data_dim",
    ):
        assert hasattr(plugin, att)


def test_class_generic_params():
    plugin = create_plugin_class(INPUT_PLUGIN)
    for att in (
        "use_roi",
        "roi_xlow",
        "roi_xhigh",
        "roi_ylow",
        "roi_yhigh",
        "binning",
    ):
        _param = plugin.generic_params.get_param(att)
        assert isinstance(_param, Parameter)


@pytest.mark.parametrize(
    "pattern", ["##test_###.tiff", "test_###0_##.tiff", "test_##_##_##.tiff"]
)
def test_update_filename_string__multiple_counters(reset_scan, pattern):
    SCAN.set_param_value("scan_name_pattern", pattern)
    plugin = InputPlugin()
    with pytest.raises(UserConfigError):
        plugin.update_filename_string()


@pytest.mark.parametrize(
    "pattern", ["test_1244.tiff", "test_0_22.npy", "test_22_ba_2.h5"]
)
def test_update_filename_string__no_counters(reset_scan, pattern):
    SCAN.set_param_value("scan_base_directory", "Test")
    SCAN.set_param_value("scan_name_pattern", pattern)
    plugin = InputPlugin()
    plugin.update_filename_string()
    assert plugin.filename_string == "Test" + os.sep + pattern


@pytest.mark.parametrize(
    "pattern", ["test_###.tiff", "test_######0_22.npy", "test_22_####_2.h5"]
)
def test_update_filename_string(reset_scan, pattern):
    SCAN.set_param_value("scan_base_directory", "Test")
    SCAN.set_param_value("scan_name_pattern", pattern)
    plugin = InputPlugin()
    plugin.update_filename_string()
    _nhash = pattern.count("#")
    _parts = pattern.split("#" * _nhash)
    _parts.insert(1, "{index:0" + str(_nhash) + "d}")
    assert plugin.filename_string == "Test" + os.sep + "".join(_parts)


@pytest.mark.parametrize("frame_index", [0, 1, 37])
@pytest.mark.parametrize("delta", [1, 3])
@pytest.mark.parametrize("offset", [0, 2, 5])
@pytest.mark.parametrize("images_per_file", [1, 11, 47])
def test_get_filename(offset, delta, frame_index, images_per_file, reset_scan):
    _input_fname = "test_name_{index:03d}.h5"
    SCAN.set_param_value("file_number_offset", offset)
    SCAN.set_param_value("file_number_delta", delta)
    plugin = TestInputPlugin(filename=_input_fname)
    plugin.set_param_value("_counted_images_per_file", images_per_file)
    _fname = plugin.get_filename(frame_index)
    _target_index = (frame_index // images_per_file) * delta + offset
    assert _fname == _input_fname.format(index=_target_index)


@pytest.mark.parametrize("ext", ["tif", "npy", "h5"])
def test_input_available__file_exists_and_readable(temp_dir_w_file, ext, reset_scan):
    _data = np.zeros((10, 10))
    _fname = temp_dir_w_file / f"test_dummy.{ext}"
    export_data(_fname, _data, overwrite=True)
    plugin = TestInputPlugin(filename=_fname)
    plugin.pre_execute()
    assert plugin.input_available(5)


@pytest.mark.parametrize("ext", ["tif", "npy", "h5"])
def test_input_available__file_exists_w_no_data(temp_dir_w_file, ext, reset_scan):
    _fname = temp_dir_w_file / f"test_empty_dummy.{ext}"
    with open(_fname, "wb") as f:
        f.write(b"")
    plugin = TestInputPlugin(filename=_fname)
    plugin.get_frame = plugin.read_frame
    plugin.pre_execute()
    assert not plugin.input_available(5)


def test_pickle():
    plugin = InputPlugin()
    _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
    for _key, _val in _new_params.items():
        plugin.add_param(Parameter(_key, str, _val))
    plugin2 = pickle.loads(pickle.dumps(plugin))
    for _key in plugin.params:
        assert plugin.get_param_value(_key) == plugin2.get_param_value(_key)


@pytest.mark.parametrize("ordinal", [0, 1, 37])
@pytest.mark.parametrize("multi_frame", ["Average", "Sum", "Maximum", "Stack"])
@pytest.mark.parametrize("i_per_point", [1, 4, 7])
def test_execute__single(reset_scan, ordinal, multi_frame, i_per_point):
    SCAN.set_param_value("scan_frames_per_scan_point", 1)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    plugin = TestInputPlugin()
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    assert _data.mean() == ordinal * i_per_point
    assert isinstance(_data, Dataset)


@pytest.mark.parametrize("ordinal", [0, 1, 37])
@pytest.mark.parametrize("multi_frame", ["Average", "Sum", "Maximum"])
@pytest.mark.parametrize("i_per_point", [1, 7, 13])
@pytest.mark.parametrize("n_frames", [2, 5, 11])
def test_execute__multiple_frames(
    reset_scan, ordinal, multi_frame, i_per_point, n_frames
):
    SCAN.set_param_value("scan_frames_per_scan_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    plugin = TestInputPlugin()
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    match multi_frame:
        case "Average":
            assert np.isclose(_data.mean(), ordinal * i_per_point + (n_frames - 1) / 2)
        case "Sum":
            assert _data.mean() == pytest.approx(
                ordinal * i_per_point * n_frames + sum(i for i in range(n_frames))
            )
        case "Maximum":
            assert _data.mean() == pytest.approx(ordinal * i_per_point + n_frames - 1)
        case _:
            raise ValueError(f"Unknown multi-frame handling: {multi_frame}")
    assert isinstance(_data, Dataset)


@pytest.mark.parametrize("ordinal", [0, 1, 37])
@pytest.mark.parametrize("i_per_point", [1, 7, 13])
@pytest.mark.parametrize("n_frames", [2, 5, 11])
def test_execute__multiple_frame_stack(reset_scan, ordinal, i_per_point, n_frames):
    SCAN.set_param_value("scan_frames_per_scan_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", "Stack")
    plugin = TestInputPlugin()
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    assert _data.shape == (n_frames, *_DUMMY_SHAPE)
    for _n in range(n_frames):
        assert _data[_n].mean() == ordinal * i_per_point + _n
    assert isinstance(_data, Dataset)


def test_copy():
    plugin = TestInputPlugin()
    copy = plugin.copy()
    assert plugin._SCAN == SCAN
    assert copy._SCAN == SCAN


if __name__ == "__main__":
    unittest.main()
