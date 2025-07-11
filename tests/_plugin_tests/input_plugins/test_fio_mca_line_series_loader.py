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

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import FileReadError, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


COLLECTION = LocalPluginCollection()

SCAN = ScanContext()

_N_CHANNELS = 2048
_N_DIRS = 13
_N_FILES = 11
_N = _N_FILES * _N_DIRS
_NAME_PATTERN = "test_#####"


@pytest.fixture(scope="module")
def temp_dir_w_files():
    _path = Path(tempfile.mkdtemp())
    _header = (
        "!\n! Comments\n!\n%c\nPosition "
        + "{position:.2f}, Index {index:d}\n"
        + "!\n! Parameter\n%p\nSample_time = 5 \n!\n! Data \n%d\n"
        + " Col 1 dummy_spectrum FLOAT\n"
    )
    _data = np.repeat(np.arange(_N, dtype=np.uint16), _N_CHANNELS).reshape(
        (_N, _N_CHANNELS)
    )
    _fnames = {}
    for _i in range(_N_DIRS):
        _tmpname = _NAME_PATTERN.replace("#####", f"{1 + _i:05d}")
        _dir = _path.joinpath(_tmpname)
        _dir.mkdir()
        for _ifile in range(_N_FILES):
            _fname = _dir.joinpath(f"{_tmpname}_mca_s{_ifile + 1}.fio")
            _global_index = _ifile + _i * _N_FILES
            _fnames[_global_index] = _fname
            with open(_fname, "w") as _file:
                _file.write(_header.format(position=12 * _ifile, index=_ifile))
                _file.write("\n".join(str(val) for val in _data[_global_index]))
    yield _path, _fnames
    shutil.rmtree(_path)


@pytest.fixture
def set_up_scan(temp_dir_w_files):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", _NAME_PATTERN)
    SCAN.set_param_value("scan_base_directory", temp_dir_w_files[0])
    SCAN.set_param_value("pattern_number_offset", 1)


@pytest.fixture
def plugin(set_up_scan):
    plugin = COLLECTION.get_plugin_by_name("FioMcaLineScanSeriesLoader")()
    plugin.set_param_value("files_per_directory", -1)
    plugin.set_param_value("use_custom_xscale", False)
    return plugin


def test__creation():
    plugin = COLLECTION.get_plugin_by_name("FioMcaLineScanSeriesLoader")()
    assert isinstance(plugin, BasePlugin)


@pytest.mark.parametrize("fio_suffix", ["_mca_s#.fio", "_s#.fio", "_mca_s#"])
@pytest.mark.parametrize("pattern", ["name_#####", "spam_###_ham", "eggs_#_bacon"])
@pytest.mark.parametrize("i0", [1, 3])
@pytest.mark.parametrize("i1", [5, 17])
def test_update_filename_string(temp_dir_w_files, fio_suffix, pattern, plugin, i0, i1):
    SCAN.set_param_value("scan_name_pattern", pattern)
    plugin.set_param_value("fio_suffix", fio_suffix)
    plugin.update_filename_string()
    _fname = plugin.filename_string.format(index0=i0, index1=i1)
    _nhash = pattern.count("#")
    assert _fname == str(
        temp_dir_w_files[0]
        / pattern.replace("#" * _nhash, "{index0:0" + str(_nhash) + "d}")
        / (
            pattern.replace("#" * _nhash, "{index0:0" + str(_nhash) + "d}")
            + fio_suffix.replace("#", "{index1:d}")
        )
    ).format(index0=i0, index1=i1)


@pytest.mark.parametrize("n_files", [-1, 1, 7])
def test_check_files_per_directory(temp_dir_w_files, plugin, n_files):
    plugin.set_param_value("files_per_directory", n_files)
    plugin.update_filename_string()
    plugin._check_files_per_directory()
    assert plugin.get_param_value("_counted_files_per_directory") == (
        n_files if n_files > 0 else _N_FILES
    )


def test_check_files_per_directory__no_dir(temp_dir_w_files, plugin):
    plugin._SCAN.set_param_value("scan_base_directory", temp_dir_w_files[0] / "test123")
    plugin.update_filename_string()
    with pytest.raises(UserConfigError):
        plugin._check_files_per_directory()


def test_check_files_per_directory__empty_dir(temp_dir_w_files, plugin):
    temp_dir_w_files[0].joinpath("empty_dir").mkdir()
    plugin._SCAN.set_param_value(
        "scan_base_directory", temp_dir_w_files[0] / "empty_dir"
    )
    plugin.update_filename_string()
    with pytest.raises(UserConfigError):
        plugin._check_files_per_directory()


@pytest.mark.parametrize("n_files", [5, 7, 11])
@pytest.mark.parametrize("frame_index", [0, 2, 39, 117])
def test_get_filename(plugin, n_files, frame_index):
    plugin.set_param_value("files_per_directory", n_files)
    plugin.update_filename_string()
    plugin._check_files_per_directory()
    _expected_i0 = frame_index // n_files + 1
    _expected_i1 = frame_index % n_files + 1
    assert plugin.get_filename(frame_index) == plugin.filename_string.format(
        index0=_expected_i0, index1=_expected_i1
    )


def test_get_frame__no_file(plugin):
    plugin.set_param_value("fio_suffix", "_something_s#.fio")
    plugin.update_filename_string()
    with pytest.raises(FileReadError):
        _data, _ = plugin.get_frame(37)


@pytest.mark.parametrize("use_roi", [True, False])
@pytest.mark.parametrize("custom_xscale", [True, False])
def test_get_frame(plugin, use_roi, custom_xscale):
    _delta = 2.5
    _offset = 150
    plugin.set_param_value("roi_xlow", 128)
    plugin.set_param_value("roi_xhigh", 256)
    plugin.set_param_value("x0_offset", _offset)
    plugin.set_param_value("x_delta", _delta)
    plugin.set_param_value("use_roi", use_roi)
    plugin.set_param_value("use_custom_xscale", custom_xscale)
    _i_image = 37
    plugin.pre_execute()
    _data, _ = plugin.get_frame(_i_image)
    _range_ref = np.arange(128, 256) if use_roi else np.arange(_N_CHANNELS)
    if custom_xscale:
        _range_ref = _range_ref * _delta + _offset
    assert np.all(_data == _i_image)
    assert np.allclose(_data.axis_ranges[0], _range_ref)


if __name__ == "__main__":
    pytest.main()
