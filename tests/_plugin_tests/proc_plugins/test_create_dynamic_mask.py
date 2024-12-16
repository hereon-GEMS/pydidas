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

import numpy as np
import scipy.ndimage
from qtpy import QtCore

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.core import UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestCreateDynamicMask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temppath = tempfile.mkdtemp()
        cls._data = np.zeros((40, 40), dtype=np.uint8)
        cls._data[7:12, 7:12] = 42
        cls._data[20:30, 12:14] = 32
        cls._data[35:, 35:] = 21
        cls._data[0:10, 30:] = 35
        cls._mask = np.zeros((40, 40), dtype=np.uint8)
        cls._mask[0:10, 30:] = 1
        cls._maskfilename = os.path.join(cls._temppath, "mask.npy")
        np.save(cls._maskfilename, cls._mask)
        cls._exp = DiffractionExperiment()
        cls._exp.set_param_value("detector_mask_file", cls._maskfilename)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temppath)
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def create_plugin(self, low=None, high=12, grow=0, iterations=1):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CreateDynamicMask")(
            diffraction_exp=self._exp,
            mask_threshold_low=low,
            mask_threshold_high=high,
            mask_grow=grow,
            kernel_iterations=iterations,
        )
        return plugin

    def test_creation(self):
        plugin = self.create_plugin()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__trivial(self):
        plugin = self.create_plugin(high=None)
        plugin.pre_execute()
        self.assertTrue(plugin._trivial)

    def test_pre_execute__use_mask(self):
        plugin = self.create_plugin()
        plugin.pre_execute()
        self.assertTrue((plugin._mask == self._mask).all())

    def test_pre_execute__use_mask_wrong_filename(self):
        plugin = self.create_plugin()
        self._exp.set_param_value("detector_mask_file", "/dummy/not/existing/file/path")
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_pre_execute__grow_mask(self):
        plugin = self.create_plugin(grow=7)
        plugin.pre_execute()
        self.assertEqual(plugin._kernel.shape, (15, 15))
        self.assertEqual(scipy.ndimage.binary_dilation, plugin._operation)

    def test_pre_execute__shrink_mask(self):
        plugin = self.create_plugin(grow=-4)
        plugin.pre_execute()
        self.assertEqual(plugin._kernel.shape, (9, 9))
        self.assertEqual(scipy.ndimage.binary_erosion, plugin._operation)

    def test_execute__trivial(self):
        plugin = self.create_plugin(high=None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assertEqual(_kwargs, dict())

    def test_execute__low_thresh(self):
        plugin = self.create_plugin(low=30, high=None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data < 30, True, False)
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__low_thresh_no_det_mask(self):
        plugin = self.create_plugin(low=30, high=None)
        plugin.set_param_value("use_detector_mask", False)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data < 30, True, False)
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__high_thresh(self):
        plugin = self.create_plugin(low=None, high=40)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data > 40, True, False)
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__low_and_high_thresh(self):
        plugin = self.create_plugin(low=25, high=40)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where((25 < self._data) & (self._data < 40), False, True)
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__high_thresh_growing(self):
        plugin = self.create_plugin(low=None, high=40, grow=2)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data > 40, True, False)
        _target_mask = scipy.ndimage.binary_dilation(
            _target_mask, structure=np.ones((5, 5))
        )
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__high_thresh_shrinking(self):
        plugin = self.create_plugin(low=None, high=40, grow=-2)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data > 40, True, False)
        _target_mask = scipy.ndimage.binary_erosion(
            _target_mask, structure=np.ones((5, 5))
        )
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__high_thresh_shrinking_multi_interations(self):
        plugin = self.create_plugin(low=None, high=40, grow=-2, iterations=3)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data > 40, True, False)
        _target_mask = scipy.ndimage.binary_erosion(
            _target_mask, structure=np.ones((5, 5)), iterations=3
        )
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())

    def test_execute__high_thresh_growing_multi_interations(self):
        plugin = self.create_plugin(low=None, high=40, grow=2, iterations=3)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _target_mask = np.where(self._data > 40, True, False)
        _target_mask = scipy.ndimage.binary_dilation(
            _target_mask, structure=np.ones((5, 5)), iterations=3
        )
        _target_mask[0:10, 30:] = True
        self.assertTrue((_kwargs["custom_mask"] == _target_mask).all())


if __name__ == "__main__":
    unittest.main()
