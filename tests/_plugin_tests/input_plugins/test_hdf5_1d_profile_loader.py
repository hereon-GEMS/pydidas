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

import os
import pickle
import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()
SCAN = ScanContext()


@pytest.fixture(scope="module")
def config():
    _config = type("Config", (object,), {})()
    _config._path = tempfile.mkdtemp()
    _config._size = 42
    _config._n_per_file = 13
    _config._n_files = 11
    _config._fname_i0 = 2
    _config._n = _config._n_files * _config._n_per_file
    _config._hdf5key = "/entry/data/data"
    _config._data = np.repeat(
        np.arange(_config._n, dtype=np.uint16), _config._size
    ).reshape((_config._n, _config._size))

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
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    plugin.set_param_value("profiles_per_file", config._n_per_file)
    plugin.set_param_value("hdf5_key", config._hdf5key)
    return plugin


def get_index_in_file(config, index):
    return index % config._n_per_file


def test_creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input(setup_scan):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    plugin.pre_execute()
    assert "dataset" in plugin._standard_kwargs.keys()
    assert "binning" in plugin._standard_kwargs.keys()
    assert plugin._standard_kwargs["forced_dimension"] == 1
    assert not plugin._standard_kwargs["import_pydidas_metadata"]
    assert plugin._config["xrange"] is None


@pytest.mark.parametrize("index", [0, 5, 12, 37, 55])
def test_get_filename(config, setup_scan, plugin, index):
    plugin.pre_execute()
    _fname = Path(plugin.get_filename(index))
    _target_i = index // config._n_per_file
    _target_fname = config._hdf5_fnames[_target_i]
    assert _fname == _target_fname


@pytest.mark.parametrize("index", [0, 5, 12, 37, 55])
def test_get_frame(config, setup_scan, plugin, index):
    plugin.pre_execute()
    _data, _kwargs = plugin.get_frame(index)
    assert isinstance(_data, Dataset)
    assert _data.shape == (config._size,)
    assert _data.mean() == index


def test_pickle(config, setup_scan, plugin):
    _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
    for _key, _val in _new_params.items():
        plugin.add_param(Parameter(_key, str, _val))
    plugin2 = pickle.loads(pickle.dumps(plugin))
    for _key in plugin.params:
        assert plugin.get_param_value(_key) == plugin2.get_param_value(_key)


if __name__ == "__main__":
    pytest.main()
