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
from pydidas.core.fitting.triple_gaussian import TripleGaussian


class TestTripleGaussian(unittest.TestCase):
    def setUp(self):
        self._x = np.linspace(0, 10, num=2001)
        self._amplitude1 = 7.3
        self._sigma1 = 0.42
        self._x1 = self._x[543]
        self._amplitude2 = 12.4
        self._sigma2 = 0.22
        self._x2 = self._x[997]
        self._amplitude3 = 3.3
        self._sigma3 = 0.12
        self._x3 = self._x[1487]
        self._data = Dataset(
            (
                self._amplitude1
                / (self._sigma1 * np.sqrt(2 * np.pi))
                * np.exp(-((self._x - self._x1) ** 2) / (2 * self._sigma1**2))
                + self._amplitude2
                / (self._sigma2 * np.sqrt(2 * np.pi))
                * np.exp(-((self._x - self._x2) ** 2) / (2 * self._sigma2**2))
                + self._amplitude3
                / (self._sigma3 * np.sqrt(2 * np.pi))
                * np.exp(-((self._x - self._x3) ** 2) / (2 * self._sigma3**2))
            ),
            data_unit="data unit",
            axis_units=["ax_unit"],
            axis_ranges=[self._x],
        )
        self._params = (
            self._amplitude1,
            self._sigma1,
            self._x1,
            self._amplitude2,
            self._sigma2,
            self._x2,
            self._amplitude3,
            self._sigma3,
            self._x3,
        )

    def tearDown(self):
        pass

    def test_profile__no_bg(self):
        _x = np.linspace(0, 5, 100)
        _c = (0, 1, 1, 0, 3, 3, 0, 1, 1)
        _profile = TripleGaussian.profile(_c, _x)
        self.assertTrue(np.allclose(_profile, 0))

    def test_profile__0order_bg(self):
        _x = np.linspace(0, 5, 100)
        _c = (0, 1, 1, 0, 3, 3, 0, 1, 1, 2)
        _profile = TripleGaussian.profile(_c, _x)
        self.assertTrue(np.allclose(_profile, 2))

    def test_profile__1order_bg(self):
        _x = np.linspace(0, 5, 100)
        _c = (0, 1, 1, 0, 3, 3, 0, 5, 5, 2, 1)
        _profile = TripleGaussian.profile(_c, _x)
        self.assertTrue(np.allclose(_profile, 2 + _x))

    def test_guess_peak_start_params__simple(self):
        _params = TripleGaussian.guess_fit_start_params(self._x, self._data)
        self.assertTrue(abs(_params[2] - self._x1) < 0.01)
        self.assertTrue(abs(_params[5] - self._x2) < 0.01)
        self.assertTrue(abs(_params[8] - self._x3) < 0.01)

    def test_guess_peak_start_params__bounds_for_peak1(self):
        _bounds = (
            TripleGaussian.param_bounds_low[:],
            TripleGaussian.param_bounds_high[:],
        )
        _bounds[0][2] = self._x[500]
        _bounds[1][2] = self._x[530]
        _params = TripleGaussian.guess_fit_start_params(
            self._x, self._data, bounds=_bounds
        )
        self.assertTrue(_params[2] <= _bounds[1][2])
        self.assertTrue(abs(_params[5] - self._x2) < 0.01)

    def test_guess_peak_start_params__bounds_for_peak2(self):
        _bounds = (
            TripleGaussian.param_bounds_low[:],
            TripleGaussian.param_bounds_high[:],
        )
        _bounds[0][5] = self._x[1460]
        _bounds[1][5] = self._x[1480]
        _params = TripleGaussian.guess_fit_start_params(
            self._x, self._data, bounds=_bounds
        )
        self.assertTrue(_params[5] <= _bounds[1][5])
        self.assertTrue(abs(_params[2] - self._x1) < 0.01)

    def test_guess_peak_start_params__peak2_bounds_and_centerstart(self):
        _bounds = (
            TripleGaussian.param_bounds_low[:],
            TripleGaussian.param_bounds_high[:],
        )
        _bounds[0][5] = self._x[1460]
        _bounds[1][5] = self._x[1480]
        _params = TripleGaussian.guess_fit_start_params(
            self._x, self._data, bounds=_bounds, center2_start=self._x[1480]
        )
        self.assertTrue(_params[5] <= _bounds[1][5])
        self.assertTrue(abs(_params[2] - self._x1) < 0.01)

    def test_guess_peak_start_params__peak2_bounds_and_centerstart_out(self):
        _bounds = (
            TripleGaussian.param_bounds_low[:],
            TripleGaussian.param_bounds_high[:],
        )
        _bounds[0][5] = self._x[1460]
        _bounds[1][5] = self._x[1480]
        _params = TripleGaussian.guess_fit_start_params(
            self._x, self._data, bounds=_bounds, center2_start=self._x[1490]
        )
        self.assertTrue(_params[5] <= _bounds[1][5])
        self.assertTrue(abs(_params[2] - self._x1) < 0.01)

    def test_fwhm(self):
        _fwhm = TripleGaussian.fwhm(self._params)
        self.assertTrue(abs(_fwhm[0] - self._sigma1 * 2.355) < 0.01)
        self.assertTrue(abs(_fwhm[1] - self._sigma2 * 2.355) < 0.01)
        self.assertTrue(abs(_fwhm[2] - self._sigma3 * 2.355) < 0.01)

    def test_amplitude(self):
        _amplitude = TripleGaussian.amplitude(self._params)
        self.assertTrue(
            abs(_amplitude[0] - 0.39894228 * self._amplitude1 / self._sigma1) < 0.01
        )
        self.assertTrue(
            abs(_amplitude[1] - 0.39894228 * self._amplitude2 / self._sigma2) < 0.01
        )
        self.assertTrue(
            abs(_amplitude[2] - 0.39894228 * self._amplitude3 / self._sigma3) < 0.01
        )


if __name__ == "__main__":
    unittest.main()
