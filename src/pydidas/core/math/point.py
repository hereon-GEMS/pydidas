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
__all__ = ["Point", "PointFromPolar"]


from dataclasses import dataclass
from numbers import Real
from typing import Any

import numpy as np


@dataclass
class Point:
    x: float
    y: float

    """
    A Point class representing a point in 2D space.
    
    The point can be initialized with either two float values for x and y coordinates,
    or a tuple of two floats. The class supports basic arithmetic operations such as
    addition, subtraction, multiplication by a scalar, and division by a scalar.
    """

    @staticmethod
    def _valid_input(item: Any) -> bool:
        """
        Check if the input is a valid Point or a tuple of two floats.

        Parameters
        ----------
        item : Any
            The item to check.

        Returns
        -------
        bool
            True if the item is a valid Point or a tuple of two floats, False otherwise.
        """
        return isinstance(item, Point) or (
            isinstance(item, (tuple, list))
            and len(item) == 2
            and all(isinstance(coord, Real) for coord in item)
        )

    def __init__(self, x: float | tuple[float, float], y: float = None) -> None:
        """
        Construct a Point object.

        The point can be initialized with either two float values for x and y coordinates,
        or a tuple of two floats. The class supports basic arithmetic operations such as
        addition, subtraction, multiplication by a scalar, and division by a scalar.
        """

        if isinstance(x, tuple) and self._valid_input(x):
            self.x, self.y = x
        elif isinstance(x, Real) and isinstance(y, Real):
            self.x, self.y = x, y
        else:
            raise TypeError(
                "Point must be initialized with two floats or a 2-tuple of floats."
            )
        self.x = float(self.x)
        self.y = float(self.y)

    def __call__(self) -> tuple[float, float]:
        """
        Return the point as a tuple (x, y).

        Returns
        -------
        tuple[float, float]
            The x and y coordinates of the point.
        """
        return self.x, self.y

    def __len__(self) -> int:
        """Return the number of dimensions of the Point."""
        return 2

    def __iter__(self):
        """Iterate over the coordinates of the Point."""
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> float:
        """
        Get the coordinate at the specified index.

        Parameters
        ----------
        index : int
            The index of the coordinate to retrieve (0 for x, 1 for y).

        Returns
        -------
        float
            The coordinate at the specified index.

        Raises
        ------
        IndexError
            If the index is not 0 or 1.
        """
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index must be 0 or 1.")

    def __contains__(self, item: Any) -> bool:
        """
        Check if the Point contains a given item.

        Parameters
        ----------
        item : Any
            The item to check for containment.

        Returns
        -------
        bool
            True if the item is either equal to x or y coordinates.
        """
        return isinstance(item, Real) and (
            np.isclose(item, self.x) or np.isclose(item, self.y)
        )

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
        if self.x == 0 and self.y > 0:
            return np.pi / 2
        elif self.x == 0 and self.y < 0:
            return 3 * np.pi / 2
        else:
            angle = np.arctan2(self.y, self.x)
            return np.mod(angle, 2 * np.pi)

    angle = theta
    chi = theta

    @property
    def theta_deg(self) -> float:
        """
        Get the angle of the point from the origin in degrees.

        Returns
        -------
        float
            The angle of the point in degrees.
        """
        return np.rad2deg(self.theta)

    angle_deg = theta_deg
    chi_deg = theta_deg

    def __repr__(self) -> str:
        """
        Return a string representation of the Point.

        Returns
        -------
        str
            A string representation of the Point.
        """
        return f"Point(x={self.x:.6f}, y={self.y:.6f})"

    def __getstate__(self) -> dict:
        """
        Get the state of the Point for serialization.

        Returns
        -------
        dict
            A dictionary containing the state of the Point.
        """
        return {"x": self.x, "y": self.y}

    def __setstate__(self, state: dict) -> None:
        """
        Set the state of the Point from a serialized state.

        Parameters
        ----------
        state : dict
            A dictionary containing the state of the Point.
        """
        self.x = state["x"]
        self.y = state["y"]

    def rounded(self, decimals: int = 6) -> "Point":
        """
        Return a new Point with coordinates rounded to the specified number of decimals.

        Parameters
        ----------
        decimals : int, optional
            The number of decimal places to round to (default is 6).

        Returns
        -------
        Point
            A new Point with rounded coordinates.
        """
        return Point(round(self.x, decimals), round(self.y, decimals))


def PointFromPolar(r: float, theta: float) -> Point:  # noqa C0103
    """
    Create a Point from polar coordinates.

    Parameters
    ----------
    r : float
        The radius.
    theta : float
        The angle in radians.

    Returns
    -------
    Point
        A Point object with the given polar coordinates.
    """
    return Point(r * np.cos(theta), r * np.sin(theta))
