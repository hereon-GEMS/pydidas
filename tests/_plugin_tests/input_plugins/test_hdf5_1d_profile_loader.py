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

import pickle
import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()
SCAN = ScanContext()
_N_PER_FILE = 13
_N_FILES = 11
_N_TOTAL = _N_FILES * _N_PER_FILE
_N_DATAPOINTS = 42
_DATA_SHAPE = (_N_PER_FILE, _N_DATAPOINTS)


@pytest.fixture(scope="module")
def config():
    _config = type("Config", (object,), {})()
    _config.path = Path(tempfile.mkdtemp())
    _N_DATAPOINTS = 42
    _config.data = np.repeat(
        np.arange(_N_TOTAL, dtype=np.uint16), _N_DATAPOINTS
    ).reshape((_N_TOTAL, _N_DATAPOINTS))

    _config._hdf5_fnames = []
    for i in range(_N_FILES):
        _fname = _config.path / f"test_{i:05d}.h5"
        _config._hdf5_fnames.append(_fname)
        _slice = slice(i * _N_PER_FILE, (i + 1) * _N_PER_FILE, 1)
        with h5py.File(_fname, "w") as f:
            f["/entry/data/data"] = _config.data[_slice]
    yield _config
    shutil.rmtree(_config.path)


@pytest.fixture
def setup_scan(config):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", "test_#####.h5")
    SCAN.set_param_value("scan_base_directory", config.path)


@pytest.fixture
def plugin(config):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    plugin.set_param_value("images_per_file", _N_PER_FILE)
    plugin.set_param_value("hdf5_key", "/entry/data/data")
    return plugin


def test__creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    assert plugin.base_output_data_dim == 1
    assert plugin.has_unique_parameter_config_widget
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input(setup_scan):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf51dProfileLoader")()
    plugin.pre_execute()
    assert "dataset" in plugin._standard_kwargs
    assert "binning" in plugin._standard_kwargs
    assert plugin._standard_kwargs["forced_dimension"] == 1
    assert not plugin._standard_kwargs["import_pydidas_metadata"]
    assert plugin._config["xrange"] is None


@pytest.mark.parametrize("frame_index", [0, 5, 12, 37, 55])
def test_get_frame(config, setup_scan, plugin, frame_index):
    plugin.pre_execute()
    _data, _kwargs = plugin.get_frame(frame_index)
    assert isinstance(_data, Dataset)
    assert _data.shape == (_N_DATAPOINTS,)
    assert _data.mean() == frame_index


def test_pickle(config, setup_scan, plugin):
    _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
    for _key, _val in _new_params.items():
        plugin.add_param(Parameter(_key, str, _val))
    plugin2 = pickle.loads(pickle.dumps(plugin))
    for _key in plugin.params:
        assert plugin.get_param_value(_key) == plugin2.get_param_value(_key)


@pytest.mark.parametrize("slice_ax", [0, 1])
@pytest.mark.parametrize("frame_index", [0, 5, 12, 55])
@pytest.mark.parametrize("n_per_file", [-1, 8])
def test__integration_execute(
    config, setup_scan, plugin, slice_ax, frame_index, n_per_file
):
    plugin.set_param_value("hdf5_slicing_axis", slice_ax)
    plugin.set_param_value("images_per_file", n_per_file)
    plugin.pre_execute()
    _data, _kwargs = plugin.execute(frame_index)
    _n_expected = _DATA_SHAPE[slice_ax] if n_per_file == -1 else n_per_file
    _n_start = _N_PER_FILE * (frame_index // _n_expected)
    match slice_ax:
        case 0:
            _slicing = (_n_start + frame_index % _n_expected,)
        case 1:
            _slicing = (
                slice(_n_start, _n_start + _DATA_SHAPE[0]),
                frame_index % _DATA_SHAPE[slice_ax],
            )
        case _:
            raise UserConfigError(f"Invalid slicing axis: {slice_ax}")
    assert plugin.get_param_value("_counted_images_per_file") == _n_expected
    assert _data.shape == config.data[_slicing].shape
    assert np.allclose(_data, config.data[_slicing])


if __name__ == "__main__":
    pytest.main()
