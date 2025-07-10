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
from pydidas.core import Parameter, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()
SCAN = ScanContext()

_SHAPE = (10, 15)
_N_PER_FILE = 13
_N_FILES = 11
_DATA_SHAPE = (_N_PER_FILE,) + _SHAPE


@pytest.fixture(scope="module")
def config():
    _config = type("Config", (object,), {})()
    _config.path = Path(tempfile.mkdtemp())
    _config.data = np.repeat(
        np.arange(_N_PER_FILE * _N_FILES, dtype=np.uint16), np.prod(_SHAPE)
    ).reshape((_N_PER_FILE * _N_FILES,) + _SHAPE)

    _config._hdf5_fnames = []
    for i in range(_N_FILES):
        _fname = _config.path / f"test_{i:05d}.h5"
        _slice = slice(i * _N_PER_FILE, (i + 1) * _N_PER_FILE, 1)
        with h5py.File(_fname, "w") as f:
            f["/entry/data/data"] = _config.data[_slice]
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", "test_#####.h5")
    SCAN.set_param_value("scan_base_directory", _config.path)
    yield _config
    shutil.rmtree(_config.path)


@pytest.fixture
def plugin():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    plugin.set_param_value("images_per_file", _N_PER_FILE)
    plugin.set_param_value("hdf5_key", "/entry/data/data")
    return plugin


def test_creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input(config):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
    plugin.pre_execute()
    assert "dataset" in plugin._standard_kwargs.keys()
    assert "binning" in plugin._standard_kwargs.keys()


@pytest.mark.parametrize("slice_ax", [0, 1, 2])
@pytest.mark.parametrize("index", [0, 3, 7])
@pytest.mark.parametrize("n_per_file", [-1, None])
def test_pre_execute(config, plugin, slice_ax, index, n_per_file):
    plugin.set_param_value("hdf5_slicing_axis", slice_ax)
    plugin.set_param_value("images_per_file", n_per_file or _DATA_SHAPE[slice_ax])
    plugin.pre_execute()
    assert plugin.get_param_value("_counted_images_per_file") == _DATA_SHAPE[slice_ax]
    assert plugin._index_func(index) == (None,) * slice_ax + (index,)
    assert "dataset" in plugin._standard_kwargs.keys()
    assert "binning" in plugin._standard_kwargs.keys()


@pytest.mark.parametrize("index", [0, 3, 7])
@pytest.mark.parametrize("n_per_file", [-1, None])
def test_pre_execute__w_none_slice_ax(config, plugin, index, n_per_file):
    plugin.set_param_value("hdf5_slicing_axis", None)
    plugin.set_param_value("images_per_file", n_per_file or _DATA_SHAPE[0])
    plugin.pre_execute()
    assert plugin.get_param_value("_counted_images_per_file") == 1
    assert plugin._index_func(index) is None
    assert "dataset" in plugin._standard_kwargs.keys()
    assert "binning" in plugin._standard_kwargs.keys()


@pytest.mark.parametrize("slice_ax", [0, 1, 2])
@pytest.mark.parametrize("frame_index", [0, 7, 27, 76])
@pytest.mark.parametrize("n_per_file", [-1, None])
def test_get_frame(config, plugin, slice_ax, frame_index, n_per_file):
    plugin.set_param_value("hdf5_slicing_axis", slice_ax)
    plugin.set_param_value("images_per_file", n_per_file or _DATA_SHAPE[slice_ax])
    plugin.pre_execute()
    _data, kwargs = plugin.execute(frame_index)
    _n_start = _N_PER_FILE * (frame_index // _DATA_SHAPE[slice_ax])
    match slice_ax:
        case 0:
            _slicing = (frame_index,)
        case 1:
            _slicing = (
                slice(_n_start, _n_start + _DATA_SHAPE[0]),
                frame_index % _DATA_SHAPE[1],
            )
        case 2:
            _slicing = (
                slice(_n_start, _n_start + _DATA_SHAPE[0]),
                slice(None),
                frame_index % _DATA_SHAPE[2],
            )
        case _:
            raise UserConfigError(f"Invalid slicing axis: {slice_ax}")
    assert plugin.get_param_value("_counted_images_per_file") == _DATA_SHAPE[slice_ax]
    assert _data.shape == config.data[_slicing].shape
    assert np.allclose(_data, config.data[_slicing])
    assert kwargs["indices"] == (None,) * (slice_ax) + (
        frame_index % _DATA_SHAPE[slice_ax],
    )
    assert (
        _data.metadata["indices"]
        == "[" + ":, " * slice_ax + f"{frame_index % _DATA_SHAPE[slice_ax]}]"
    )


def test_get_frame__wrong_dim(config, plugin):
    plugin.set_param_value("hdf5_slicing_axis", None)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin.get_frame(0)


@pytest.mark.parametrize("roi", [[0, 5, 0, None], [1, 5, 1, 5], [None, None, 2, 7]])
def test__integration__execute_with_roi(config, plugin, roi):
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
    assert kwargs["indices"] == (_index % _N_PER_FILE,)
    assert _data.metadata["indices"] == f"[{_index % _N_PER_FILE}]"
    assert _roi == (slice(roi[0], roi[1]), slice(roi[2], roi[3]))
    assert (
        _data.shape
        == config.data[0, slice(roi[0], roi[1]), slice(roi[2], roi[3])].shape
    )


def test_pickle(config, plugin):
    _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
    for _key, _val in _new_params.items():
        plugin.add_param(Parameter(_key, str, _val))
    plugin2 = pickle.loads(pickle.dumps(plugin))
    for _key in plugin.params:
        assert plugin.get_param_value(_key) == plugin2.get_param_value(_key)


if __name__ == "__main__":
    pytest.main()
