# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import random
import unittest

import numpy as np
import scipy.ndimage
from qtpy import QtCore

from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestMaskAndAverageImageStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._shape = (5, 100, 100)

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        _n = self._shape[0] * self._shape[1] * self._shape[2]
        self._data = np.asarray([random.randint(0, 100) for _ in range(_n)]).reshape(
            self._shape
        )
        self._zero = np.zeros(self._shape[1:], dtype=np.float64)

    def assert_arrays_equal(self, data1: np.ndarray, data2: np.ndarray):
        self.assertTrue(np.array_equal(data1, data2))

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__grow(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("mask_threshold_high", 3)
        plugin.set_param_value("mask_grow", 1)
        plugin.pre_execute()
        self.assertIs(plugin._operation, scipy.ndimage.binary_dilation)

    def test_pre_execute__shrink(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("mask_threshold_high", 3)
        plugin.set_param_value("mask_grow", -1)
        plugin.pre_execute()
        self.assertIs(plugin._operation, scipy.ndimage.binary_erosion)

    def test_pre_execute__overlapping_thresholds(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("mask_threshold_low", 80)
        plugin.set_param_value("mask_threshold_high", 20)
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_pre_execute__trivial(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.pre_execute()
        self.assertTrue(plugin._trivial)

    def test_execute__no_thresholds(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin._trivial = True
        _data, _kwargs = plugin.execute(self._data)
        self._zero = np.sum(self._data, axis=0) / self._data.shape[0]
        self.assert_arrays_equal(_data, self._zero)

    def test_execute__single_pixel(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        _input = np.zeros(self._shape, dtype=np.uint8)
        _input[0, 0, 0] = 1
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(_input)
        self._zero[0, 0] = _input[0, 0, 0] / _input.shape[0]
        self.assert_arrays_equal(_result, self._zero)

    def test_execute__single_pixel_center(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        _input = np.zeros(self._shape, dtype=np.uint8)
        _input[0, 50, 50] = 1
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(_input)
        self._zero[50, 50] = _input[0, 50, 50] / _input.shape[0]
        self.assert_arrays_equal(_result, self._zero)

    def test_execute__bottom_half(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = np.zeros(self._shape, dtype=np.uint8)
        self._data[0, 50:, 0:] = 1
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self._zero = np.sum(self._data, axis=0) / self._data.shape[0]
        self.assert_arrays_equal(_data, self._zero)

    def test_execute__grow(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = Dataset(np.zeros(self._shape, dtype=np.uint8))
        self._data[1] = 4
        self._data[0, 10:90, 10:90] = 90
        _thresh_high = 80
        plugin.set_param_value("mask_threshold_high", _thresh_high)
        plugin.set_param_value("mask_grow", 9)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _ref = np.full(_data.shape, np.sum(self._data, axis=0) / self._data.shape[0])
        _ref[1:-1, 1:-1] = np.sum(
            np.where(self._data <= _thresh_high, self._data, 0)[:, 1:-1, 1:-1], axis=0
        ) / (self._data.shape[0] - 1)
        self.assert_arrays_equal(_data, _ref)

    def test_execute__shrink(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = np.zeros(self._shape, dtype=np.uint8)
        self._data[1, 0:, 0:] = 1
        self._data[0, 1:-1, 1:-1] = 90
        _thresh_high = 80
        plugin.set_param_value("mask_threshold_high", _thresh_high)
        plugin.set_param_value("mask_grow", -1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _ref = np.full(_data.shape, np.sum(self._data, axis=0) / self._data.shape[0])
        _ref[2:-2, 2:-2] = np.sum(
            np.where(self._data <= _thresh_high, self._data, 0)[:, 2:-2, 2:-2], axis=0
        ) / (self._data.shape[0] - 1)
        self.assert_arrays_equal(_data, _ref)

    def test_execute__single_image(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = np.delete(self._data, (1, 2, 3, 4), axis=0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_arrays_equal(_data, self._data[0])

    def test_execute__2d_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = np.ones((100, 100), dtype=np.uint8)
        plugin.pre_execute()
        with self.assertRaises(UserConfigError):
            plugin.execute(self._data)

    def test_execute__empty_images(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        self._data = np.zeros(self._shape, dtype=np.uint8)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_arrays_equal(_data, self._zero)

    def test_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        with self.assertRaises(UserConfigError):
            plugin.execute(0)

    def test_execute__background_value(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("mask_threshold_low", 10)
        for background_value in (0, 12, np.nan):
            with self.subTest(background_value=background_value):
                plugin.set_param_value("background_value", background_value)
                self._data = np.full(self._shape, 5, dtype=np.uint8)
                self._data[0:, 1, 1] = 0
                plugin.pre_execute()
                _data, _kwargs = plugin.execute(self._data)
                if background_value is np.nan:
                    self.assertTrue(np.all(np.isnan(_data[1, 1])))
                else:
                    self.assertTrue(_data[1, 1] == background_value)

    def test_execute__adc_y(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("adc_mask", "Mask Y-axis")
        plugin.set_param_value("adc_mask_threshold", 5)
        plugin.pre_execute()
        self._data = np.ones(self._shape, dtype=np.uint8)
        self._data[0:, 1, 1] = 10
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(np.isnan(_data[:, 1]).all())
        self.assertTrue(np.all(_data[:, 2:] == 1))

    def test_execute__adc_x(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("adc_mask", "Mask X-axis")
        plugin.set_param_value("adc_mask_threshold", 5)
        plugin.pre_execute()
        self._data = np.ones(self._shape, dtype=np.uint8)
        self._data[0:, 1, 1] = 10
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(np.isnan(_data[1, :]).all())
        self.assertTrue(np.all(_data[2:, :] == 1))

    def test_execute__adc_half_y(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("adc_mask", "Mask half Y-axis")
        plugin.set_param_value("adc_mask_threshold", 5)
        plugin.pre_execute()
        self._data = np.ones(self._shape, dtype=np.uint8)
        self._data[0:, 1, 1] = 10
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(np.isnan(_data[:50, 1]).all())
        self.assertTrue(np.all(_data[51:, 1] == 1))

    def test_execute__adc_half_x(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskAndAverageImageStack")()
        plugin.set_param_value("adc_mask", "Mask half X-axis")
        plugin.set_param_value("adc_mask_threshold", 5)
        plugin.pre_execute()
        self._data = np.ones(self._shape, dtype=np.uint8)
        self._data[0:, 1, 1] = 10
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(np.isnan(_data[1, :50]).all())
        self.assertTrue(np.all(_data[1, 51:] == 1))


if __name__ == "__main__":
    unittest.main()
