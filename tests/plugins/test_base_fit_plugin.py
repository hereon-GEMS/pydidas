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

from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.fitting.gaussian import Gaussian
from pydidas.plugins import BaseFitPlugin, BasePlugin


class TestBaseFitPlugin(unittest.TestCase):
    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(
            np.ones(150), data_unit="data unit", axis_units=["ax_unit"]
        )
        self._x = np.arange(self._data.size) * 0.5
        self._peak_x = self._x[self._peakpos]
        self._data.axis_ranges = [self._x]

        self._sigma = 1.25
        self._amp = 25
        _peak = self._amp * Gaussian.func((1, self._sigma, 0), np.linspace(-4, 4, 15))
        self._data[self._peakpos - 7 : self._peakpos + 8] += _peak

    def tearDown(self):
        pass

    def create_generic_plugin(self):
        _low = 10
        _high = 37
        self._range = np.where((self._x >= _low) & (self._x <= _high))[0].size
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_lower_limit", _low)
        plugin.set_param_value("fit_upper_limit", _high)
        plugin.set_param_value("fit_output", "Peak position")
        plugin.calculate_result_shape()
        return plugin

    def create_gauss_plugin_with_dummy_fit(self):
        plugin = self.create_generic_plugin()
        plugin.set_param_value("fit_func", "Gaussian")
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

    def test_creation(self):
        plugin = BaseFitPlugin()
        self.assertIsInstance(plugin, BasePlugin)

    def test_is_basic_plugin__baseclass(self):
        for _plugin in [BaseFitPlugin, BaseFitPlugin()]:
            self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__subclass(self):
        class TestPlugin(BaseFitPlugin):
            pass

        for _plugin in [TestPlugin, TestPlugin()]:
            self.assertFalse(_plugin.is_basic_plugin())

    def test_pre_execute(self):
        _min_peak = 12.4
        _sigma = 0.42
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_min_peak_height", _min_peak)
        plugin.set_param_value("fit_sigma_threshold", _sigma)
        plugin.set_param_value("fit_bg_order", None)
        plugin.pre_execute()
        self.assertEqual(plugin._config["sigma_threshold"], _sigma)
        self.assertEqual(plugin._config["min_peak_height"], _min_peak)
        self.assertEqual(plugin._config["param_labels"], Gaussian.param_labels)
        self.assertEqual(plugin._config["param_bounds_low"], Gaussian.param_bounds_low)
        self.assertEqual(
            plugin._config["param_bounds_high"], Gaussian.param_bounds_high
        )

    def test_pre_execute__bg_order_0(self):
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_bg_order", 0)
        plugin.pre_execute()
        self.assertTrue("background_p0" in plugin._config["param_labels"])
        self.assertEqual(len(plugin._config["param_bounds_low"]), 4)
        self.assertEqual(len(plugin._config["param_bounds_high"]), 4)

    def test_pre_execute__bg_order_1(self):
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_bg_order", 1)
        plugin.pre_execute()
        self.assertTrue("background_p0" in plugin._config["param_labels"])
        self.assertTrue("background_p1" in plugin._config["param_labels"])
        self.assertEqual(len(plugin._config["param_bounds_low"]), 5)
        self.assertEqual(len(plugin._config["param_bounds_high"]), 5)

    def test_prepare_input_data(self):
        plugin = BaseFitPlugin()
        plugin._config["settings_updated_from_data"] = True
        plugin.prepare_input_data(self._data)
        self.assertTrue(np.all((self._data == plugin._data)))
        self.assertTrue(np.all((self._x == plugin._data_x)))

    def test_prepare_input_data__w_limits(self):
        plugin = BaseFitPlugin()
        plugin._config["settings_updated_from_data"] = True
        plugin.set_param_value("fit_lower_limit", 12)
        plugin.set_param_value("fit_upper_limit", 25)
        plugin.prepare_input_data(self._data)
        self.assertTrue(np.all((self._data[24:51] == plugin._data)))
        self.assertTrue(np.all((self._x[24:51] == plugin._data_x)))

    def test_update_peak_bounds_from_data(self):
        plugin = BaseFitPlugin()
        plugin.pre_execute()
        plugin.prepare_input_data(self._data)
        self.assertEqual(plugin._config["param_bounds_low"][2], np.amin(self._x))
        self.assertEqual(plugin._config["param_bounds_high"][2], np.amax(self._x))

    def test_update_peak_bounds_from_data__bounds_already_set(self):
        _low = self._x[4]
        _high = self._x[-7]
        plugin = BaseFitPlugin()
        plugin.pre_execute()
        plugin._config["param_bounds_low"][2] = _low
        plugin._config["param_bounds_high"][2] = _high
        plugin.prepare_input_data(self._data)
        self.assertEqual(plugin._config["param_bounds_low"][2], _low)
        self.assertEqual(plugin._config["param_bounds_high"][2], _high)

    def test_update_fit_param_bounds(self):
        _low = self._x[12]
        _high = self._x[-17]
        plugin = BaseFitPlugin()
        plugin.add_params(
            get_generic_param_collection("fit_peak_xlow", "fit_peak_xhigh")
        )
        plugin.set_param_value("fit_peak_xlow", _low)
        plugin.set_param_value("fit_peak_xhigh", _high)
        plugin.pre_execute()
        self.assertEqual(plugin._config["param_bounds_low"][2], _low)
        self.assertEqual(plugin._config["param_bounds_high"][2], _high)

    def test_create_fit_start_param_dict(self):
        _center = 12
        _sigma = 2.0
        plugin = BaseFitPlugin()
        plugin.add_params(
            get_generic_param_collection("fit_peak_xstart", "fit_peak_width")
        )
        plugin.set_param_value("fit_peak_xstart", _center)
        plugin.set_param_value("fit_peak_width", _sigma)
        plugin.pre_execute()
        _params = plugin._fit_presets
        self.assertEqual(_params["center_start"], _center)
        self.assertEqual(_params["width_start"], _sigma)

    def test_check_min_peak_height__None(self):
        plugin = BaseFitPlugin()
        plugin.pre_execute()
        plugin.prepare_input_data(self._data)
        self.assertTrue(plugin.check_min_peak_height())

    def test_check_min_peak_height__height_okay(self):
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_min_peak_height", 5)
        plugin.pre_execute()
        plugin.prepare_input_data(self._data)
        self.assertTrue(plugin.check_min_peak_height())

    def test_check_min_peak_height__height_too_small(self):
        plugin = BaseFitPlugin()
        plugin.set_param_value("fit_min_peak_height", 50)
        plugin.pre_execute()
        plugin.prepare_input_data(self._data)
        self.assertFalse(plugin.check_min_peak_height())


if __name__ == "__main__":
    unittest.main()
