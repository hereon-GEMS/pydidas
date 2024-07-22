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
__copyright__ = "Copyright  2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np

from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.core.utils import (
    calculate_histogram_limits,
)
from pydidas.data_io import import_data


class TestImageUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qsettings = PydidasQsettings()
        cls._std_low = cls.qsettings.value(
            "user/histogram_outlier_fraction_low", dtype=float
        )
        cls._std_high = cls.qsettings.value(
            "user/histogram_outlier_fraction_high", dtype=float
        )

    def tearDown(self):
        self.qsettings.set_value("user/histogram_outlier_fraction_low", self._std_low)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", self._std_high)

    def test_calculate_histogram_limits__wrong_limits(self):
        data = np.arange(100**2).reshape((100, 100))
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.6)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.4)
        with self.assertRaises(UserConfigError):
            calculate_histogram_limits(data)

    def test_calculate_histogram_limits__simple(self):
        raw_data = np.arange(100**2)
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
        for _offset in [0, -500, -5e4, 12000, 120000]:
            with self.subTest(offset=_offset):
                data = raw_data + _offset
                low, high = calculate_histogram_limits(data)
                self.assertTrue(abs(low - (500 + _offset)) < 25)
                self.assertTrue(abs(high - (9500 + _offset)) < 25)

    def test_calculate_histogram_limits__only_high_lim_very_low(self):
        raw_data = np.arange(1000**2)
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 1 - 1e-6)
        data = raw_data
        low, high = calculate_histogram_limits(data)
        self.assertIsNone(low)
        self.assertAlmostEqual(high, 0)

    def test_calculate_histogram_limits__constant_arr_values(self):
        raw_data = np.ones(100**2)
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
        data = raw_data
        low, high = calculate_histogram_limits(data)
        print("flat data: ", low, high)
        # self.assertTrue(abs(low - (500 + _offset)) < 25)
        # self.assertTrue(abs(high - (9500 + _offset)) < 25)

    def test_calculate_histogram_limits__no_upper_limit(self):
        raw_data = np.arange(100**2)
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0)
        for _offset in [0, -500, -5e4, 12000, 120000]:
            with self.subTest(offset=_offset):
                data = raw_data + _offset
                low, high = calculate_histogram_limits(data)
                self.assertTrue(abs(low - (500 + _offset)) < 25)
                self.assertIsNone(high)

    def test_calculate_histogram_limits__no_lower_limit(self):
        raw_data = np.arange(100**2)
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.0)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
        for _offset in [0, -500, -5e4, 12000, 120000]:
            with self.subTest(offset=_offset):
                data = raw_data + _offset
                low, high = calculate_histogram_limits(data)
                self.assertIsNone(low)
                self.assertTrue(abs(high - (9500 + _offset)) < 25)

    def test_calculate_histogram_limits__big_low_outlier(self):
        raw_data = 0.01 * np.arange(1000**2)
        raw_data[0] = -1e6
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
        for _offset in [0 , -500, -5e4, 12000, 120000]:
            with self.subTest(offset=_offset):
                _tolerance = 400 * (1 + abs(_offset) / 1e5)
                data = raw_data + _offset
                low, high = calculate_histogram_limits(data)
                self.assertTrue(abs(low - (500 + _offset)) < _tolerance)
                self.assertTrue(abs(high - (9500 + _offset)) < _tolerance)

    def test_calculate_histogram_limits__real_data(self):
        raw_data = import_data(r"E:\_data\David_Canelo\T6_Malte\T6_Centre-00141.tif")
        self.qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
        self.qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
        _tolerance = 400
        data = raw_data
        low, high = calculate_histogram_limits(data)
        # self.assertTrue(abs(low - (500 + _offset)) < _tolerance)
        # self.assertTrue(abs(high - (9500 + _offset)) < _tolerance)


if __name__ == "__main__":
    unittest.main()
