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

from pydidas.core import UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection, create_dataset


PLUGIN_COLLECTION = LocalPluginCollection()


class TestSum2dData(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def tearDown(self): ...

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_get_index_range__w_indices(self):
        _low, _high = 3, 8
        data = create_dataset(2)
        for _ax in (0, 1):
            with self.subTest(dim=_ax):
                plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
                plugin.set_param_value(f"lower_limit_ax{_ax}", _low)
                plugin.set_param_value(f"upper_limit_ax{_ax}", _high)
                plugin.set_param_value("type_selection", "Indices")
                plugin._data = data
                _range = plugin._get_valid_indices(_ax, _ax)
                _ref_range = np.zeros((plugin._data.shape[_ax],), dtype=bool)
                _ref_range[_low : _high + 1] = True
                self.assertTrue(np.all(_range == _ref_range))

    def test_get_index_range__w_data(self):
        _low, _high = 3, 7
        data = create_dataset(2)
        _x, _y = data.axis_ranges[1], data.axis_ranges[0]
        for _int, _ax in [(1, _x), (0, _y)]:
            with self.subTest(dim=_int):
                plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
                plugin._data = data
                plugin.set_param_value(f"lower_limit_ax{_int}", _ax[_low])
                plugin.set_param_value(f"upper_limit_ax{_int}", _ax[_high])
                plugin.set_param_value("type_selection", "Axis values")
                _range = plugin._get_valid_indices(_int, _int)
                _ref_range = np.zeros((plugin._data.shape[_int],), dtype=bool)
                _ref_range[_low : _high + 1] = True
                self.assertTrue(np.all(_range == _ref_range))

    def test_get_index_range__w_empty_range(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        data = create_dataset(2)
        plugin._data = data
        _x = data.axis_ranges[1]
        plugin.set_param_value("lower_limit_ax1", _x[-1] + 5)
        plugin.set_param_value("upper_limit_ax1", _x[-1] + 10)
        plugin.set_param_value("type_selection", "Axis values")
        _range = plugin._get_valid_indices(1, 1)
        self.assertTrue(np.all(_range == 0))

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
        data = create_dataset(2)
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], 0)

    def test_execute__single_item_selection(self):
        _low_y = 5
        _high_y = 5
        _low_x = 7
        _high_x = 7
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low_x)
        plugin.set_param_value("upper_limit_ax1", _high_x)
        plugin.set_param_value("lower_limit_ax0", _low_y)
        plugin.set_param_value("upper_limit_ax0", _high_y)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(2)
        _data, _ = plugin.execute(data)
        self.assertEqual(_data[0], data[_low_y, _low_x])

    def test_execute__range(self):
        _low_y = 3
        _high_y = 7
        _low_x = 1
        _high_x = 7
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        plugin.set_param_value("lower_limit_ax1", _low_x)
        plugin.set_param_value("upper_limit_ax1", _high_x)
        plugin.set_param_value("lower_limit_ax0", _low_y)
        plugin.set_param_value("upper_limit_ax0", _high_y)
        plugin.set_param_value("type_selection", "Indices")
        data = create_dataset(2)
        _data, _ = plugin.execute(data)
        self.assertEqual(
            _data[0], np.sum(data[_low_y : _high_y + 1, _low_x : _high_x + 1])
        )

    def test_calculate_ranges__wrong_dims(self):
        _dim_settings = [(2, (1,)), (2, (3, 4, 5)), (3, None)]
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
        for _ndim, _dim_to_process in _dim_settings:
            with self.subTest(ndim=_ndim):
                plugin._data = create_dataset(_ndim)
                plugin.set_param_value("process_data_dims", _dim_to_process)
                with self.assertRaises(UserConfigError):
                    plugin._create_sum_mask()

    def test_pre_execute__with_more_dimensions(self):
        _cases = [(3, (0, 1)), (3, (2, 0)), (4, (1, 3)), (4, (0, -2))]
        for _ndim, _proc_dims in _cases:
            with self.subTest(ndim=_ndim, dims=_proc_dims):
                data = create_dataset(_ndim)
                plugin = PLUGIN_COLLECTION.get_plugin_by_name("Sum2dData")()
                plugin.set_param_value("process_data_dims", _proc_dims)
                plugin.pre_execute()
                _results, _ = plugin.execute(data)
                self.assertTrue(np.all(_results == np.sum(data, axis=_proc_dims)))


if __name__ == "__main__":
    unittest.main()
