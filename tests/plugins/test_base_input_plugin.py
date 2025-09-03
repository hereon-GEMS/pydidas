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

import pickle
import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.data_io import export_data, import_data
from pydidas.plugins import InputPlugin
from pydidas.unittest_objects import create_plugin_class


_DUMMY_SHAPE = (130, 140)
_DUMMY_SHAPE_1d = (145,)

SCAN = ScanContext()


class TestInputPlugin(InputPlugin):
    output_data_label = "Test data"
    output_data_unit = "some counts"

    def __init__(self, filename="", ndim=2):
        self.base_output_data_dim = ndim
        InputPlugin.__init__(self)
        self.filename_string = str(filename)

    def get_frame(self, index, **kwargs):
        _shape = _DUMMY_SHAPE if self.base_output_data_dim == 2 else _DUMMY_SHAPE_1d
        _frame = Dataset(
            np.zeros(_shape, dtype=np.uint16) + index,
            axis_labels=["det y", "det x"] if self.base_output_data_dim == 2 else ["x"],
            axis_units=["px", "px"] if self.base_output_data_dim == 2 else ["channels"],
            data_unit=self.output_data_unit,
            data_label=self.output_data_label,
        )
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


@pytest.mark.parametrize("base_output_data_dim", [1, 2])
def test__init__correct_params(base_output_data_dim):
    plugin_class = create_plugin_class(INPUT_PLUGIN)
    plugin_class.base_output_data_dim = base_output_data_dim
    plugin = plugin_class()
    for att in (
        "use_roi",
        "roi_xlow",
        "roi_xhigh",
        "binning",
    ):
        assert isinstance(plugin.get_param(att), Parameter)
    if base_output_data_dim == 2:
        assert isinstance(plugin.get_param("roi_ylow"), Parameter)
        assert isinstance(plugin.get_param("roi_yhigh"), Parameter)


@pytest.mark.parametrize("base_dim", [1, 2, 3])
@pytest.mark.parametrize("n_frames", [1, 3, 4])
@pytest.mark.parametrize("multi_frame", ["Average", "Sum", "Maximum", "Stack"])
def test_output_data_dim(reset_scan, base_dim, n_frames, multi_frame):
    plugin = create_plugin_class(INPUT_PLUGIN)()
    plugin.base_output_data_dim = base_dim
    SCAN.set_param_value("scan_frames_per_point", n_frames)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    _expected_dim = base_dim
    if n_frames > 1 and multi_frame == "Stack":
        _expected_dim += 1
    assert plugin.output_data_dim == _expected_dim


@pytest.mark.parametrize(
    "pattern",
    ["test_1244.tiff", "test_0_22.npy", "test_###.tiff", "test_######0_22.npy"],
)
@pytest.mark.parametrize("directory", [Path(__file__).parent, None])
def test_update_filename_string__valid_pattern(
    reset_scan, pattern, directory, temp_dir_w_file
):
    _dir = directory or temp_dir_w_file
    SCAN.set_param_value("scan_base_directory", _dir)
    SCAN.set_param_value("scan_name_pattern", pattern)
    plugin = InputPlugin()
    plugin.update_filename_string()
    _target = str(_dir / pattern)
    if "#" in pattern:
        _target = _target.replace(
            "#" * pattern.count("#"), "{index:0" + str(pattern.count("#")) + "d}"
        )
    assert plugin.filename_string == _target


@pytest.mark.parametrize("frame_index", [0, 1, 37])
@pytest.mark.parametrize("delta", [1, 3])
@pytest.mark.parametrize("offset", [0, 2, 5])
@pytest.mark.parametrize("images_per_file", [1, 11, 47])
def test_get_filename(offset, delta, frame_index, images_per_file, reset_scan):
    _input_fname = "test_name_{index:03d}.h5"
    SCAN.set_param_value("pattern_number_offset", offset)
    SCAN.set_param_value("pattern_number_delta", delta)
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
@pytest.mark.parametrize("output_dim", [1, 2])
def test_execute__single(reset_scan, ordinal, multi_frame, i_per_point, output_dim):
    SCAN.set_param_value("scan_frames_per_point", 1)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    plugin = TestInputPlugin(ndim=output_dim)
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    assert _data.shape == (_DUMMY_SHAPE if output_dim == 2 else _DUMMY_SHAPE_1d)
    assert _data.mean() == ordinal * i_per_point
    assert isinstance(_data, Dataset)


@pytest.mark.parametrize("ordinal", [0, 1, 37])
@pytest.mark.parametrize("multi_frame", ["Average", "Sum", "Maximum"])
@pytest.mark.parametrize("i_per_point", [1, 7, 13])
@pytest.mark.parametrize("n_frames", [2, 5, 11])
@pytest.mark.parametrize("output_dim", [1, 2])
def test_execute__multiple_frames(
    reset_scan, ordinal, multi_frame, i_per_point, n_frames, output_dim
):
    SCAN.set_param_value("scan_frames_per_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", multi_frame)
    plugin = TestInputPlugin(ndim=output_dim)
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    _ref = plugin.get_frame(ordinal)[0].property_dict
    assert _data.shape == (_DUMMY_SHAPE if output_dim == 2 else _DUMMY_SHAPE_1d)
    for _key in ["data_label", "data_unit", "axis_labels", "axis_units"]:
        assert getattr(_data, _key) == _ref[_key]
    assert all(
        np.allclose(_data.axis_ranges[i], _ref["axis_ranges"][i])
        for i in range(output_dim)
    )
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
@pytest.mark.parametrize("output_dim", [1, 2])
def test_execute__multiple_frame_stack(
    reset_scan, ordinal, i_per_point, n_frames, output_dim
):
    SCAN.set_param_value("scan_frames_per_point", n_frames)
    SCAN.set_param_value("frame_indices_per_scan_point", i_per_point)
    SCAN.set_param_value("scan_multi_frame_handling", "Stack")
    plugin = TestInputPlugin(ndim=output_dim)
    plugin.pre_execute()
    _data, _ = plugin.execute(ordinal)
    _ref = plugin.get_frame(ordinal)[0].property_dict
    assert _data.shape == (n_frames,) + (
        _DUMMY_SHAPE if output_dim == 2 else _DUMMY_SHAPE_1d
    )
    _ref = plugin.get_frame(ordinal)[0].property_dict
    assert list(_data.axis_labels.values()) == ["image number"] + list(
        _ref["axis_labels"].values()
    )
    assert list(_data.axis_units.values()) == [""] + list(_ref["axis_units"].values())
    assert all(
        np.allclose(_data.axis_ranges[i + 1], _ref["axis_ranges"][i])
        for i in range(output_dim)
    )
    for _n in range(n_frames):
        assert _data[_n].mean() == ordinal * i_per_point + _n
    assert isinstance(_data, Dataset)


def test_copy():
    plugin = TestInputPlugin()
    copy = plugin.copy()
    assert plugin._SCAN == SCAN
    assert copy._SCAN == SCAN


if __name__ == "__main__":
    pytest.main()
