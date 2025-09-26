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

import warnings
from dataclasses import dataclass
from numbers import Real
from typing import Any, Union

import numpy as np


@dataclass
class Point:
    x: Real
    y: Real

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

    def __init__(self, x: Real, y: Real = None) -> None:
        """
        Construct a Point object.

        The point can be initialized with either two float values for x and y
        coordinates, or a tuple of two floats. The class supports basic arithmetic
        operations such as addition, subtraction, multiplication by a scalar,
        and division by a scalar.
        """

        if isinstance(x, tuple) and self._valid_input(x):
            x, y = x
            warnings.warn(
                "Initializing Point with a tuple is deprecated, please use "
                "two Real values instead.",
                DeprecationWarning,
            )
        elif not (isinstance(x, Real) and isinstance(y, Real)):
            raise TypeError(
                "Point must be initialized with two floats or a 2-tuple of floats."
            )
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float:
        """
        Get the x coordinate of the Point.

        Returns
        -------
        float
            The x coordinate of the point.
        """
        return self._x

    @x.setter
    def x(self, value: Real) -> None:
        """
        Set the x coordinate of the Point.

        Parameters
        ----------
        value : Real
            The new x coordinate.
        """
        if not isinstance(value, Real):
            raise TypeError("x coordinate must be a real number.")
        self._x = float(value)

    @property
    def y(self) -> float:
        """
        Get the y coordinate of the Point.

        Returns
        -------
        float
            The y coordinate of the point.
        """
        return self._y

    @y.setter
    def y(self, value: Real) -> None:
        """
        Set the y coordinate of the Point.

        Parameters
        ----------
        value : Real
            The new y coordinate.
        """
        if not isinstance(value, Real):
            raise TypeError("y coordinate must be a real number.")
        self._y = float(value)

    def __call__(self) -> tuple[float, float]:
        """
        Return the point as a tuple (x, y).

        Returns
        -------
        tuple[float, float]
            The x and y coordinates of the point.
        """
        return self._x, self._y

    def __len__(self) -> int:
        """Return the number of dimensions of the Point."""
        return 2

    def __iter__(self):
        """Iterate over the coordinates of the Point."""
        yield self._x
        yield self._y

    def __getitem__(self, obj: int | slice) -> float | tuple[float, float]:
        """
        Get the item of the Point at the specified index or slice.

        Parameters
        ----------
        obj: : Integral | slice
            The index of the coordinate to retrieve (0 for x, 1 for y) or any
            valid python slice object.

        Returns
        -------
        float | tuple[float, float]
            The coordinate at the specified index.

        Raises
        ------
        IndexError
            If the index is not 0, 1 or a slice.
        """
        if obj == 0:
            return self._x
        elif obj == 1:
            return self._y
        elif isinstance(obj, slice):
            return tuple(self)[obj]
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
            np.isclose(item, self._x) or np.isclose(item, self._y)
        )

    def __add__(self, other: Union["Point", tuple[Real, Real]]) -> "Point":
        """
        Add another Point or a tuple to this Point.

        Parameters
        ----------
        other : Point | tuple[Real, Real]
            The point or tuple to add.

        Returns
        -------
        Point
            A new Point with the summed coordinates.
        """
        if not self._valid_input(other):
            raise TypeError("Can only add another Point or a tuple of two floats.")
        return Point(self.x + other[0], self.y + other[1])

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
        if not self._valid_input(other):
            raise TypeError("Can only subtract another Point or a tuple of two floats.")
        return Point(self.x - other[0], self.y - other[1])

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
            return Point(self._x * other, self._y * other)  # noqa
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
        if not isinstance(other, Real):
            raise TypeError("Can only divide a Point by a scalar number.")
        if other == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return Point(self.x / other, self.y / other)  # noqa

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
        if not self._valid_input(other):
            return False
        return self._x == other[0] and self._y == other[1]

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
        if self.x == 0.0 and self.y > 0.0:
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
        self._x = state["x"]
        self._y = state["y"]

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
