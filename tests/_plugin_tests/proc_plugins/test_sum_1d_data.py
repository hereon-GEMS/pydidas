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

from pydidas.core import Dataset
from pydidas.plugins import BasePlugin, PluginCollection


PLUGIN_COLLECTION = PluginCollection()


class TestSum1dData(unittest.TestCase):
    def setUp(self):
        self._n = 120
        self._data = np.arange(self._n)

    def tearDown(self):
        ...

    def create_dataset(self):
        self._x = 12 + 0.37 * np.arange(self._n)
        _data = Dataset(self._data, axis_ranges=[self._x])
        return _data

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_get_slice__w_indices(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        _range = plugin._get_slice()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_slice__w_data(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit", self._x[_low])
        plugin.set_param_value("upper_limit", self._x[_high])
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_slice()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_slice__w_empty_range(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit", self._x[_high])
        plugin.set_param_value("upper_limit", self._x[_low])
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_slice()
        self.assertEqual(_range, slice(0, 0))

    def test_get_slice__w_sinple_point_range(self):
        _low = 42
        _high = 42
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value("lower_limit", self._x[_high])
        plugin.set_param_value("upper_limit", self._x[_low])
        plugin.set_param_value("type_selection", "Data values")
        _range = plugin._get_slice()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _low + 1)

    def test_execute__empty_selection(self):
        _low = 42
        _high = 40
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], 0)

    def test_execute__single_item_selection(self):
        _low = 42
        _high = 42
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(_data[0], self._data[_low])

    def test_execute__range(self):
        _low = 42
        _high = 47
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(_data[0], np.sum(self._data[_low : _high + 1]))

    def test_execute__None_lower_bounds(self):
        _low = None
        _high = 47
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(_data[0], np.sum(self._data[: _high + 1]))

    def test_execute__None_upper_bounds(self):
        _low = 42
        _high = None
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = self.create_dataset()
        _data, _ = plugin.execute(data)
        self.assertTrue(_data[0], np.sum(self._data[_low:]))


if __name__ == "__main__":
    unittest.main()
