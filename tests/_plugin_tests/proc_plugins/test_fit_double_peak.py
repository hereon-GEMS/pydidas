# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import itertools
import unittest

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset
from pydidas.core.fitting.gaussian import Gaussian
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestFitDoublePeak(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        self._data = Dataset(
            np.ones((150)), data_unit="data unit", axis_units=["ax_unit"]
        )
        self._x = np.arange(self._data.size) * 0.5
        _index1 = 42
        _index2 = 48
        self._peak_x1 = self._x[_index1]
        self._peak_x2 = self._x[_index2]
        self._data.axis_ranges = [self._x]

        self._sigma = 1.25
        self._amp1 = 25
        self._amp2 = 37
        _peak = Gaussian.func((1, self._sigma, 0), np.linspace(-4, 4, 15))
        self._data[_index1 - 7 : _index1 + 8] += self._amp1 * _peak
        self._data[_index2 - 7 : _index2 + 8] += self._amp2 * _peak

    def tearDown(self):
        pass

    def create_generic_plugin(self, func="Double Gaussian"):
        _low = 10
        _high = 37
        self._rangen = np.where((self._x >= _low) & (self._x <= _high))[0].size
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitDoublePeak")()
        plugin._config["input_shape"] = (150,)
        plugin.set_param_value("fit_func", func)
        plugin.set_param_value("fit_lower_limit", _low)
        plugin.set_param_value("fit_upper_limit", _high)
        plugin.set_param_value("fit_output", "position")
        plugin.calculate_result_shape()
        return plugin

    def create_gauss_plugin_with_dummy_fit(self):
        plugin = self.create_generic_plugin()
        plugin._data = self._data
        plugin._data_x = self._data.axis_ranges[0]
        plugin._crop_data_to_selected_range()
        plugin.pre_execute()
        _startguess = plugin._fitter.guess_fit_start_params(
            plugin._data_x,
            plugin._data,
            bg_order=plugin.get_param_value("fit_bg_order"),
        )
        plugin._fit_params = dict(zip(plugin._config["param_labels"], _startguess))
        self._dummy_metadata = {"test_meta": 123}
        plugin._data.metadata = plugin._data.metadata | self._dummy_metadata
        return plugin

    def assert_fit_results_okay(self, fit_result_data, params, bg_order):
        self.assertEqual(fit_result_data.shape, (2,))
        self.assertTrue("fit_params" in fit_result_data.metadata)
        self.assertTrue("fit_func" in fit_result_data.metadata)
        self.assertTrue("fit_residual_std" in fit_result_data.metadata)
        self.assertTrue(abs(params["amplitude0"] - self._amp1) <= 20)
        self.assertTrue(abs(params["amplitude1"] - self._amp2) <= 20)
        if "sigma" in params:
            self.assertTrue(abs(params["sigma0"] - self._sigma) < 0.5)
        if "gamma" in params:
            self.assertTrue(abs(params["gamma0"] - self._sigma) < 0.5)
        self.assertTrue(abs(params["center0"] - self._peak_x1) < 1)
        self.assertTrue(abs(params["center1"] - self._peak_x2) < 2)
        if bg_order in [0, 1]:
            self.assertTrue(abs(params["background_p0"] - 1) < 1)
        if bg_order == 1:
            self.assertTrue(abs(params["background_p1"]) < 1)

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitDoublePeak")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_create_result_dataset__peak_area(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("fit_output", "area")
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__peak_position(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("fit_output", "position")
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__peak_outside_array(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin._fit_params["center"] = 0
        plugin.set_param_value("fit_output", "position")
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertTrue(np.isnan(_new_data.array[0]))

    def test_create_result_dataset__high_std(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin._fit_params["amplitude"] = 1e6
        plugin.set_param_value("fit_output", "position")
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertTrue(np.isnan(_new_data.array[0]))
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__peak_pos_and_area(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("fit_output", "position; area")
        plugin.calculate_result_shape()
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2, 2))

    def test_create_result_dataset__fwhm(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("fit_output", "FWHM")
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2,))

    def test_create_result_dataset__peak_pos_and_area_and_fwhm(self):
        plugin = self.create_gauss_plugin_with_dummy_fit()
        plugin.set_param_value("fit_output", "position; area; FWHM")
        plugin.calculate_result_shape()
        _new_data = plugin.create_result_dataset()
        self.assertTrue("fit_params" in _new_data.metadata)
        self.assertTrue("fit_func" in _new_data.metadata)
        self.assertTrue("fit_residual_std" in _new_data.metadata)
        self.assertTrue("test_meta" in _new_data.metadata)
        self.assertEqual(_new_data.shape, (2, 3))

    def test_execute__gaussian_no_bg(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data - 0.5)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)
        self.assertIn(self._data.axis_units[0], _data.data_label)

    def test_execute__gaussian_no_bg_all_outputs(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", None)
        plugin.set_param_value("fit_output", "position; area; FWHM")
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assertEqual(_data.shape, (2, 3))

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
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)
        self.assertTrue(abs(_kwargs["fit_params"]["background_p1"] - 6) < 0.5)

    def test_execute__gaussian_w_only_background_and_min_peak(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin.set_param_value("fit_min_peak_height", 10)
        plugin.pre_execute()
        _tmp_data = Dataset(3 * np.arange(self._data.size))
        _data, _kwargs = plugin.execute(_tmp_data)

    def test_execute__lorentzian_no_bg(self):
        plugin = self.create_generic_plugin("Double Lorentzian")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)

    def test_execute__lorentzian_0d_bg(self):
        plugin = self.create_generic_plugin("Double Lorentzian")
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 0)

    def test_execute__lorentzian_1d_bg(self):
        plugin = self.create_generic_plugin("Double Lorentzian")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 1)

    def test_execute__voigt_no_bg(self):
        plugin = self.create_generic_plugin("Double Voigt")
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], None)

    def test_execute__voigt_0d_bg(self):
        plugin = self.create_generic_plugin("Double Voigt")
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 0)

    def test_execute__voigt_1d_bg(self):
        plugin = self.create_generic_plugin("Double Voigt")
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs["fit_params"], 1)

    def test_calculate_result_shape__area(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_output", "area")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2,))

    def test_calculate_result_shape__position(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_output", "position")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2,))

    def test_calculate_result_shape__fwhm(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_output", "FWHM")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2,))

    def test_calculate_result_shape__area_and_pos(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_output", "position; area")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2, 2))

    def test_calculate_result_shape__area_pos_and_std(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_output", "position; area; FWHM")
        plugin.calculate_result_shape()
        self.assertEqual(plugin._config["result_shape"], (2, 3))

    def test_detailed_results(self):
        plugin = self.create_generic_plugin()
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data, store_details=True)
        _details = plugin.detailed_results
        self.assertEqual(set(_details.keys()), {None})

    def test_detailed_results__multidim(self):
        _data = np.tile(self._data, (3, 3, 1))
        _data.axis_labels = ("a", "b", "data")
        _data.axis_ranges = (
            np.array((0, 2, 4)),
            np.array((1, 5, 9)),
            np.arange(self._data.size) / 2,
        )
        _data.axis_units = ("u0", "u1", "u2")
        plugin = self.create_generic_plugin()
        plugin.pre_execute()
        _new_data, _kwargs = plugin.execute(_data, store_details=True)
        _details = plugin.detailed_results
        for _indices in itertools.product(np.arange(3), np.arange(3)):
            self.assertIn(
                _data.get_description_of_point(_indices + (None,)), _details.keys()
            )
        self.assertNotIn(None, _details.keys())


if __name__ == "__main__":
    unittest.main()
