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

import itertools
import unittest

import numpy as np

from pydidas.core import UserConfigError, Dataset
from pydidas.plugins import PluginCollection, BasePlugin
from pydidas.core.fitting import FitFuncMeta

PLUGIN_COLLECTION = PluginCollection()


class TestFitSinglePeak(unittest.TestCase):
    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(np.ones((150)))
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

    def create_generic_plugin(self, func="Gaussian"):
        _low = 10
        _high = 37
        self._rangen = np.where((self._x >= _low) & (self._x <= _high))[0].size
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin._config["input_shape"] = (150,)
        plugin.set_param_value("fit_func", func)
        plugin.set_param_value("fit_lower_limit", _low)
        plugin.set_param_value("fit_upper_limit", _high)
        plugin.calculate_result_shape()
        return plugin

    def create_gauss_plugin_with_dummy_fit(self):
        plugin = self.create_generic_plugin()
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        # plugin._config[]
        plugin._crop_data_to_selected_range()
        plugin.pre_execute()
        _startguess = plugin._fitter.guess_fit_start_params(
            plugin._data_x, plugin._data, plugin.get_param_value("fit_bg_order")
        )
        plugin._fit_params = dict(zip(plugin._config["param_labels"], _startguess))
        self._dummy_metadata = {"test_meta": 123}
        plugin._data.metadata = plugin._data.metadata | self._dummy_metadata
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
        self.assertEqual(plugin._fitter, FitFuncMeta.get_fitter("Gaussian"))
        self.assertEqual(
            plugin._config["param_labels"], ["amplitude", "sigma", "center"]
        )
        self.assertEqual(plugin._config["bounds_low"], [0, 0, -np.inf])
        self.assertEqual(plugin._config["bounds_high"], [np.inf, np.inf, np.inf])

    def test_pre_execute__lorentzian(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
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
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
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
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", 42)
        plugin.set_param_value("fit_upper_limit", 2)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        with self.assertRaises(UserConfigError):
            plugin._crop_data_to_selected_range()

    def test_crop_data_to_selected_range__normal_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", 5)
        plugin.set_param_value("fit_upper_limit", 20)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x <= 20).all())
        self.assertTrue((plugin._data_x >= 5).all())

    def test_crop_data_to_selected_range__low_limit_None(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", None)
        plugin.set_param_value("fit_upper_limit", 20)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x <= 20).all())

    def test_crop_data_to_selected_range__high_limit_None(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitSinglePeak")()
        plugin.set_param_value("fit_lower_limit", 5)
        plugin.set_param_value("fit_upper_limit", None)
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        self.assertTrue((plugin._data_x >= 5).all())

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

    def test_create_result_dataset__peak_outside_array(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin._fit_params["center"] = 0
        plugin.set_param_value("output", "Peak position")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertTrue(np.isnan(_new_data.array[0]))

    def test_create_result_dataset__high_std(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin._fit_params["amplitude"] = 1e6
        plugin.set_param_value("output", "Peak position")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertTrue(np.isnan(_new_data.array[0]))

    def test_create_result_dataset__peak_pos_and_area(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak position and area")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__fwhm(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "FWHM")
        _new_data = plugin._create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (1,))

    def test_create_result_dataset__peak_pos_and_area_and_fwhm(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("output", "Peak position, area and FWHM")
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

    def test_execute__gaussian_w_steep_1d_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _tmp_data = self._data + 3 * np.arange(self._data.size)
        _data, _kwargs = plugin.execute(_tmp_data)
        self.assertEqual(_data.shape, (1,))
        self.assertTrue("fit_params" in _data.metadata)
        self.assertTrue("fit_func" in _data.metadata)
        self.assertTrue("fit_residual_std" in _data.metadata)
        self.assertTrue(20 <= _kwargs["fit_params"]["amplitude"] <= 60)
        if "sigma" in _kwargs["fit_params"]:
            self.assertTrue(_kwargs["fit_params"]["sigma"] < 5)
        self.assertTrue(
            (_kwargs["fit_params"]["center"] < 22)
            & (_kwargs["fit_params"]["center"] > 20)
        )
        self.assertTrue(
            (_kwargs["fit_params"]["background_p1"] < 6.5)
            & (_kwargs["fit_params"]["background_p1"] > 5.5)
        )

    def test_execute__gaussian_w_only_background_and_min_peak(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin.set_param_value("fit_min_peak_height", 10)
        plugin.pre_execute()
        _tmp_data = Dataset(3 * np.arange(self._data.size))
        _data, _kwargs = plugin.execute(_tmp_data)

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

    def test_calculate_result_shape__fwhm(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "FWHM")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (1,))

    def test_calculate_result_shape__area_and_pos(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak position and area")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2,))

    def test_calculate_result_shape__area_pos_and_std(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("output", "Peak position, area and FWHM")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (3,))

    def test_calculate_result_shape__other(self):
        plugin = self.create_generic_plugin()
        plugin.params["output"].choices = plugin.params["output"].choices + ["dummy"]
        plugin.set_param_value("output", "dummy")
        with self.assertRaises(ValueError):
            plugin.calculate_result_shape()

    def test_detailed_results(self):
        plugin = self.create_generic_plugin()
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        _details = plugin.detailed_results
        self.assertEqual(set(_details.keys()), {None})

    def test_detailed_results__multidim(self):
        _data = np.tile(self._data, (3, 3, 1))
        _data.axis_labels = ("a", "b", "data")
        _data.axis_ranges = (
            np.array((0, 2, 4)),
            np.array((1, 5, 9)),
            np.arange(self._data.size),
        )
        _data.axis_units = ("u0", "u1", "u2")
        plugin = self.create_generic_plugin()
        plugin.pre_execute()
        _new_data, _kwargs = plugin.execute(_data)
        _details = plugin.detailed_results
        for _indices in itertools.product(np.arange(3), np.arange(3)):
            self.assertIn(
                _data.get_description_of_point(_indices + (None,)), _details.keys()
            )
        self.assertNotIn(None, _details.keys())


if __name__ == "__main__":
    unittest.main()
