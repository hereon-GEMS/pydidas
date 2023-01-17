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
        cls.config = {
            "zone_n": 125,
            "trans_n": 20,
            "max_width": 4,
            "peak_heights": [
                5.5,
                -5.5,
                0.4,
                -0.4,
                1.5,
                -1.5,
                0.8,
                -0.8,
                2.1,
                -2.1,
                3.5,
                -3.5,
            ],
        }
        cls._peaks = []
        cls._create_base_data()
        cls._add_peaks_to_data()
        cls._add_noise_to_data()

    @classmethod
    def _create_base_data(cls):
        """
        Create the base data background.
        """
        _cfg = cls.config
        _zone_len = 2 * (_cfg["zone_n"] + _cfg["trans_n"])
        data = np.ones((_cfg["max_width"] * 12 * _zone_len))
        for _index_width in range(_cfg["max_width"]):
            _i0 = _index_width * 12 * _zone_len
            for _index_cycle in range(12):
                _i_temp = _i0 + _index_cycle * _zone_len
                data[_i_temp : _i_temp + _cfg["trans_n"]] = np.linspace(
                    -1, 1, _cfg["trans_n"]
                )
                _i_temp += _cfg["trans_n"]
                data[_i_temp : _i_temp + _cfg["zone_n"]] = 1
                _i_temp += _cfg["zone_n"]
                data[_i_temp : _i_temp + _cfg["trans_n"]] = np.linspace(
                    1, -1, _cfg["trans_n"]
                )
                _i_temp += _cfg["trans_n"]
                data[_i_temp : _i_temp + _cfg["zone_n"]] = -1
        cls._base_data = data
        cls._is_noisy = np.zeros((cls._base_data.size), dtype=bool)

    @classmethod
    def _add_peaks_to_data(cls):
        """
        Add the peaks to the base background.
        """
        _cfg = cls.config
        _data = cls._base_data.copy()
        for _index_width, _width in enumerate(range(1, _cfg["max_width"] + 1)):
            _i0 = _index_width * 24 * (_cfg["zone_n"] + _cfg["trans_n"])
            for _index_cycle in range(24):
                for _index_peak, _peak_y in enumerate(_cfg["peak_heights"]):
                    _true_width = _width
                    _tail = None
                    _f = None
                    _i_peak = (
                        _i0
                        + _index_cycle * (_cfg["zone_n"] + _cfg["trans_n"])
                        + 10 * _index_peak
                        + _cfg["trans_n"]
                        + 5
                    )
                    _bg_level = _data[_i_peak]
                    _data[_i_peak : _i_peak + _width] = _peak_y
                    if _index_cycle % 12 in [2, 3, 4, 5]:
                        _tail = "right"
                        _f = 0.4 if _index_cycle % 12 in [2, 3] else 0.6
                        _true_width = _width + _f
                        _data[_i_peak + _width] = _f * _peak_y + (1 - _f) * _bg_level
                    elif _index_cycle % 12 in [6, 7, 8, 9]:
                        _tail = "left"
                        _f = 0.4 if _index_cycle % 12 in [6, 7] else 0.6
                        _true_width = _width + _f
                        _data[_i_peak - 1] = _f * _peak_y + (1 - _f) * _bg_level
                    elif _index_cycle % 12 in [10, 11]:
                        _tail = "both"
                        _f = 0.4 if _index_cycle % 12 == 10 else 0.6
                        _true_width = _width + 1.5
                        _data[_i_peak - 1] = _f * _peak_y + (1 - _f) * _bg_level
                        _data[_i_peak + _width] = _f * _peak_y + (1 - _f) * _bg_level
                    cls._peaks.append(
                        [_i_peak, _width, _true_width, _peak_y, _bg_level, _tail, _f]
                    )
        cls._data = _data
        cls._noisefree_data = cls._data.copy()

    @classmethod
    def _add_noise_to_data(cls):
        """
        Add the peaks to the base background.
        """
        _cfg = cls.config
        cls._noisefree_data = cls._data.copy()
        _noise = 0.04 * (
            np.cos(np.arange(cls._data.size) * 1.77)
            + np.sin(np.arange(cls._data.size) * 2.783)
            + np.cos(np.arange(cls._data.size) * 3.17)
            + np.sin(np.arange(cls._data.size) * 1.37)
        )
        for _index_width, _width in enumerate(range(1, _cfg["max_width"] + 1)):
            _i0 = _index_width * 24 * (_cfg["zone_n"] + _cfg["trans_n"]) + 12 * (
                _cfg["zone_n"] + _cfg["trans_n"]
            )
            _i_end = _i0 + 12 * (_cfg["zone_n"] + _cfg["trans_n"])
            cls._data[_i0:_i_end] += _noise[_i0:_i_end]
            cls._is_noisy[_i0:_i_end] = True

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def get_peak_positions(self, threshold, kernel_width):
        _correct_peaks = []
        for _index, _top_width, _width, _height, _bg, _tail, _tail_f in self._peaks:
            _peak = abs(_height - _bg)
            if _peak >= threshold and kernel_width >= _width:
                _correct_peaks.append(_index)
                _full_width = int(np.floor(_width))
                _w = 0
                _correct_peaks.extend([_index + _w for _w in range(1, _full_width)])
                if _width > _full_width and _tail in ["left", "both"]:
                    _correct_peaks.append(_index - 1)
                if _width > _full_width and _tail in ["right", "both"]:
                    _correct_peaks.append(_index + _w + 1)
            elif _peak >= threshold and kernel_width >= _top_width and _tail == "both":
                _tail_y = _tail_f * _height + (1 - _tail_f) * _bg
                _ref = (
                    _tail_y
                    - 0.5 * self._noisefree_data[_index - kernel_width - 2]
                    - 0.5 * self._noisefree_data[_index + kernel_width]
                )
                _check = (
                    _ref > -0.3 * threshold if _height < _bg else _ref < 0.3 * threshold
                )
                if _check:
                    _correct_peaks.extend([_index + _w for _w in range(_top_width)])
        return _correct_peaks

    def get_data_without_peaks(self, threshold, kernel_width):
        _peaks = self.get_peak_positions(threshold, kernel_width)
        _new_data = self._data.copy()
        _new_data[_peaks] = self._base_data[_peaks]
        return _new_data

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
        plugin.pre_execute()
        _newdata, _ = plugin.execute(self._data.copy())
        _ref = self.get_data_without_peaks(_thresh, 1)
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        _indices = np.where(abs(_newdata - _ref) > 0.25)[0]
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        self.assertTrue(_indices.size <= 3)

    def test_execute__w_kernel_1_thresh4(self):
        _thresh = 4
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 1)
        plugin.set_param_value("outlier_threshold", _thresh)
        plugin.pre_execute()
        _newdata, _ = plugin.execute(self._data.copy())
        _ref = self.get_data_without_peaks(_thresh, 1)
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        _noisy_delta = _newdata[self._is_noisy] - _ref[self._is_noisy]
        self.assertTrue(np.alltrue((-0.25 <= _noisy_delta) & (_noisy_delta <= 0.25)))

    def test_execute__w_kernel_1_thresh0p55(self):
        _thresh = 0.55
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 1)
        plugin.set_param_value("outlier_threshold", _thresh)
        plugin.pre_execute()
        _newdata, _ = plugin.execute(self._data.copy())
        _ref = self.get_data_without_peaks(_thresh, 1)
        _indices = np.where(abs(_newdata - _ref) > 0.25)[0]
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        self.assertTrue(_indices.size <= 3)

    def test_execute__w_kernel_2_thresh_1(self):
        _thresh = 1
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", 2)
        plugin.set_param_value("outlier_threshold", _thresh)
        plugin.pre_execute()
        _newdata, _ = plugin.execute(self._data.copy())
        _ref = self.get_data_without_peaks(_thresh, 2)
        _indices = np.where(abs(_newdata - _ref) > 0.25)[0]
        for _index in _indices:
            print(_index, self._data[_index], self._noisefree_data[_index])
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        _noisy_delta = _newdata[self._is_noisy] - _ref[self._is_noisy]
        self.assertTrue(np.alltrue((-0.25 <= _noisy_delta) & (_noisy_delta <= 0.25)))

    def test_execute__w_kernel_2_thresh_4(self):
        _thresh = 4
        _kernel = 2
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("RemoveOutliers")()
        plugin.set_param_value("kernel_width", _kernel)
        plugin.set_param_value("outlier_threshold", _thresh)
        plugin.pre_execute()
        _newdata, _ = plugin.execute(self._data.copy())
        _ref = self.get_data_without_peaks(_thresh, _kernel)
        self.assertTrue(np.allclose(_newdata[~self._is_noisy], _ref[~self._is_noisy]))
        _noisy_delta = _newdata[self._is_noisy] - _ref[self._is_noisy]
        self.assertTrue(np.alltrue((-0.25 <= _noisy_delta) & (_noisy_delta <= 0.25)))


if __name__ == "__main__":
    unittest.main()
