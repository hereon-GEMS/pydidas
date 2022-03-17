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

from pydidas.core import AppConfigError,  Dataset
from pydidas.core.constants import GAUSSIAN, LORENTZIAN, PSEUDO_VOIGT
from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestFitSinglePeak(unittest.TestCase):

    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(np.ones((150)))
        self._x = np.arange(self._data.size) * 0.5
        self._peak_x = self._x[self._peakpos]
        self._data.axis_ranges[0] = self._x
        self._data[self._peakpos - 5: self._peakpos + 6] = [
            0.5, 1.6, 4, 7.2, 10.5, 12, 10.5, 7.2, 4, 1.5, 0.5]

    def tearDown(self):
        pass

    def create_gauss_plugin(self):
        _low = 10
        _high = 30
        self._rangen = np.where((self._x >= _low) & (self._x <= _high))[0].size
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_func', 'Gaussian')
        plugin.set_param_value('fit_lower_limit', _low)
        plugin.set_param_value('fit_upper_limit', _high)
        return plugin

    def assert_fit_results_okay(self, fit_result_data, params, bg_order):
        _nparams = 4 + bg_order if bg_order is not None else 3
        self.assertEqual(fit_result_data.shape, (3, self._rangen))
        self.assertEqual(len(params), _nparams)
        self.assertTrue('fit_params' in fit_result_data.metadata)
        self.assertTrue('fit_func' in fit_result_data.metadata)
        self.assertTrue('fit_param_labels' in fit_result_data.metadata)
        self.assertTrue((params[0] < 15) & (params[0] > 5))
        self.assertTrue(params[1] < 5)
        self.assertTrue((params[2] < 22) & (params[2] > 20))
        if bg_order in [0, 1]:
            self.assertTrue((params[3] < 1) & (params[3] > 0))
        if bg_order == 1:
            self.assertTrue((params[4] < 1) & (params[4] > -1))

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__gaussian(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_func', 'Gaussian')
        plugin.pre_execute()
        self.assertEqual(plugin._ffunc, GAUSSIAN)
        self.assertEqual(plugin._fitparam_labels, [])
        self.assertEqual(plugin._fitparam_startpoints, [])

    def test_pre_execute__lorentzian(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_func', 'Lorentzian')
        plugin.pre_execute()
        self.assertEqual(plugin._ffunc, LORENTZIAN)
        self.assertEqual(plugin._fitparam_labels, [])
        self.assertEqual(plugin._fitparam_startpoints, [])

    def test_pre_execute__voigt(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_func', 'Pseudo-Voigt')
        plugin.pre_execute()
        self.assertEqual(plugin._ffunc, PSEUDO_VOIGT)
        self.assertEqual(plugin._fitparam_labels, ['fraction'])
        self.assertEqual(plugin._fitparam_startpoints, [0.5])

    def test_get_data_range__no_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        with self.assertRaises(AppConfigError):
            plugin._get_data_range(self._data)

    def test_get_data_range__empty_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_lower_limit', 42)
        plugin.set_param_value('fit_upper_limit', 2)
        with self.assertRaises(AppConfigError):
            plugin._get_data_range(self._data)

    def test_get_data_range__normal_limits(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FitSinglePeak')()
        plugin.set_param_value('fit_lower_limit', 0)
        plugin.set_param_value('fit_upper_limit', 20)
        _x, _data = plugin._get_data_range(self._data)
        self.assertTrue((_x <= 20).all())
        self.assertTrue((_x >= 0).all())

    def test_update_fit_startparams__no_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', None)
        _x, _data = plugin._get_data_range(self._data)
        plugin._update_fit_startparams(_x, _data)
        self.assertEqual(plugin._fitparam_labels,
                          ['amplitude', 'sigma', 'center'])
        self.assertEqual(len(plugin._fitparam_startpoints), 3)
        self.assertEqual(len(plugin._fitparam_bounds[0]), 3)
        self.assertEqual(len(plugin._fitparam_bounds[1]), 3)

    def test_update_fit_startparams__0order_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', 0)
        _x, _data = plugin._get_data_range(self._data)
        plugin._update_fit_startparams(_x, _data)
        self.assertEqual(plugin._fitparam_labels,
                          ['amplitude', 'sigma', 'center', 'background p0'])
        self.assertEqual(len(plugin._fitparam_startpoints), 4)
        self.assertEqual(len(plugin._fitparam_bounds[0]), 4)
        self.assertEqual(len(plugin._fitparam_bounds[1]), 4)

    def test_update_fit_startparams__1order_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', 1)
        _x, _data = plugin._get_data_range(self._data)
        plugin._update_fit_startparams(_x, _data)
        self.assertEqual(plugin._fitparam_labels,
                          ['amplitude', 'sigma', 'center', 'background p0',
                          'background p1'])
        self.assertEqual(len(plugin._fitparam_startpoints), 5)
        self.assertEqual(len(plugin._fitparam_bounds[0]), 5)
        self.assertEqual(len(plugin._fitparam_bounds[1]), 5)

    def test_create_new_dataset__simple(self):
        plugin = self.create_gauss_plugin()
        _x, _data = plugin._get_data_range(self._data)
        _data.metadata['test_meta'] = 123
        plugin.pre_execute()
        plugin._update_fit_startparams(_x, _data)
        _new_data = plugin._create_new_dataset(_x, _data,
                                                plugin._fitparam_startpoints)
        self.assertTrue('fit_params' in _new_data.metadata)
        self.assertTrue('fit_func' in _new_data.metadata)
        self.assertTrue('fit_param_labels' in _new_data.metadata)
        self.assertTrue('test_meta' in _new_data.metadata)
        self.assertEqual(_new_data.axis_labels[0], 'Data and fit')
        self.assertEqual(_new_data.axis_ranges[0], ['data', 'fit', 'residual'])

    def test_execute__gaussian_no_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], None)

    def test_execute__gaussian_0d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], 0)

    def test_execute__gaussian_1d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_bg_order', 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], 1)

    def test_execute__lorentzian_no_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Lorentzian')
        plugin.set_param_value('fit_bg_order', None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], None)

    def test_execute__lorentzian_0d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Lorentzian')
        plugin.set_param_value('fit_bg_order', 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], 0)

    def test_execute__lorentzian_1d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Lorentzian')
        plugin.set_param_value('fit_bg_order', 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'], 1)

    def test_execute__voigt_no_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Pseudo-Voigt')
        plugin.set_param_value('fit_bg_order', None)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(0 <= _kwargs['fit_params'][0] <= 1)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'][1:], None)

    def test_execute__voigt_0d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Pseudo-Voigt')
        plugin.set_param_value('fit_bg_order', 0)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(0 <= _kwargs['fit_params'][0] <= 1)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'][1:], 0)

    def test_execute__voigt_1d_bg(self):
        plugin = self.create_gauss_plugin()
        plugin.set_param_value('fit_func', 'Pseudo-Voigt')
        plugin.set_param_value('fit_bg_order', 1)
        plugin.pre_execute()
        _data, _kwargs = plugin.execute(self._data)
        self.assertTrue(0 <= _kwargs['fit_params'][0] <= 1)
        self.assert_fit_results_okay(_data, _kwargs['fit_params'][1:], 1)


if __name__ == "__main__":
    unittest.main()
