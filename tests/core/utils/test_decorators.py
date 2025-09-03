# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

from pydidas.core.utils.decorators import copy_docstring


class _TestClass:
    """Class docstring."""

    def __init__(self):
        self.attr1 = "Test"

    def method1(self):
        """
        Test docstring 1.
        """

    def method2(self):
        """
        Test docstring 2.
        """


class Test_copy_docstring(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def test_copy_from_class(self):
        class NewTest:
            def __init__(self): ...

            @copy_docstring(_TestClass)
            def method1(self): ...

        self.assertEqual(NewTest.method1.__doc__, _TestClass.method1.__doc__)

    def test_copy_from_method(self):
        class NewTest:
            def __init__(self): ...

            @copy_docstring(_TestClass.method2)
            def method3(self): ...

        self.assertEqual(NewTest.method3.__doc__, _TestClass.method2.__doc__)


if __name__ == "__main__":
    unittest.main()
