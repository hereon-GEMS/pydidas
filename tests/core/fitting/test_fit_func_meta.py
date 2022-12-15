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

from pydidas.core.fitting import (
    FitFuncMeta,
    FitFuncBase,
)


def create_test_class():
    class TestClass(FitFuncBase, metaclass=FitFuncMeta):
        func_name = "Test"
        param_bounds_low = []
        param_bounds_high = []
        param_labels = []


class TestFitFuncMeta(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
