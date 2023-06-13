# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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

from pydidas.core.fitting.fit_func_base import FitFuncBase


FIT_CLASS = FitFuncBase


class TestFitFuncBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._x = np.arange(20)
        cls._y = np.random.random((cls._x.size))

    def test_class_params_okay(self):
        for _attribute in [
            "name",
            "param_bounds_low",
            "param_bounds_high",
            "param_labels",
        ]:
            self.assertTrue(hasattr(FIT_CLASS, _attribute))

    def test_func(self):
        _res = FIT_CLASS.func([], self._y)
        self.assertTrue(np.alltrue(_res == self._y))

    def test_profile(self):
        _result = FIT_CLASS.profile([], self._x)
        self.assertTrue(np.allclose(_result, self._x))

    def test_delta(self):
        _values = np.random.random((self._x.size))
        _result = FIT_CLASS.delta([], self._x, _values)
        self.assertTrue(np.allclose(_result, self._x - _values))

    def test_area(self):
        _input = [42.1, 12, 27]
        self.assertEqual(FIT_CLASS.area(_input), _input[0])

    def test_calculate_background_params__no_bg(self):
        _x = np.arange(20)
        _y = np.sin(_x / 3)
        _y_new, _bg_params = FIT_CLASS.calculate_background_params(_x, _y, None)
        self.assertTrue(np.allclose(_y, _y_new))
        self.assertEqual(_bg_params, [])

    def test_calculate_background_params__const_bg(self):
        _x = np.arange(20)
        _y = np.sin(_x / 3)
        _y_new, _bg_params = FIT_CLASS.calculate_background_params(_x, _y, 0)
        self.assertTrue(np.alltrue(_y_new >= 0))
        self.assertEqual(_bg_params, [np.amin(_y)])

    def test_calculate_background_params__bg_order1(self):
        _x = np.arange(20)
        _slope = -3
        _offset = 80
        _y = 10 * np.exp(-0.25 * (_x - 8) ** 2) + _slope * _x + _offset
        _y_new, _bg_params = FIT_CLASS.calculate_background_params(_x, _y, 1)
        self.assertTrue(np.alltrue(_y_new >= -1e-6))
        self.assertTrue(abs(_slope - _bg_params[1]) < 0.1)
        self.assertTrue(abs(_offset - _bg_params[0]) < 0.1)

    def test_calculate_background_params__wrong_bg_order(self):
        _x = np.arange(20)
        _y = np.sin(_x / 3)
        with self.assertRaises(ValueError):
            FIT_CLASS.calculate_background_params(_x, _y, 4)

    def test_get_fwhm_indices__single_range_x_in(self):
        _x = np.linspace(-0.5 * np.pi, 1.5 * np.pi, num=41)
        _y = np.sin(_x)
        _x0 = (_x[19] + _x[20]) / 2
        _y0 = np.sin(_x0)
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.alltrue(np.where(_y >= 0.5 * _y0)[0] == _range))

    def test_get_fwhm_indices__empty_range(self):
        _x = 0.4 * np.arange(30) + 2
        _y = np.ones(_x.size)
        _range = FIT_CLASS.get_fwhm_indices(_x[15], 3, _x, _y)
        self.assertTrue(np.alltrue(np.array([]) == _range))

    def test_get_fwhm_indices__adjacent_jumps(self):
        _x = 0.4 * np.arange(30) + 2
        _y = np.zeros(_x.size)
        _y[2:5] = 1
        _y[9] = 1
        _y[15:18] = 1
        _range = FIT_CLASS.get_fwhm_indices(_x[3], 1, _x, _y)
        self.assertTrue(np.alltrue(np.arange(2, 5) == _range))

    def test_get_fwhm_indices__double_range_x_in(self):
        _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
        _y = np.sin(_x)
        _x0 = (_x[15] + _x[14]) / 2
        _y0 = np.sin(_x0)
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.alltrue(np.where(_y[:31] >= 0.5 * _y0)[0] == _range))

    def test_get_fwhm_indices__double_range_x_out(self):
        _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
        _y = np.sin(_x)
        _x0 = np.pi
        _y0 = 1
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.alltrue(np.array([]) == _range))


if __name__ == "__main__":
    unittest.main()
