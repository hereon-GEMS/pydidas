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
__status__ = "Development"


import unittest

import numpy as np

from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestAverageOppositeSectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._nx = 10
        cls._ny = 25
        cls._n = cls._nx * cls._ny
        cls._data = np.arange(cls._n).reshape(cls._ny, cls._nx)
        cls._x = np.arange(cls._nx) * 2.4 - 12
        cls._y = np.arange(cls._ny) * 1.7 + 42

        cls._d = Dataset(
            np.ones((36, 400)),
            axis_ranges=[np.linspace(0, 360, 36, endpoint=False), np.arange(400)],
            axis_units=["chi / deg", "2theta / deg"],
        )

    def tearDown(self):
        ...

    def create_dataset(self, chi_start=0, chi_end=360, dchi=5):
        _y = np.linspace(
            chi_start, chi_end, num=(chi_end - chi_start) // dchi, endpoint=False
        )
        _x = np.linspace(3, 5, num=200)
        _data = np.tile(np.arange(_y.size), _x.size).reshape(_y.size, _x.size).T
        return Dataset(_data, axis_ranges=[_y, _x])

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_calculate_result_shape__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
        with self.assertRaises(UserConfigError):
            plugin.calculate_result_shape()

    def test_calculate_result_shape__correct_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
        plugin._config["input_shape"] = (24, 500)
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (12, 500))

    # def test_calculate_result_shape__correct_input_full_symmetry(self):
    #     plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
    #     plugin.set_param_value("symmetry", plugin.get_param("symmetry").choices[1])
    #     plugin._config["input_shape"] = (24, 500)
    #     plugin.calculate_result_shape()
    #     self.assertEqual(plugin._config["result_shape"], (6, 500))

    def test_calculate_result_shape__incorrect_shape(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
        plugin._config["input_shape"] = (25, 500)
        with self.assertRaises(UserConfigError):
            plugin.calculate_result_shape()

    # def test_calculate_result_shape__full_symmetry_incorrect_shape(self):
    #     plugin = PLUGIN_COLLECTION.get_plugin_by_name("AverageOppositeSectors")()
    #     plugin.set_param_value("symmetry", plugin.get_param("symmetry").choices[1])
    #     plugin._config["input_shape"] = (22, 500)
    #     with self.assertRaises(UserConfigError):
    #         plugin.calculate_result_shape()


if __name__ == "__main__":
    unittest.main()
