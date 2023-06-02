# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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

from pydidas.core import Dataset, UserConfigError
from pydidas.core.fitting import FitFuncMeta
from pydidas.plugins import BasePlugin, PluginCollection


PLUGIN_COLLECTION = PluginCollection()


class TestBaseFitPlugin(unittest.TestCase):
    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(
            np.ones((150)), data_unit="data unit", axis_units=["ax_unit"]
        )
        self._x = np.arange(self._data.size) * 0.5
        self._peak_x = self._x[self._peakpos]
        self._data.axis_ranges = [self._x]
        self._data[self._peakpos - 5 : self._peakpos + 6] += [
            0.5,
            1.6,
            4,
            7.2,
            10.5,
            12,
            10.5,
            7.2,
            4,
            1.5,
            0.5,
        ]

    def tearDown(self):
        pass

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__gaussian_no_bg(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_func", "Gaussian")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        self.assertEqual(plugin._fitter, FitFuncMeta.get_fitter("Gaussian"))
        self.assertEqual(
            plugin._config["param_labels"], ["amplitude", "sigma", "center"]
        )
        self.assertEqual(plugin._config["bounds_low"], [0, 0, -np.inf])
        self.assertEqual(plugin._config["bounds_high"], [np.inf, np.inf, np.inf])

    def test_pre_execute__lorentzian(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_func", "Lorentzian")
        plugin.pre_execute()
        self.assertEqual(plugin._fitter, FitFuncMeta.get_fitter("Lorentzian"))
        self.assertEqual(
            plugin._config["param_labels"],
            ["amplitude", "gamma", "center", "background_p0"],
        )
        self.assertEqual(plugin._config["bounds_low"], [0, 0, -np.inf, -np.inf])
        self.assertEqual(
            plugin._config["bounds_high"], [np.inf, np.inf, np.inf, np.inf]
        )

    def test_pre_execute__voigt_1st_order_bg(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_func", "Voigt")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        self.assertEqual(plugin._fitter, FitFuncMeta.get_fitter("Voigt"))
        self.assertEqual(
            plugin._config["param_labels"],
            ["amplitude", "sigma", "gamma", "center", "background_p0", "background_p1"],
        )
        self.assertEqual(
            plugin._config["bounds_low"], [0, 0, 0, -np.inf, -np.inf, -np.inf]
        )
        self.assertEqual(
            plugin._config["bounds_high"],
            [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        )

    def test_crop_data_to_selected_range__empty_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_lower_limit", 42)
        plugin.set_param_value("fit_upper_limit", 2)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        with self.assertRaises(UserConfigError):
            plugin._crop_data_to_selected_range()

    def test_crop_data_to_selected_range__normal_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_lower_limit", 5)
        plugin.set_param_value("fit_upper_limit", 20)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x <= 20).all())
        self.assertTrue((plugin._data_x >= 5).all())

    def test_crop_data_to_selected_range__low_limit_None(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_lower_limit", None)
        plugin.set_param_value("fit_upper_limit", 20)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x <= 20).all())

    def test_crop_data_to_selected_range__high_limit_None(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("BaseFitPlugin")()
        plugin.set_param_value("fit_lower_limit", 5)
        plugin.set_param_value("fit_upper_limit", None)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x >= 5).all())


if __name__ == "__main__":
    unittest.main()
