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


import unittest

import numpy as np
from qtpy import QtCore

from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection, create_dataset


PLUGIN_COLLECTION = LocalPluginCollection()


class TestSum1dData(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self): ...

    def tearDown(self): ...

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
        plugin._data = create_dataset(1, shape=(200,))
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        _mask = plugin._get_mask()
        _mask_true = np.where(_mask)[0]
        self.assertEqual(_mask_true.size, _high - _low + 1)
        self.assertEqual(_mask_true[0], _low)
        self.assertEqual(_mask_true[-1], _high)

    def test_get_slice__w_data(self):
        _low = 42
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = create_dataset(1, shape=(200,))
        plugin._data = data
        plugin.set_param_value("lower_limit", data.axis_ranges[0][_low])
        plugin.set_param_value("upper_limit", data.axis_ranges[0][_high])
        plugin.set_param_value("type_selection", "Axis values")
        _mask = plugin._get_mask()
        _mask_true = np.where(_mask)[0]
        self.assertEqual(_mask_true[0], _low)
        self.assertEqual(_mask_true[-1], _high)

    def test_get_slice__w_empty_range(self):
        _low = 90
        _high = 87
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = create_dataset(1, shape=(200,))
        plugin._data = data
        plugin.set_param_value("lower_limit", data.axis_ranges[0][_low])
        plugin.set_param_value("upper_limit", data.axis_ranges[0][_high])
        plugin.set_param_value("type_selection", "Axis values")
        _mask = plugin._get_mask()
        _mask_true = np.where(_mask)[0]
        self.assertEqual(_mask_true.size, 0)

    def test_get_slice__w_sinple_point_range(self):
        _low = 42
        _high = 42
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        data = create_dataset(1, shape=(200,))
        plugin._data = data
        plugin.set_param_value("lower_limit", data.axis_ranges[0][_low])
        plugin.set_param_value("upper_limit", data.axis_ranges[0][_high])
        plugin.set_param_value("type_selection", "Axis values")
        _mask = plugin._get_mask()
        _mask_true = np.where(_mask)[0]
        self.assertEqual(_mask_true.size, 1)
        self.assertEqual(_mask_true[0], _low)

    def test_execute__empty_selection(self):
        _low = 42
        _high = 40
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(1)
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], 0)

    def test_execute__single_item_selection(self):
        _low = 42
        _high = 42
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(1, shape=(200,))
        _data, _ = plugin.execute(data)
        self.assertEqual(sum(_data), data[_low])

    def test_execute__range(self):
        _low = 42
        _high = 47
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(1, shape=(200,))
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], np.sum(data[_low : _high + 1]))

    def test_execute__None_lower_bounds(self):
        _low = None
        _high = 47
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(1, shape=(200,))
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], np.sum(data[: _high + 1]))

    def test_execute__None_upper_bounds(self):
        _low = 42
        _high = None
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(1, shape=(200,))
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], np.sum(data[_low:]))

    def test_execute__multidim(self):
        _low = 2
        _high = 7
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum1dData")()
        plugin.set_param_value("lower_limit", _low)
        plugin.set_param_value("upper_limit", _high)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(4)
        for _dim in range(4):
            with self.subTest(dim=_dim):
                plugin._data = data
                plugin.pre_execute()
                plugin.set_param_value("process_data_dim", _dim)
                _ref_arr = np.where(
                    (_low <= np.arange(data.shape[_dim]))
                    & (np.arange(data.shape[_dim]) <= _high),
                    1,
                    0,
                ).astype(bool)
                _slicer = [None] * _dim + [slice(None)] + [None] * (3 - _dim)
                _ref_mask = np.ones(data.shape, dtype=bool) * _ref_arr[*_slicer]
                _data, _ = plugin.execute(data)
                self.assertTrue(
                    np.all(_data == np.sum(data, axis=_dim, where=_ref_mask))
                )


if __name__ == "__main__":
    unittest.main()
