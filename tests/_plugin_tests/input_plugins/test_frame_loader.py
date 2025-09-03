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
import unittest
import warnings
from pathlib import Path

import numpy as np
import pytest
import skimage
from qtpy import QtCore

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()

SCAN = ScanContext()
_IMG_SHAPE = (11, 13)
_N = 50
_DATA = np.repeat(np.arange(_N, dtype=np.uint16), np.prod(_IMG_SHAPE)).reshape(
    _N, *_IMG_SHAPE
)


@pytest.fixture(scope="module")
def temp_dir():
    _path = Path(tempfile.mkdtemp())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(_N):
            _fname = _path / f"test_{i:05d}.tiff"
            skimage.io.imsave(_fname, _DATA[i])
    yield _path
    shutil.rmtree(_path)
    # necessary due to use of 'LocalPluginCollection':
    qs = QtCore.QSettings("Hereon", "pydidas")
    qs.remove("unittesting")


@pytest.fixture
def set_up_scan(temp_dir):
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_name_pattern", "test_#####.tiff")
    SCAN.set_param_value("scan_base_directory", temp_dir)


def test_creation():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
    assert isinstance(plugin, BasePlugin)


def test_execute__no_input():
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
    with pytest.raises(UserConfigError):
        plugin.execute(0)


@pytest.mark.parametrize("ordinal", [0, 11, 21, 34])
@pytest.mark.parametrize("use_roi", [True, False])
def test_get_frame(set_up_scan, ordinal, use_roi):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
    plugin.set_param_value("use_roi", use_roi)
    plugin.set_param_value("roi_yhigh", 5)
    plugin.pre_execute()
    _data, kwargs = plugin.get_frame(ordinal)
    assert isinstance(_data, Dataset)
    assert _data.shape == (5 if use_roi else _IMG_SHAPE[0], _IMG_SHAPE[1])
    assert np.allclose(_data, ordinal)


@pytest.mark.parametrize("ordinal", [0, 11, 21, 34])
@pytest.mark.parametrize("use_roi", [True, False])
def test__integration__execute(set_up_scan, ordinal, use_roi):
    plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
    plugin.set_param_value("use_roi", use_roi)
    plugin.set_param_value("roi_yhigh", 5)
    plugin.pre_execute()
    _data, kwargs = plugin.execute(ordinal)
    assert np.allclose(_data, ordinal)
    assert _data.shape == (5 if use_roi else _IMG_SHAPE[0], _IMG_SHAPE[1])


if __name__ == "__main__":
    unittest.main()
