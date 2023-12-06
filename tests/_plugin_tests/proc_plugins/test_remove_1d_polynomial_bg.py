# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest
import warnings

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestRemove1dPolynomialBackground(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._n = 120
        cls._x = 4 + 0.42 * np.arange(cls._n)
        cls._y = 12 + 1.67 * np.sin(cls._x / 3) + (0.5 - np.random.random(cls._n))

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_dataset(self):
        _data = Dataset(
            self._y, axis_ranges=[self._x], axis_labels=["test"], axis_units=["number"]
        )
        return _data

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_kernel(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        plugin.set_param_value("kernel_width", 0)
        plugin.pre_execute()
        self.assertIsNone(plugin._kernel)

    def test_pre_execute__kernel(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        plugin.set_param_value("kernel_width", 3)
        plugin.pre_execute()
        self.assertIsInstance(plugin._kernel, np.ndarray)

    def test_pre_execute__nan_thresh(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        plugin.set_param_value("threshold_low", np.nan)
        plugin.pre_execute()
        self.assertIsNone(plugin._thresh)

    def test_pre_execute__None_thresh(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        plugin.set_param_value("threshold_low", None)
        plugin.pre_execute()
        self.assertIsNone(plugin._thresh)

    def test_pre_execute__finite_thresh(self):
        _thresh = -12.6
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        plugin.set_param_value("threshold_low", _thresh)
        plugin.pre_execute()
        self.assertEqual(plugin._thresh, _thresh)

    def test_execute__simple(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        data = self.create_dataset()
        plugin.pre_execute()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_data, _ = plugin.execute(data)
        self.assertEqual(data.axis_labels[0], new_data.axis_labels[0])
        self.assertEqual(data.axis_units[0], new_data.axis_units[0])
        self.assertTrue(np.allclose(data.axis_ranges[0], new_data.axis_ranges[0]))

    def test_execute__with_threshold(self):
        _thresh = 12
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        data = self.create_dataset()
        plugin.set_param_value("threshold_low", _thresh)
        plugin.pre_execute()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_data, _ = plugin.execute(data)
        self.assertTrue(np.all(new_data >= _thresh))

    def test_execute__with_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Remove1dPolynomialBackground")()
        data = self.create_dataset()
        plugin.set_param_value("include_limits", True)
        plugin.pre_execute()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_data, _ = plugin.execute(data)
        self.assertTrue(np.allclose(data, self._y, atol=0.51))


if __name__ == "__main__":
    unittest.main()
