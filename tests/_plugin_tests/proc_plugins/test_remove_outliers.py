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
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

import numpy as np

from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestRemoveOutliers(unittest.TestCase):

    def setUp(self):
        self._n = 120
        self._outliers_width_one = {7: 2.5, 23: 0.45, 31: 0.6, 56: 1.2, 75: 12}
        self._outliers_width_two = {12: 1.5, 67: 0.4, 89: 0.6, 105: 3.2}
        self._data = np.arange(self._n) + 1
        self._rawdata = self._data.copy()
        for _key, _factor in self._outliers_width_one.items():
            self._data[_key] = self._data[_key] * _factor
        for _key, _factor in self._outliers_width_two.items():
            self._data[_key] = self._data[_key] * _factor
            self._data[_key + 1] = self._data[_key + 1] * _factor

    def tearDown(self):
        ...

    def assert_data_width_one_okay(self, data, threshold):
        for _index, _factor in self._outliers_width_one.items():
            _rel_delta = abs((data[_index] - self._rawdata[_index])
                             / self._rawdata[_index])
            self.assertTrue(_rel_delta <= threshold)
            if 1 / threshold <= _factor <= threshold:
                self.assertAlmostEqual(data[_index], self._data[_index])

    def assert_data_width_two_okay(self, data, threshold):
        for _index, _factor in self._outliers_width_two.items():
            for _offset in [0, 1]:
                _rel_delta = abs((data[_index + _offset]
                                  - self._rawdata[_index + _offset])
                                 / self._rawdata[_index + _offset])
                self.assertTrue(_rel_delta <= threshold)
                if 1 / threshold <= _factor <= threshold:
                    self.assertAlmostEqual(data[_index + _offset],
                                           self._data[_index + _offset])

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_execute__w_kernel_1_thresh1(self):
        _thresh = 1
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        plugin.set_param_value('kernel_width', 1)
        plugin.set_param_value('outlier_threshold', _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        self.assert_data_width_one_okay(_newdata, _thresh)

    def test_execute__w_kernel_1_thresh5(self):
        _thresh = 5
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        plugin.set_param_value('kernel_width', 1)
        plugin.set_param_value('outlier_threshold', _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        self.assert_data_width_one_okay(_newdata, _thresh)

    def test_execute__w_kernel_2_thresh1(self):
        _thresh = 1
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        plugin.set_param_value('kernel_width', 2)
        plugin.set_param_value('outlier_threshold', _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        self.assert_data_width_one_okay(_newdata, _thresh)
        self.assert_data_width_two_okay(_newdata, _thresh)

    def test_execute__w_kernel_2_thresh5(self):
        _thresh = 5
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('RemoveOutliers')()
        plugin.set_param_value('kernel_width', 2)
        plugin.set_param_value('outlier_threshold', _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        self.assert_data_width_one_okay(_newdata, _thresh)
        self.assert_data_width_two_okay(_newdata, _thresh)


if __name__ == "__main__":
    unittest.main()
