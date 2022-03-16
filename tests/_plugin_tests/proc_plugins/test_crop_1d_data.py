# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import unittest
import tempfile
import shutil
import random

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset
from pydidas.plugins import PluginCollection, BasePlugin
from pydidas.image_io import rebin2d


PLUGIN_COLLECTION = PluginCollection()


class TestCrop1dData(unittest.TestCase):

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
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_get_index_range__w_indices(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        plugin.set_param_value('crop_low', _low)
        plugin.set_param_value('crop_high', _high)
        plugin.set_param_value('crop_type', 'Indices')
        _range = plugin._get_index_range()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__w_data(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value('crop_low', self._x[_low])
        plugin.set_param_value('crop_high', self._x[_high])
        plugin.set_param_value('crop_type', 'Data values')
        _range = plugin._get_index_range()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _high + 1)

    def test_get_index_range__w_empty_range(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value('crop_low', self._x[_high])
        plugin.set_param_value('crop_high', self._x[_low])
        plugin.set_param_value('crop_type', 'Data values')
        _range = plugin._get_index_range()
        self.assertEqual(_range, slice(0, 0))

    def test_get_index_range__w_sinple_point_range(self):
        _low = 42
        _high = 42
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        data = self.create_dataset()
        plugin._data = data
        plugin.set_param_value('crop_low', self._x[_high])
        plugin.set_param_value('crop_high', self._x[_low])
        plugin.set_param_value('crop_type', 'Data values')
        _range = plugin._get_index_range()
        self.assertEqual(_range.start, _low)
        self.assertEqual(_range.stop, _low + 1)

    def test_execute(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Crop1dData')()
        plugin.set_param_value('crop_low', _low)
        plugin.set_param_value('crop_high', _high)
        plugin.set_param_value('crop_type', 'Indices')
        _data, _ = plugin.execute(self._data)
        self.assertTrue(np.allclose(_data, self._data[_low:_high + 1]))


if __name__ == "__main__":
    unittest.main()
