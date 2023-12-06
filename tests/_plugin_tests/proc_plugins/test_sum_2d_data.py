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

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestSum2dData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._nx = 10
        cls._ny = 25
        cls._n = cls._nx * cls._ny
        cls._data = np.arange(cls._n).reshape(cls._ny, cls._nx)
        cls._x = np.arange(cls._nx) * 2.4 - 12
        cls._y = np.arange(cls._ny) * 1.7 + 42

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def tearDown(self):
        ...

    def create_dataset(self):
        _data = Dataset(self._data, axis_ranges=[self._y, self._x])
        return _data

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_get_index_range__x_w_indices(self):
        _low = 3
        _high = 8
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low)
        plugin.set_param_value("upper_limit_ax1", _high)
        plugin.set_param_value("type_selection", "Indices")
        plugin._data = self.create_dataset()
        _range = plugin._get_index_ranges()[1]
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__y_w_indices(self):
        _low = 5
        _high = 13
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax0", _low)
        plugin.set_param_value("upper_limit_ax0", _high)
        plugin.set_param_value("type_selection", "Indices")
        plugin._data = self.create_dataset()
        _range = plugin._get_index_ranges()[0]
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__x_w_data(self):
        _low = 3
        _high = 8
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit_ax1", self._x[_low])
        plugin.set_param_value("upper_limit_ax1", self._x[_high])
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_index_ranges()[1]
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__y_w_data(self):
        _low = 4
        _high = 15
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit_ax0", self._y[_low])
        plugin.set_param_value("upper_limit_ax0", self._y[_high])
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_index_ranges()[0]
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__w_empty_range(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit_ax1", 120)
        plugin.set_param_value("upper_limit_ax1", 420)
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_index_ranges()[1]
        self.assertEqual(_range, slice(0, 0))

    def test_execute__empty_selection(self):
        _low_y = 12
        _high_y = 7
        _low_x = 8
        _high_x = 3
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low_x)
        plugin.set_param_value("upper_limit_ax1", _high_x)
        plugin.set_param_value("lower_limit_ax0", _low_y)
        plugin.set_param_value("upper_limit_ax0", _high_y)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], 0)

    def test_execute__single_item_selection(self):
        _low_y = 12
        _high_y = 12
        _low_x = 7
        _high_x = 7
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low_x)
        plugin.set_param_value("upper_limit_ax1", _high_x)
        plugin.set_param_value("lower_limit_ax0", _low_y)
        plugin.set_param_value("upper_limit_ax0", _high_y)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(_data[0], self._data[_low_y, _low_x])

    def test_execute__range(self):
        _low_y = 3
        _high_y = 12
        _low_x = 1
        _high_x = 7
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low_x)
        plugin.set_param_value("upper_limit_ax1", _high_x)
        plugin.set_param_value("lower_limit_ax0", _low_y)
        plugin.set_param_value("upper_limit_ax0", _high_y)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(
            _data[0], np.sum(self._data[_low_y : _high_y + 1, _low_x : _high_x + 1])
        )


if __name__ == "__main__":
    unittest.main()
