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
The point module defines a Point class for representing points in 2D space.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright  2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Point"]


from dataclasses import dataclass
from numbers import Real
from typing import Any

import numpy as np


@dataclass
class Point:
    x: float
    y: float

    def __call__(self) -> tuple[float, float]:
        """
        Return the point as a tuple (x, y).

        Returns
        -------
        tuple[float, float]
            The x and y coordinates of the point.
        """
        return self.x, self.y

    def __add__(self, other) -> "Point":
        """
        Add another Point or a tuple to this Point.

        Parameters
        ----------
        other : Point or tuple[float, float]
            The point or tuple to add.

        Returns
        -------
        Point
            A new Point with the summed coordinates.
        """
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif (
            isinstance(other, tuple)
            and len(other) == 2
            and isinstance(other[0], Real)
            and isinstance(other[1], Real)
        ):
            return Point(self.x + other[0], self.y + other[1])
        else:
            raise TypeError("Can only add another Point or a tuple of two floats.")

    __iadd__ = __add__
    __radd__ = __add__

    def __sub__(self, other) -> "Point":
        """
        Subtract another Point or a tuple from this Point.

        Parameters
        ----------
        other : Point or tuple[float, float]
            The point or tuple to subtract.

        Returns
        -------
        Point
            A new Point with the subtracted coordinates.
        """
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        elif (
            isinstance(other, tuple)
            and len(other) == 2
            and isinstance(other[0], Real)
            and isinstance(other[1], Real)
        ):
            return Point(self.x - other[0], self.y - other[1])
        else:
            raise TypeError("Can only subtract another Point or a tuple of two floats.")

    __isub__ = __sub__
    __rsub__ = __sub__

    def __mul__(self, other: Real) -> "Point":
        """
        Multiply the Point by a scalar.

        Parameters
        ----------
        other : Real
            The scalar to multiply with.

        Returns
        -------
        Point
            A new Point with the multiplied coordinates.
        """
        if isinstance(other, Real):
            return Point(self.x * other, self.y * other)
        else:
            raise TypeError("Can only multiply a Point by a scalar number.")

    __rmul__ = __mul__
    __imul__ = __mul__

    def __truediv__(self, other: Real) -> "Point":
        """
        Divide the Point by a scalar.

        Parameters
        ----------
        other : Real
            The scalar to divide by.

        Returns
        -------
        Point
            A new Point with the divided coordinates.
        """
        if isinstance(other, Real):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            return Point(self.x / other, self.y / other)
        else:
            raise TypeError("Can only divide a Point by a scalar number.")

    def __eq__(self, other: Any) -> bool:
        """
        Check if this Point is equal to another Point or a tuple.

        Parameters
        ----------
        other : Point or tuple[float, float]
            The point or tuple to compare with.

        Returns
        -------
        bool
            True if the points are equal, False otherwise.
        """
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        elif (
            isinstance(other, tuple)
            and len(other) == 2
            and isinstance(other[0], Real)
            and isinstance(other[1], Real)
        ):
            return self.x == other[0] and self.y == other[1]
        return False

    @property
    def r(self) -> float:
        """
        Get the radius of the point from the origin.

        Returns
        -------
        float
            The radius of the point.
        """
        return (self.x**2 + self.y**2) ** 0.5

    @property
    def theta(self) -> float:
        """
        Get the angle of the point from the origin in radians.

        Returns
        -------
        float
            The angle of the point in radians.
        """
        if self.x == 0 and self.y >= 0:
            return np.pi / 2
        elif self.x == 0 and self.y < 0:
            return 3 * np.pi / 2
        else:
            angle = np.arctan2(self.y, self.x)
            return np.mod(angle, 2 * np.pi)
