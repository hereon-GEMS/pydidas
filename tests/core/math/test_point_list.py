# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or _NESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Unittests for the Point class in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright  2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

import numpy as np
import pytest

from pydidas.core.math.point import Point
from pydidas.core.math.point_list import PointList


def test_initialization():
    point_list = PointList()
    assert len(point_list) == 0


def test_append():
    point_list = PointList()
    point = Point(1.0, 2.0)
    point_list.append(point)
    assert len(point_list) == 1
    assert point_list[0] == point


def test_append__multiple():
    point_list = PointList()
    for _i in range(6):
        point = Point(1.0, _i)
        point_list.append(point)
    assert len(point_list) == 6
    assert point_list[-1] == point


def test_add_invalid_type():
    point_list = PointList()
    with pytest.raises(TypeError):
        point_list.append("invalid")  # type: ignore


@pytest.mark.parametrize(
    "item",
    [[Point(4, 5), Point(6, 7)], PointList((Point(12, 2), Point(4, 3), Point(7, 1)))],
)
def test_extend(item):
    point_list = PointList([Point(1.0, 2.0), Point(3.0, 4.0)])
    point_list.extend(item)
    assert len(point_list) == 2 + len(item)


def test_insert():
    point_list = PointList([Point(1.0, 2.0), Point(3.0, 4.0)])
    point = Point(5.0, 6.0)
    point_list.insert(1, point)
    assert len(point_list) == 3
    assert point_list[1] == point


def test_remove():
    point_list = PointList()
    point = Point(1.0, 2.0)
    point_list.append(point)
    point_list.remove(point)
    assert len(point_list) == 0


def test_remove_nonexistent_point():
    point_list = PointList()
    point = Point(1.0, 2.0)
    with pytest.raises(ValueError):
        point_list.remove(point)


def test_clear():
    point_list = PointList()
    point_list.append(Point(1.0, 2.0))
    point_list.append(Point(3.0, 4.0))
    point_list.clear()
    assert len(point_list) == 0


def test_iteration():
    point_list = PointList()
    points = [Point(1.0, 2.0), Point(3.0, 4.0)]
    for point in points:
        point_list.append(point)
    for i, point in enumerate(point_list):
        assert point == points[i]


def test_contains():
    point_list = PointList()
    point = Point(1.0, 2.0)
    point_list.append(point)
    assert point in point_list
    assert Point(3.0, 4.0) not in point_list


def test_indexing():
    point_list = PointList()
    points = [Point(1.0, 2.0), Point(3.0, 4.0)]
    for point in points:
        point_list.append(point)
    assert point_list[0] == points[0]
    assert point_list[1] == points[1]


def test_slicing():
    point_list = PointList()
    points = [Point(1.0, 2.0), Point(3.0, 4.0), Point(5.0, 6.0)]
    for point in points:
        point_list.append(point)
    sliced = point_list[1:]
    assert len(sliced) == 2
    assert sliced[0] == points[1]
    assert sliced[1] == points[2]


def test_xarr_property():
    point_list = PointList([Point(1.0, 2.0), Point(3.0, 4.0), Point(1, 4), Point(2, 1)])
    xarr = point_list.xarr
    assert isinstance(xarr, np.ndarray)
    assert np.array_equal(xarr, np.array([1.0, 3.0, 1.0, 2.0]))


def test_yarr_property():
    point_list = PointList([Point(1.0, 2.0), Point(3.0, 4.0), Point(1, 4), Point(2, 1)])
    yarr = point_list.yarr
    assert isinstance(yarr, np.ndarray)
    assert np.array_equal(yarr, np.array([2.0, 4.0, 4.0, 1.0]))


if __name__ == "__main__":
    pytest.main()
