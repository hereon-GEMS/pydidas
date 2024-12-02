# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import os
import shutil
import tempfile
import unittest

import h5py
import numpy as np
from pydidas.core.utils import get_random_string, rebin2d
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection
from qtpy import QtCore


PLUGIN_COLLECTION = LocalPluginCollection()


class TestSubtractBgImage(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._shape = (20, 20)
        self._bg = np.random.random(self._shape)
        self._data = np.ones(self._shape)

    def tearDown(self):
        shutil.rmtree(self._temppath)

    def create_bg_image(self):
        _fname = os.path.join(self._temppath, "bg_image.npy")
        np.save(_fname, self._bg)
        return _fname

    def create_bg_hdf5_image(self):
        _fname = os.path.join(self._temppath, "bg_image.h5")
        _dset = get_random_string(4) + "/" + get_random_string(4) + "data"
        with h5py.File(_fname, "w") as _f:
            _f[_dset] = self._bg[None]
        return _fname, _dset

    def create_plugin(self, hdf5=False):
        _cls = PLUGIN_COLLECTION.get_plugin_by_name("SubtractBackgroundImage")
        plugin = _cls()
        if hdf5:
            _fname, _dset = self.create_bg_hdf5_image()
            plugin.set_param_value("bg_file", _fname)
            plugin.set_param_value("bg_hdf5_key", _dset)
        else:
            _fname = self.create_bg_image()
            plugin.set_param_value("bg_file", _fname)
        return plugin

    def test_creation(self):
        plugin = self.create_plugin()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__simple_bg_image(self):
        plugin = self.create_plugin(hdf5=False)
        plugin.pre_execute()
        self.assertTrue(np.all(plugin._bg_image == self._bg))

    def test_pre_execute__hdf5_bg_image(self):
        plugin = self.create_plugin(hdf5=True)
        plugin.pre_execute()
        self.assertTrue(np.all(plugin._bg_image == self._bg))

    def test_pre_execute__None_threshold(self):
        plugin = self.create_plugin(hdf5=True)
        plugin.set_param_value("threshold_low", None)
        plugin.pre_execute()
        self.assertIsNone(plugin._thresh)

    def test_pre_execute__nan_threshold(self):
        plugin = self.create_plugin(hdf5=True)
        plugin.set_param_value("threshold_low", np.nan)
        plugin.pre_execute()
        self.assertIsNone(plugin._thresh)

    def test_pre_execute_finite_threshold(self):
        _thresh = 42.567
        plugin = self.create_plugin(hdf5=True)
        plugin.set_param_value("threshold_low", _thresh)
        plugin.pre_execute()
        self.assertEqual(plugin._thresh, _thresh)

    def test_execute__simple(self):
        _thresh = 0.12
        _kwargs = {"key": 1, "another_key": "another_val"}
        plugin = self.create_plugin(hdf5=False)
        plugin.set_param_value("threshold_low", _thresh)
        plugin.pre_execute()
        _new_data, _new_kwargs = plugin.execute(self._data, **_kwargs)
        self.assertEqual(_kwargs, _new_kwargs)
        self.assertTrue(np.all(_new_data >= _thresh))
        self.assertTrue(np.all(self._data - self._bg <= _new_data))

    def test_execute__with_roi_and_binning(self):
        _thresh = 0.12
        _kwargs = {"key": 1, "another_key": "another_val"}
        plugin = self.create_plugin(hdf5=False)
        plugin.set_param_value("threshold_low", _thresh)
        plugin.set_param_value("binning", 2)
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_xlow", 3)
        plugin.set_param_value("roi_xhigh", self._shape[0])
        plugin.set_param_value("roi_ylow", 1)
        plugin.set_param_value("roi_yhigh", self._shape[1])
        plugin.pre_execute()
        _data = rebin2d(self._data[1:, 3:], 2)
        _new_data, _new_kwargs = plugin.execute(_data, **_kwargs)
        self.assertEqual(_kwargs, _new_kwargs)
        self.assertEqual(
            _new_data.shape, ((self._shape[0] - 1) // 2, (self._shape[1] - 3) // 2)
        )
        self.assertTrue(np.all(_new_data >= _thresh))


if __name__ == "__main__":
    unittest.main()
