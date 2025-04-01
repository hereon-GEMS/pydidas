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
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Parameter, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()
SCAN = ScanContext()


@pytest.fixture(scope="module")
def config():
    _config = type("Config", (object,), {})()
    _config._path = tempfile.mkdtemp()
    _config._img_shape = (10, 10)
    _config._n_per_file = 13
    _config._n_files = 11
    _config._fname_i0 = 2
    _config._n = _config._n_files * _config._n_per_file
    _config._hdf5key = "/entry/data/data"
    _config._data = np.repeat(
        np.arange(_config._n, dtype=np.uint16), np.prod(_config._img_shape)
    ).reshape((_config._n,) + _config._img_shape)

    _config._hdf5_fnames = []
    for i in range(_config._n_files):
        _fname = Path(
            os.path.join(_config._path, f"test_{i + _config._fname_i0:05d}.h5")
        )
        _config._hdf5_fnames.append(_fname)
        _slice = slice(i * _config._n_per_file, (i + 1) * _config._n_per_file, 1)
        with h5py.File(_fname, "w") as f:
            f[_config._hdf5key] = _config._data[_slice]
    yield _config
    shutil.rmtree(_config._path)


@pytest.fixture
def setup_scan(config):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", "test_#####.h5")
    SCAN.set_param_value("scan_base_directory", config._path)
    SCAN.set_param_value("scan_start_index", config._fname_i0)


@pytest.fixture
def plugin(config):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    plugin.set_param_value("images_per_file", config._n_per_file)
    plugin.set_param_value("hdf5_key", config._hdf5key)
    return plugin


def get_index_in_file(config, index):
    return index % config._n_per_file


def test_creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input(setup_scan):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    plugin.pre_execute()
    assert "dataset" in plugin._standard_kwargs.keys()
    assert "binning" in plugin._standard_kwargs.keys()


def test_pre_execute__no_images_per_file_set(config, setup_scan, plugin):
    plugin.set_param_value("images_per_file", -1)
    plugin.pre_execute()
    assert plugin.get_param_value("_counted_images_per_file") == config._n_per_file


def test_execute__no_input(plugin):
    with pytest.raises(UserConfigError):
        plugin.execute(0)


def test_execute__simple(config, setup_scan, plugin):
    _index = 0
    plugin.pre_execute()
    _data, kwargs = plugin.execute(_index)
    assert (_data == _index).all()
    assert kwargs["indices"] == (get_index_in_file(config, _index),)
    assert _data.metadata["indices"] == f"[{get_index_in_file(config, _index)}]"


def test_execute__slicing_ax_1(config, setup_scan, plugin):
    plugin.set_param_value("hdf5_slicing_axis", 1)
    _index = 0
    plugin.pre_execute()
    _data, kwargs = plugin.execute(_index)
    assert np.allclose(_data, config._data[: config._n_per_file, _index])
    assert kwargs["indices"] == (None, get_index_in_file(config, _index))
    assert _data.metadata["indices"] == f"[:, {get_index_in_file(config, _index)}]"


@pytest.mark.parametrize("roi", [[0, 5, 0, None], [1, 5, 1, 5]])
def test_execute__with_roi(config, setup_scan, plugin, roi):
    plugin.set_param_value("use_roi", True)
    plugin.set_param_value("roi_ylow", roi[0])
    plugin.set_param_value("roi_yhigh", roi[1])
    plugin.set_param_value("roi_xlow", roi[2])
    plugin.set_param_value("roi_xhigh", roi[3])
    _index = 0
    plugin.pre_execute()
    _data, kwargs = plugin.execute(_index)
    _roi = plugin._get_own_roi()
    assert (_data == _index).all()
    assert kwargs["indices"] == (get_index_in_file(config, _index),)
    assert _data.metadata["indices"] == f"[{get_index_in_file(config, _index)}]"
    assert _roi == (slice(roi[0], roi[1]), slice(roi[2], roi[3]))
    for _dim in [0, 1]:
        if _roi[_dim] == slice(0, None):
            assert _data.shape[_dim] == config._img_shape[_dim]
        else:
            assert _data.shape[_dim] == _roi[_dim].stop - _roi[_dim].start


def test_get_frame__wrong_dim(config, setup_scan, plugin):
    plugin.set_param_value("hdf5_slicing_axis", None)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin.execute(0)


def test_execute__get_all_frames(config, setup_scan, plugin):
    plugin.pre_execute()
    for _index in range(config._n):
        _data, kwargs = plugin.execute(_index)
        assert (_data == _index).all()
        assert kwargs["indices"] == (get_index_in_file(config, _index),)
        assert _data.metadata["indices"] == f"[{get_index_in_file(config, _index)}]"


def test_pickle(config, setup_scan, plugin):
    _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
    for _key, _val in _new_params.items():
        plugin.add_param(Parameter(_key, str, _val))
    plugin2 = pickle.loads(pickle.dumps(plugin))
    for _key in plugin.params:
        assert plugin.get_param_value(_key) == plugin2.get_param_value(_key)


if __name__ == "__main__":
    pytest.main()
