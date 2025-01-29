# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np

from pydidas.core import Dataset
from pydidas.core.fitting.lorentzian import Lorentzian


class TestLorentzian(unittest.TestCase):
    def setUp(self):
        self._x = np.linspace(0, 10, num=2000)
        self._gamma = 1.42
        self._x0 = self._x[987]
        self._amplitude = 7.3
        self._data = Dataset(
            (
                self._amplitude
                * (self._gamma / np.pi)
                / ((self._x - self._x0) ** 2 + self._gamma**2)
            ),
            data_unit="data unit",
            axis_units=["ax_unit"],
            axis_ranges=[self._x],
        )
        self._params = (self._amplitude, self._gamma, self._x0)

    def tearDown(self):
        pass

    def test_guess_peak_start_params__narrow_peak(self):
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Lorentzian.guess_fit_start_params(self._x, _data)
        self.assertTrue(_params[1] > 0)

    def test_guess_peak_start_params__normal_peak(self):
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Lorentzian.guess_fit_start_params(self._x, self._data)
        self.assertTrue(_params[1] > 0)

    def test_guess_peak_start_params__bounds__peak_x_low(self):
        _bounds = (
            Lorentzian.param_bounds_low[:],
            Lorentzian.param_bounds_high[:],
        )
        _bounds[0][2] = self._x[42]
        _bounds[1][2] = self._x[50]
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Lorentzian.guess_fit_start_params(self._x, self._data, bounds=_bounds)
        self.assertTrue(_bounds[0][2] <= _params[2] <= _bounds[1][2])
        self.assertTrue(_params[1] > 0)

    def test_guess_peak_start_params__bounds__peak_x_high(self):
        _bounds = (
            Lorentzian.param_bounds_low[:],
            Lorentzian.param_bounds_high[:],
        )
        _bounds[0][2] = self._x[35]
        _bounds[1][2] = self._x[38]
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Lorentzian.guess_fit_start_params(self._x, self._data, bounds=_bounds)
        self.assertTrue(_bounds[0][2] <= _params[2] <= _bounds[1][2])
        self.assertTrue(_params[1] > 0)

    def test_func__values(self):
        _func_values = Lorentzian.func(self._params, self._x)
        self.assertTrue(np.allclose(self._data, _func_values))

    def test_amplitude(self):
        _amp = Lorentzian.amplitude(self._params)
        self.assertAlmostEqual(np.amax(self._data), max(_amp))

    def test_fwhm(self):
        _y_max = np.amax(self._data)
        _indices = np.where(self._data >= 0.5 * _y_max)[0]
        _fwhm = self._x[_indices[-1]] - self._x[_indices[0]]
        self.assertTrue(
            abs(_fwhm - Lorentzian.fwhm(self._params)) <= 2 * (self._x[1] - self._x[0])
        )


if __name__ == "__main__":
    unittest.main()
