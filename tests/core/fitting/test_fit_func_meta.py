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


import copy
import unittest

from pydidas.core.fitting import FitFuncBase, FitFuncMeta


def create_test_class():
    class TestClass(FitFuncBase):
        name = "Test"
        param_bounds_low = []
        param_bounds_high = []
        param_labels = []


class TestFitFuncMeta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._registry = copy.deepcopy(FitFuncMeta.registry)

    @classmethod
    def tearDownClass(cls):
        FitFuncMeta.registry = cls._registry

    def tearDown(self):
        FitFuncMeta.clear_registry()

    def test_class_is_registered(self):
        create_test_class()
        self.assertIn("Test", FitFuncMeta.registry)

    def test_clear_registry(self):
        create_test_class()
        FitFuncMeta.clear_registry()
        self.assertEqual(FitFuncMeta.registry, {})

    def test_register_class__repeat(self):
        create_test_class()
        with self.assertRaises(KeyError):
            create_test_class()

    def test_get_fitter_names_with_num_peaks__n1(self):
        create_test_class()
        _n1 = FitFuncMeta.get_fitter_names_with_num_peaks(1)
        _n2 = FitFuncMeta.get_fitter_names_with_num_peaks(2)
        self.assertEqual(_n1, ("Test",))
        self.assertEqual(_n2, ())

    def test_get_fitter_names_with_num_peaks__n3(self):
        create_test_class()
        FitFuncMeta.registry["Test"].num_peaks = 3
        _n1 = FitFuncMeta.get_fitter_names_with_num_peaks(1)
        _n2 = FitFuncMeta.get_fitter_names_with_num_peaks(2)
        _n3 = FitFuncMeta.get_fitter_names_with_num_peaks(3)
        self.assertEqual(_n1, ())
        self.assertEqual(_n2, ())
        self.assertEqual(_n3, ("Test",))


if __name__ == "__main__":
    unittest.main()
