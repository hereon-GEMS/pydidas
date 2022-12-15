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

from pydidas.core.fitting.fit_func_base import FitFuncBase


FIT_CLASS = FitFuncBase


class TestFitFuncBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._x = np.arange(20)
        cls._y = np.random.random((cls._x.size))

    def test_class_params_okay(self):
        for _attribute in [
            "func_name",
            "param_bounds_low",
            "param_bounds_high",
            "param_labels",
        ]:
            self.assertTrue(hasattr(FIT_CLASS, _attribute))

    def test_function(self):
        _result = FIT_CLASS.function([], self._x)
        self.assertTrue(np.allclose(_result, self._x))

    def test_delta(self):
        _values = np.random.random((self._x.size))
        _result = FIT_CLASS.delta([], self._x, _values)
        self.assertTrue(np.allclose(_result, self._x - _values))


if __name__ == "__main__":
    unittest.main()
