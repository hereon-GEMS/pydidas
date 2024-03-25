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


import unittest

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestRollingAverage1d(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._n = 120
        cls._x = np.linspace(0, 2 * np.pi, num=cls._n)
        cls._y = np.sin(cls._x) + 0.2 * (0.5 - np.random.random(cls._n))

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self): ...

    def tearDown(self): ...

    def create_dataset(self):
        _data = Dataset(
            self._y, axis_ranges=[self._x], axis_labels=["test"], axis_units=["number"]
        )
        return _data

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RollingAverage1d")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_kernel(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RollingAverage1d")()
        plugin.set_param_value("kernel_width", 0)
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_pre_execute__kernel(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RollingAverage1d")()
        plugin.set_param_value("kernel_width", 3)
        plugin.pre_execute()
        self.assertIsInstance(plugin._kernel, np.ndarray)

    def test_execute__kernel4(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RollingAverage1d")()
        plugin.set_param_value("kernel_width", 4)
        data = self.create_dataset()
        plugin.pre_execute()
        new_data, _ = plugin.execute(data)
        self.assertEqual(data.axis_labels[0], new_data.axis_labels[0])
        self.assertEqual(data.axis_units[0], new_data.axis_units[0])
        self.assertTrue(np.allclose(data.axis_ranges[0], new_data.axis_ranges[0]))
        for _index in [0, 1, 2, -3, -2, -1]:
            self.assertEqual(data[_index], new_data[_index])
        for _index in [3, 4, -5, -4]:
            self.assertNotEqual(data[_index], new_data[_index])

    def test_execute__kernel7(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RollingAverage1d")()
        plugin.set_param_value("kernel_width", 7)
        data = self.create_dataset()
        plugin.pre_execute()
        new_data, _ = plugin.execute(data)
        for _index in [0, 1, 2, 3, -4, -3, -2, -1]:
            self.assertEqual(data[_index], new_data[_index])
        for _index in [5, 6, -6, -5]:
            self.assertNotEqual(data[_index], new_data[_index])


if __name__ == "__main__":
    unittest.main()
