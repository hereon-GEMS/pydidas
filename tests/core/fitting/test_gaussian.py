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

from pydidas.core import Dataset
from pydidas.core.fitting.gaussian import Gaussian


class TestGaussian(unittest.TestCase):
    def setUp(self):
        self._peakpos = 42
        self._data = Dataset(
            np.ones((150)), data_unit="data unit", axis_units=["ax_unit"]
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

    def test_guess_peak_start_params__narrow_peak(self):
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Gaussian.guess_fit_start_params(self._x, _data)
        self.assertTrue(_params[1] > 0)

    def test_guess_peak_start_params__normal_peak(self):
        _data = Dataset(np.ones((150)), data_unit="data unit", axis_units=["ax_unit"])
        _data[39:42] = 2
        _data[40] = 5
        _params = Gaussian.guess_fit_start_params(self._x, self._data)
        self.assertTrue(_params[1] > 0)


if __name__ == "__main__":
    unittest.main()
