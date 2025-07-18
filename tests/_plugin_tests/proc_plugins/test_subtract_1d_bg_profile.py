# This file is part of pydidas.
#
# Copyright 025, Helmholtz-Zentrum Hereon
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

"""
Tests for the Subtract1dBackgroundProfile plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from pydidas_plugins.proc_plugins.subtract_1d_bg_profile import (
    Subtract1dBackgroundProfile,
)

from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import ProcPlugin


_PROFILE = np.zeros((200,))
for _i in range(0, 200, 10):
    _PROFILE[_i : _i + 10] = _i


@pytest.fixture(scope="module")
def temp_path():
    _path = Path(tempfile.mkdtemp())
    yield _path
    shutil.rmtree(_path)


def get_profile_file(temp_path, dtype) -> Path:
    profile_file = temp_path / "profile.npy"
    np.save(profile_file, _PROFILE.astype(dtype))
    return profile_file


def test_init():
    plugin = Subtract1dBackgroundProfile()
    assert isinstance(plugin, ProcPlugin)
    assert plugin._thresh is None
    assert plugin._profile is None
    assert plugin._profile_cast is None


@pytest.mark.parametrize("profile_dtype", [float, np.float32, int, np.uint32])
@pytest.mark.parametrize("multiplicator", [0.1, 1.0, 1, 2.5, 4])
@pytest.mark.parametrize("threshold", [None, np.inf, np.nan, -1, 0, 1.5])
def test_pre_execute(temp_path, profile_dtype, multiplicator, threshold):
    plugin = Subtract1dBackgroundProfile()
    profile_file = get_profile_file(temp_path, profile_dtype)
    plugin.set_param_value("profile_file", profile_file)
    plugin.set_param_value("multiplicator", multiplicator)
    plugin.set_param_value("threshold_low", threshold)
    plugin.pre_execute()

    assert np.allclose(plugin._profile, multiplicator * _PROFILE)
    if threshold in [None, np.inf, np.nan]:
        assert plugin._thresh is None
    else:
        assert plugin._thresh == threshold


@pytest.mark.parametrize("profile_dtype", [float, np.float32, int, np.uint32])
@pytest.mark.parametrize("data_dtype", [np.float64, np.uint16, np.int32])
@pytest.mark.parametrize("multiplicator", [0.1, 1.0, 2.5])
@pytest.mark.parametrize("threshold", [None, -1, 0, 1.5])
def test_execute(temp_path, profile_dtype, data_dtype, multiplicator, threshold):
    plugin = Subtract1dBackgroundProfile()
    profile_file = get_profile_file(temp_path, profile_dtype)
    plugin.set_param_value("profile_file", profile_file)
    plugin.set_param_value("multiplicator", multiplicator)
    plugin.set_param_value("threshold_low", threshold)
    plugin.pre_execute()
    _data = Dataset(np.arange(200, dtype=data_dtype)) * 200
    _res, _kws = plugin.execute(_data)
    _ref = _data - multiplicator * _PROFILE
    if threshold is not None:
        _ref = np.where(_ref < threshold, threshold, _ref)
    assert np.allclose(_res, _ref)


@pytest.mark.parametrize("ax", [-2, -1, 0, 1, 2])
def test_execute__w_3d_data(temp_path, ax):
    plugin = Subtract1dBackgroundProfile()
    profile_file = get_profile_file(temp_path, float)
    plugin.set_param_value("profile_file", profile_file)
    plugin.set_param_value("process_data_dim", ax)
    plugin.pre_execute()
    ax = ax % 3  # Ensure ax is within the range of 0 to 2
    _data = Dataset(np.arange(2000, dtype=float))
    _data.shape = (5, 2)[:ax] + (-1,) + (5, 2)[ax:]
    _res, _kws = plugin.execute(_data)
    _profile_ref = _PROFILE.copy()
    _profile_ref.shape = (1,) * ax + (-1,) + (1,) * (2 - ax)
    _ref = _data - _profile_ref
    assert np.allclose(plugin._profile_cast, _profile_ref)
    assert np.allclose(_res, _ref)


def test_execute__w_3d_data_and_invalid_shape(temp_path):
    plugin = Subtract1dBackgroundProfile()
    profile_file = get_profile_file(temp_path, float)
    plugin.set_param_value("profile_file", profile_file)
    plugin.set_param_value("process_data_dim", 1)
    _data = Dataset(np.arange(2000, dtype=float)).reshape(10, 20, 10)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin.execute(_data)


if __name__ == "__main__":
    pytest.main()
