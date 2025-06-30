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

import pickle

import numpy as np
import pytest

from pydidas.core.math.point import Point  # Adjust the import path as needed


def test_point_initialization():
    point = Point(3.5, 7.2)
    assert point.x == 3.5
    assert point.y == 7.2


def test_point_initialization__w_tuple():
    point = Point((3.5, 7.2))
    assert point.x == 3.5
    assert point.y == 7.2


@pytest.mark.parametrize("value", [(3.5, "7"), (1, 2, 3), ("2", 3, 2)])
def test_point_initialization__w_wrong_tuple(value):
    with pytest.raises(TypeError):
        Point(value)


def test_point_equality():
    point1 = Point(1.0, 2.0)
    point2 = Point(1.0, 2.0)
    point3 = Point(2.0, 3.0)
    assert point1 == point2
    assert point1 != point3


def test_point_repr():
    point = Point(4.0, 5.0)
    assert repr(point) == "Point(x=4.000000, y=5.000000)"


def test_point_call():
    point = Point(3.0, 4.0)
    assert point() == (3.0, 4.0)


def test_point_addition__w_point():
    point1 = Point(1.0, 2.0)
    point2 = Point(3.0, 4.0)
    result = point1 + point2
    assert result == Point(4.0, 6.0)


def test_point_addition__w_tuple():
    point1 = Point(1.0, 2.0)
    result = point1 + (2.0, 3.0)
    assert result == Point(3.0, 5.0)


def test_point_addition__right_w_tuple():
    point1 = Point(1.0, 2.0)
    result = (2.0, 3.0) + point1
    assert result == Point(3.0, 5.0)


def test_point_addition_in_place():
    point1 = Point(1.0, 2.0)
    point1 += Point(3.0, 4.0)
    assert point1 == Point(4.0, 6.0)


def test_point_addition__w_tuple_wrong_length():
    point1 = Point(1.0, 2.0)
    with pytest.raises(TypeError):
        point1 + (2.0, 3.0, 2.1)


def test_point_addition__w_tuple__non_numbers():
    point1 = Point(1.0, 2.0)
    with pytest.raises(TypeError):
        point1 + (2.0, "invalid")


def test_point_addition__w_scalar():
    point1 = Point(1.0, 2.0)
    with pytest.raises(TypeError):
        point1 + 3  # noqa


def test_point_addition__w_invalid_type():
    point1 = Point(1.0, 2.0)
    with pytest.raises(TypeError):
        point1 + "invalid"  # noqa


def test_point_subtraction__w_point():
    point1 = Point(5.0, 7.0)
    point2 = Point(3.0, 4.0)
    result = point1 - point2
    assert result == Point(2.0, 3.0)


def test_point_subtraction__w_tuple():
    point1 = Point(5.0, 7.0)
    result = point1 - (2.0, 3.0)
    assert result == Point(3.0, 4.0)


def test_point_subtraction__right_w_tuple():
    point1 = Point(5.0, 7.0)
    result = (7.0, 9.0) - point1
    assert result == Point(-2.0, -2.0)


def test_point_subtraction_in_place():
    point1 = Point(5.0, 7.0)
    point1 -= Point(3.0, 4.0)
    assert point1 == Point(2.0, 3.0)


def test_point_subtraction__w_tuple_wrong_length():
    point1 = Point(5.0, 7.0)
    with pytest.raises(TypeError):
        point1 - (2.0, 3.0, 2.1)


def test_point_subtraction__w_tuple__non_numbers():
    point1 = Point(5.0, 7.0)
    with pytest.raises(TypeError):
        point1 - (2.0, "invalid")


def test_point_subtraction__w_scalar():
    point1 = Point(5.0, 7.0)
    with pytest.raises(TypeError):
        point1 - 3  # noqa


def test_point_subtraction__w_invalid_type():
    point1 = Point(5.0, 7.0)
    with pytest.raises(TypeError):
        point1 - "invalid"  # noqa


def test_point_multiplication__w_scalar():
    point = Point(2.0, 3.0)
    result = point * 2
    assert result == Point(4.0, 6.0)


def test_point_multiplication__w_left_scalar():
    point = Point(2.0, 3.0)
    result = 2 * point
    assert result == Point(4.0, 6.0)


def test_point_multiplication__in_place():
    point = Point(2.0, 3.0)
    point *= 2
    assert point == Point(4.0, 6.0)


def test_point_multiplication__w_tuple():
    point = Point(2.0, 3.0)
    with pytest.raises(TypeError):
        point * (2, 3)  # noqa


def test_point_division():
    point = Point(6.0, 8.0)
    result = point / 2
    assert result == Point(3.0, 4.0)


def test_point_division__in_place():
    point = Point(6.0, 8.0)
    point /= 2
    assert point == Point(3.0, 4.0)


def test_point_division__zero():
    point = Point(6.0, 8.0)
    with pytest.raises(ZeroDivisionError):
        point / 0


def test_point_division__wrong_type():
    point = Point(6.0, 8.0)
    with pytest.raises(TypeError):
        point / "invalid"  # noqa


def test_point_radius():
    point = Point(3.0, 4.0)
    assert point.r == 5.0


@pytest.mark.parametrize(
    "x, y, expected_theta",
    [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, np.pi / 2),
        (-1.0, 0.0, np.pi),
        (0.0, -1.0, 3 * np.pi / 2),
        (-1, -1, 5 * np.pi / 4),
        (1.0, 1.0, np.pi / 4),
    ],
)
def test_point_theta(x, y, expected_theta):
    point = Point(x, y)
    assert point.theta == pytest.approx(expected_theta)
    assert point.angle == pytest.approx(expected_theta)
    assert point.chi == pytest.approx(expected_theta)


@pytest.mark.parametrize(
    "x, y, expected_theta",
    [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, np.rad2deg(np.pi / 2)),
        (-1.0, 0.0, np.rad2deg(np.pi)),
        (0.0, -1.0, np.rad2deg(3 * np.pi / 2)),
        (-1, -1, np.rad2deg(5 * np.pi / 4)),
        (1.0, 1.0, np.rad2deg(np.pi / 4)),
    ],
)
def test_point_theta_deg(x, y, expected_theta):
    point = Point(x, y)
    assert point.theta_deg == pytest.approx(expected_theta)
    assert point.angle_deg == pytest.approx(expected_theta)
    assert point.chi_deg == pytest.approx(expected_theta)


def test_pickle():
    point = Point(3.0, 4.0)
    pickled_point = pickle.dumps(point)
    unpickled_point = pickle.loads(pickled_point)
    assert isinstance(unpickled_point, Point)
    assert unpickled_point.x == point.x
    assert unpickled_point.y == point.y


@pytest.mark.parametrize("decimals", [0, 1, 2, 3, 5])
def test_rounded(decimals):
    point = Point(3.1415953345, 2.718223423428)
    rounded_point = point.rounded(decimals)
    assert rounded_point.x == pytest.approx(np.round(point.x, decimals))
    assert rounded_point.y == pytest.approx(np.round(point.y, decimals))


if __name__ == "__main__":
    pytest.main()
