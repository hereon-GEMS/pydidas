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

from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestRemoveOutliers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _len = 50
        _tzone = 20
        cls._section_length = _len
        cls._trans_zone = _tzone
        cls._peak_heights = [5, -5, 0.4, -0.4, 1.4, -1.4, 0.8, -0.8]
        data = np.ones(4 * _len + 3 * _tzone)
        data[_len : _len + _tzone] = np.linspace(1, -1, _tzone)
        data[_len + _tzone : 2 * _len + _tzone] = -1
        data[2 * _len + _tzone : 2 * _len + 2 * _tzone] = np.linspace(-1, 1, _tzone)
        data[3 * _len + 2 * _tzone : 3 * _len + 3 * _tzone] = np.linspace(1, -1, _tzone)
        data[3 * _len + 3 * _tzone :] = -1
        for _width in [1, 2]:
            _x0 = (_width - 1) * (2 * _len + 2 * _tzone)
            for _sign in [1, -1]:
                for _index, _peak in enumerate(cls._peak_heights):
                    _curr_x = (
                        3 + 5 * _index + _x0 + int(0.5 * (1 - _sign)) * (_len + _tzone)
                    )
                    data[_curr_x : _curr_x + _width] = _peak
        cls._data = data
        cls._x = np.arange(data.size)

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def find_peak_positions(self, threshold, kernel_width):
        _peaks = []
        _len = self._section_length
        _tzone = self._trans_zone
        for _width in range(1, 1 + kernel_width):
            _x0 = (_width - 1) * (2 * _len + 2 * _tzone)
            for _sign in [1, -1]:
                for _index, _peak in enumerate(self._peak_heights):
                    _curr_x = (
                        3 + 5 * _index + _x0 + int(0.5 * (1 - _sign)) * (_len + _tzone)
                    )
                    if (
                        abs((self._data[_curr_x] - _sign) / _sign) >= threshold
                        or abs((self._data[_curr_x] - _sign) / self._data[_curr_x])
                        >= threshold
                    ):
                        _peaks.append(_curr_x)
        return _peaks

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.pre_execute()
        # assert does not raise an Error

    def test_execute__w_kernel_1_thresh1(self):
        _thresh = 1
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 1)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 1)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)

    def test_execute__w_kernel_1_thresh4(self):
        _thresh = 4
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 1)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 1)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)

    def test_execute__w_kernel_1_thresh0p5(self):
        _thresh = 0.5
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 1)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 1)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)

    def test_execute__w_kernel_2_thresh_1(self):
        _thresh = 1
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 2)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 2)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)

    def test_execute__w_kernel_2_thresh_4(self):
        _thresh = 4
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 2)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 2)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)

    def test_execute__w_kernel_2_thresh_0p5(self):
        _thresh = 0.5
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 2)
        plugin.set_param_value("outlier_threshold", _thresh)
        _newdata, _ = plugin.execute(self._data.copy())
        _peaks = self.find_peak_positions(_thresh, 2)
        for _peak in _peaks:
            self.assertAlmostEqual(abs(_newdata[_peak]), 1)


if __name__ == "__main__":
    unittest.main()
