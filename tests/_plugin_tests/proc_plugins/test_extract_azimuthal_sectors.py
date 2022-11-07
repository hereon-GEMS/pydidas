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
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

import numpy as np

from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestExtractAzimuthalSectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._input_data = np.ones((72, 1000))
        cls._x = np.arange(cls._input_data.shape[1])

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_dataset_degree(self):
        _data = Dataset(
            self._input_data,
            axis_ranges=[np.linspace(2.5, 357.5, 72), self._x],
            axis_labels=["azimuthal", "radial"],
            axis_units=["deg", "px"],
        )
        return _data

    def get_default_plugin(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ExtractAzimuthalSectors")()
        plugin.set_param_value("centers", "0; 90; 180; 270")
        plugin.set_param_value("width", 10)
        plugin._data = self.create_dataset_degree()
        return plugin

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ExtractAzimuthalSectors")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_get_sector_values__no_sectors(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ExtractAzimuthalSectors")()
        with self.assertRaises(UserConfigError):
            plugin._get_sector_values()

    def test_get_sector_values__no_float_sectors(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ExtractAzimuthalSectors")()
        plugin.set_param_value("centers", "-something; -12")
        with self.assertRaises(UserConfigError):
            plugin._get_sector_values()

    def test_pre_execute__sectors(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ExtractAzimuthalSectors")()
        plugin.set_param_value("centers", "90; 170; 240")
        plugin.pre_execute()
        self.assertIsInstance(plugin._config["centers"], np.ndarray)
        self.assertTrue(
            np.allclose(plugin._config["centers"], np.array((90, 170, 240)))
        )

    def test_update_settings_from_data__degree_width_10(self):
        plugin = self.get_default_plugin()
        plugin.pre_execute()
        plugin._update_settings_from_data()
        for _index, _slice in plugin._config["slices"].items():
            self.assertEqual(len(_slice), 2)

    def test_update_settings_from_data__rad_width_10_deg(self):
        plugin = self.get_default_plugin()
        plugin.set_param_value("width", 10 * np.pi / 180)
        plugin.set_param_value(
            "centers", ";".join(f"{i*np.pi/2:.10f}" for i in range(4))
        )
        plugin._data.update_axis_units(0, "rad")
        plugin._data.update_axis_ranges(
            0, np.linspace(np.pi / 72, 143 / 72 * np.pi, 72)
        )
        plugin.pre_execute()
        plugin._update_settings_from_data()
        for _index, _slice in plugin._config["slices"].items():
            self.assertEqual(len(_slice), 2)

    def test_update_settings_from_data__degree_width_10_inconsistency_at_180(self):
        plugin = self.get_default_plugin()
        plugin.pre_execute()
        plugin._data.update_axis_ranges(0, np.linspace(-177.5, 177.5, 72))
        plugin._update_settings_from_data()
        for _index, _slice in plugin._config["slices"].items():
            self.assertEqual(len(_slice), 2)

    def test_update_settings_from_data__degree_width_5(self):
        plugin = self.get_default_plugin()
        plugin.set_param_value("width", 5)
        plugin.pre_execute()
        with self.assertRaises(UserConfigError):
            plugin._update_settings_from_data()

    def test_execute__width_10_sum(self):
        plugin = self.get_default_plugin()
        plugin.set_param_value("mode", "Sum")
        plugin.pre_execute()
        _input = self.create_dataset_degree()
        _res, _kwargs = plugin.execute(_input)
        self.assertEqual(_res.shape, (4, self._x.size))
        self.assertEqual(np.mean(_res), 2)
        self.assertEqual(np.std(_res), 0)

    def test_execute__width_10_average(self):
        plugin = self.get_default_plugin()
        plugin.set_param_value("mode", "Average")
        plugin.pre_execute()
        _input = self.create_dataset_degree()
        _res, _kwargs = plugin.execute(_input)
        self.assertEqual(_res.shape, (4, self._x.size))
        self.assertEqual(np.mean(_res), 1)
        self.assertEqual(np.std(_res), 0)


if __name__ == "__main__":
    unittest.main()