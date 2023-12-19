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

from pydidas.core.utils import flatten, flatten_all


class TestFlattenIterable(unittest.TestCase):
    def test_flatten__nested_input(self):
        _input = [[1, 2, 3, 4], [5, 6], [7, 8]]
        _flat = flatten(_input)
        self.assertEqual(_flat, [1, 2, 3, 4, 5, 6, 7, 8])

    def test_flatten__nested_list_as_tuple(self):
        _input = [[1, 2, 3, 4], [5, 6], [7, 8]]
        _flat = flatten(_input, astype=tuple)
        self.assertEqual(_flat, (1, 2, 3, 4, 5, 6, 7, 8))

    def test_flatten__nested_list_depth2_iter1(self):
        _input = [[1, 2, [3, 4]], [5, 6], [7, 8]]
        _flat = flatten(_input)
        self.assertEqual(_flat, [1, 2, [3, 4], 5, 6, 7, 8])

    def test_flatten__nested_tuple(self):
        _input = [[1, 2, 3, 4], [5, 6], [7, 8]]
        _flat = flatten(_input, astype=tuple)
        self.assertEqual(_flat, (1, 2, 3, 4, 5, 6, 7, 8))

    def test_flatten_all__nested_list_depth2(self):
        _input = [[1, 2, [3, 4]], [5, 6], [7, 8]]
        _flat = flatten_all(_input)
        self.assertEqual(_flat, [1, 2, 3, 4, 5, 6, 7, 8])

    def test_flatten_all__nested_list_depth5(self):
        _input = [[1, 2, [3, 4]], 5, 6, [7, 8], [[9, 10, [11, 12, [13, 14]]]]]
        _flat = flatten_all(_input)
        self.assertEqual(_flat, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

    def test_flatten_all__nested_list_depth5_as_tuple(self):
        _input = [[1, 2, [3, 4]], 5, 6, [7, 8], [[9, 10, [11, 12, [13, 14]]]]]
        _flat = flatten_all(_input, astype=tuple)
        self.assertEqual(_flat, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))


if __name__ == "__main__":
    unittest.main()
