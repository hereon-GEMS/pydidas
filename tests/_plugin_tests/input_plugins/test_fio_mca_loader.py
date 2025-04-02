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

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest
from qtpy import QtCore

from pydidas.contexts import ScanContext
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


COLLECTION = LocalPluginCollection()
SCAN = ScanContext()


@pytest.fixture(scope="module")
def config():
    _config = type("Config", (object,), {})()
    _config._path = Path(tempfile.mkdtemp())
    _config._n_channels = 2048
    _config._n_files = 110
    _config._n = _config._n_files
    _config._header = (
        "!\n! Comments\n!\n%c\nPosition "
        + "{position:.2f}, Index {index:d}\n"
        + "!\n! Parameter\n%p\nSample_time = 5 \n!\n! Data \n%d\n"
        + " Col 1 dummy_spectrum FLOAT\n"
    )
    _config._data = np.repeat(
        np.arange(_config._n, dtype=np.uint16), _config._n_channels
    ).reshape((_config._n, _config._n_channels))
    _config._params = {}
    _config._global_fnames = {}
    _config._name_pattern = "test_12_mca_s#.fio"
    for _ifile in range(_config._n_files):
        _fname = _config._path.joinpath(
            _config._name_pattern.replace("#", str(_ifile + 1))
        )
        _config._global_fnames[_ifile] = _fname
        with open(_fname, "w") as _file:
            _file.write(_config._header.format(position=12 * _ifile, index=_ifile))
            _file.write("\n".join(str(val) for val in _config._data[_ifile]))
    yield _config
    shutil.rmtree(_config._path)
    qs = QtCore.QSettings("Hereon", "pydidas")
    qs.remove("unittesting")


@pytest.fixture
def setup_scan(config):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", config._name_pattern)
    SCAN.set_param_value("scan_base_directory", config._path)
    SCAN.set_param_value("scan_start_index", 1)
    yield
    SCAN.restore_all_defaults(True)


@pytest.fixture
def plugin(config):
    plugin = COLLECTION.get_plugin_by_name("FioMcaLoader")()
    for _key, _val in config._params.items():
        plugin.set_param_value(_key, _val)
    return plugin


def test_creation():
    plugin = COLLECTION.get_plugin_by_name("FioMcaLoader")()
    assert isinstance(plugin, BasePlugin)
    assert not plugin.get_param_value("live_processing")


def test_update_filename_string(setup_scan, plugin):
    plugin.update_filename_string()
    _fname = plugin.filename_string.format(index0=1)
    assert Path(_fname).is_file()


def test_determine_header_size(setup_scan, config, plugin):
    plugin.pre_execute()
    with open(plugin.get_filename(0), "r") as f:
        _n_header_lines = len(f.readlines()) - config._n_channels
    assert _n_header_lines == plugin._config["header_lines"]


def test_get_filename__start(setup_scan, config, plugin):
    plugin.update_filename_string()
    _name = plugin.get_filename(0)
    assert Path(_name) == config._global_fnames[0]


def test_determine_roi__no_roi(setup_scan, plugin):
    plugin.pre_execute()
    assert plugin._config["roi"] is None


def test_determine_roi__roi_no_abs_energy(setup_scan, plugin):
    plugin.set_param_value("use_roi", True)
    plugin.set_param_value("roi_xlow", 128)
    plugin.set_param_value("roi_xhigh", 256)
    plugin.pre_execute()
    assert plugin._config["roi"] == slice(128, 256)


def test_get_frame__no_x_scale(setup_scan, plugin):
    _i_image = 37
    plugin.pre_execute()
    _data, _ = plugin.get_frame(_i_image)
    assert np.all(_data == _i_image)
    assert np.allclose(_data.axis_ranges[0], np.arange(_data.size))


def test_get_frame__no_x_scale_w_roi(setup_scan, plugin):
    _i_image = 37
    plugin.set_param_value("use_roi", True)
    plugin.set_param_value("roi_xlow", 128)
    plugin.set_param_value("roi_xhigh", 256)
    plugin.pre_execute()
    _data, _ = plugin.get_frame(_i_image)
    assert np.all(_data == _i_image)
    assert np.allclose(_data.axis_ranges[0], np.arange(128, 256))


def test_get_frame__w_x_scale(setup_scan, plugin):
    _i_image = 42
    _delta = 2.5
    _offset = 150
    plugin.set_param_value("use_custom_xscale", True)
    plugin.set_param_value("x0_offset", _offset)
    plugin.set_param_value("x_delta", _delta)
    plugin.pre_execute()
    _data, _ = plugin.get_frame(_i_image)
    assert np.all(_data == _i_image)
    assert np.allclose(_data.axis_ranges[0], np.arange(_data.size) * _delta + _offset)


def test_get_frame__w_x_scale_and_roi(setup_scan, plugin):
    _i_image = 87
    _delta = 2.5
    _offset = 150
    plugin.set_param_value("use_custom_xscale", True)
    plugin.set_param_value("x0_offset", _offset)
    plugin.set_param_value("x_delta", _delta)
    plugin.set_param_value("use_roi", True)
    plugin.set_param_value("roi_xlow", 128)
    plugin.set_param_value("roi_xhigh", 256)
    plugin.pre_execute()
    _data, _ = plugin.get_frame(_i_image)
    assert np.all(_data == _i_image)
    assert np.allclose(_data.axis_ranges[0], np.arange(128, 256) * _delta + _offset)


if __name__ == "__main__":
    pytest.main()
