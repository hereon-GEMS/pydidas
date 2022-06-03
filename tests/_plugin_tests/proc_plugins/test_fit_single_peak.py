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

from pydidas.core import AppConfigError, Dataset
from pydidas.core.constants import gaussian, lorentzian, voigt
from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestFitSinglePeak(unittest.TestCase):
    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(np.ones((150)))
        self._x = np.arange(self._data.size) * 0.5
        self._peak_x = self._x[self._peakpos]
        self._data.axis_ranges[0] = self._x
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

    def create_generic_plugin(self, func="Gaussian"):
        _low = 15
        _high = 27
        self._rangen = np.where((self._x >= _low) & (self._x <= _high))[0].size
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_func", func)
        plugin.set_param_value("fit_lower_limit", _low)
        plugin.set_param_value("fit_upper_limit", _high)
        return plugin

    def create_gauss_plugin_with_dummy_fit(self):
        plugin = self.create_generic_plugin()
        plugin._data = self._data
        plugin._crop_data_to_selected_range()
        plugin.pre_execute()
        _startguess = plugin._update_fit_startparams()
        plugin._fit_params = dict(zip(plugin._fitparam_labels, _startguess))
        self._dummy_metadata = {"test_meta": 123}
        plugin._data.metadata.update(self._dummy_metadata)
        return plugin

    def assert_fit_results_okay(self, fit_result_data, params, bg_order):
        self.assertEqual(fit_result_data.shape, (1,))
        self.assertTrue("fit_params" in fit_result_data.metadata)
        self.assertTrue("fit_func" in fit_result_data.metadata)
        self.assertTrue("fit_residual_std" in fit_result_data.metadata)
        self.assertTrue(20 <= params["amplitude"] <= 60)
        if "sigma" in params:
            self.assertTrue(params["sigma"] < 5)
        if "gamma" in params:
            self.assertTrue(params["gamma"] < 5)
        self.assertTrue((params["center"] < 22) & (params["center"] > 20))
        if bg_order in [0, 1]:
            self.assertTrue(
                (params["background_p0"] < 1) & (params["background_p0"] > 0)
            )
        if bg_order == 1:
            self.assertTrue(
                (params["background_p1"] < 1) & (params["background_p1"] > -1)
            )

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__gaussian_no_bg(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_func", "Gaussian")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        self.assertEqual(plugin._func, gaussian)
        self.assertEqual(plugin._fitparam_labels, ["amplitude", "sigma", "center"])
        self.assertEqual(plugin._fitparam_startpoints, [])
        self.assertEqual(plugin._fitparam_bounds_low, [0, 0, -np.inf])
        self.assertEqual(plugin._fitparam_bounds_high, [np.inf, np.inf, np.inf])

    def test_pre_execute__lorentzian(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_func", "Lorentzian")
        plugin.pre_execute()
        self.assertEqual(plugin._func, lorentzian)
        self.assertEqual(
            plugin._fitparam_labels, ["amplitude", "gamma", "center", "background_p0"]
        )
        self.assertEqual(plugin._fitparam_startpoints, [])
        self.assertEqual(plugin._fitparam_bounds_low, [0, 0, -np.inf, -np.inf])
        self.assertEqual(plugin._fitparam_bounds_high, [np.inf, np.inf, np.inf, np.inf])

    def test_pre_execute__voigt_1st_order_bg(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_func", "Voigt")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        self.assertEqual(plugin._func, voigt)
        self.assertEqual(
            plugin._fitparam_labels,
            ["amplitude", "sigma", "gamma", "center", "background_p0", "background_p1"],
        )
        self.assertEqual(
            plugin._fitparam_bounds_low, [0, 0, 0, -np.inf, -np.inf, -np.inf]
        )
        self.assertEqual(
            plugin._fitparam_bounds_high,
            [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        )

    def test_crop_data_to_selected_range__no_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin._data = self._data
        with self.assertRaises(AppConfigError):
            plugin._crop_data_to_selected_range()

    def test_crop_data_to_selected_range__empty_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", 42)
        plugin.set_param_value("fit_upper_limit", 2)
        plugin._data = self._data
        with self.assertRaises(AppConfigError):
            plugin._crop_data_to_selected_range()

    def test_crop_data_to_selected_range__normal_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", 0)
        plugin.set_param_value("fit_upper_limit", 20)
        plugin._data = self._data
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._x <= 20).all())
        self.assertTrue((plugin._x >= 0).all())

    def test_update_fit_startparams__no_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", None)
        plugin._data = self._data
        plugin._crop_data_to_selected_range()
        _startguess = plugin._update_fit_startparams()
        self.assertEqual(len(_startguess), 3)
        self.assertTrue(10 <= _startguess[0] <= 60)
        self.assertTrue(1 <= _startguess[1] <= 5)
        self.assertEqual(_startguess[2], self._peak_x)

    def test_update_fit_startparams__0order_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 0)
        plugin._data = self._data
        plugin._crop_data_to_selected_range()
        _startguess = plugin._update_fit_startparams()
        self.assertEqual(len(_startguess), 4)
        self.assertTrue(0 <= _startguess[0] <= 50)
        self.assertTrue(1 <= _startguess[1] <= 5)
        self.assertEqual(_startguess[2], self._peak_x)
        self.assertEqual(_startguess[3], np.amin(self._data))

    def test_update_fit_startparams__1order_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin._data = self._data
        plugin._crop_data_to_selected_range()
        _startguess = plugin._update_fit_startparams()
        self.assertEqual(len(_startguess), 5)
        self.assertTrue(0 <= _startguess[0] <= 50)
        self.assertTrue(1 <= _startguess[1] <= 5)
        self.assertEqual(_startguess[2], self._peak_x)
        self.assertEqual(_startguess[3], np.amin(self._data))
        self.assertEqual(_startguess[4], 0)

    def test_create_result_dataset__peak_area(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak area")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (1,))

    def test_create_result_dataset__peak_position(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak position")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (1,))

    def test_create_result_dataset__peak_area_and_position(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak area and position")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__std(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Fit normalized standard deviation")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (1,))

    def test_create_result_dataset__peak_area_and_position_and_std(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak area, position and norm. std")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (3,))

    def test_execute__gaussian_no_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)

    def test_execute__gaussian_0d_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 0)

    def test_execute__gaussian_1d_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 1)

    def test_execute__lorentzian_no_bg(self):
        plugin = self.create_generic_plugin("Lorentzian")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)

    def test_execute__lorentzian_0d_bg(self):
        plugin = self.create_generic_plugin("Lorentzian")
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 0)

    def test_execute__lorentzian_1d_bg(self):
        plugin = self.create_generic_plugin("Lorentzian")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 1)

    def test_execute__voigt_no_bg(self):
        plugin = self.create_generic_plugin("Voigt")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)

    def test_execute__voigt_0d_bg(self):
        plugin = self.create_generic_plugin("Voigt")
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 0)

    def test_execute__voigt_1d_bg(self):
        plugin = self.create_generic_plugin("Voigt")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 1)

    def test_calculate_result_shape__area(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak area")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (1,))

    def test_calculate_result_shape__position(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak position")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (1,))

    def test_calculate_result_shape__std(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Fit normalized standard deviation")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (1,))

    def test_calculate_result_shape__area_and_pos(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak area and position")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2,))

    def test_calculate_result_shape__area_pos_and_std(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak area, position and norm. std")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (3,))

    def test_calculate_result_shape__other(self):
        plugin = self.create_generic_plugin()
        plugin.params["output"].choices = plugin.params["output"].choices + ["dummy"]
        plugin.set_param_value("output", "dummy")
        with self.assertRaises(ValueError):
            plugin.calculate_result_shape()


if __name__ == "__main__":
    unittest.main()
