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
The point_list module defines a PointList class for managing a list of Point objects.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PointList"]

from numbers import Real
from typing import Any

import numpy as np

from pydidas.core.math.point import Point


class PointList(list):
    """
    A list-like class for managing Point objects, allowing for convenient initialization
    and access to x and y coordinate arrays.
    """

    @staticmethod
    def _convenience_tuple_convert(item: Any) -> Any | Point:
        """
        Convert a tuple to a Point if it has two numeric elements.

        Parameters
        ----------
        item : Any
            The item to convert.

        Returns
        -------
        Any | Point
            The original item if it is not a tuple or does not have two numeric elements,
            otherwise a Point object.
        """
        if (
            isinstance(item, tuple)
            and len(item) == 2
            and all(isinstance(coord, Real) for coord in item)
        ):
            return Point(*item)
        return item

    def append(self, item: Point) -> None:
        item = self._convenience_tuple_convert(item)
        if not isinstance(item, Point):
            raise TypeError("Only Point objects can be added to PointList.")
        super().append(item)

    def extend(self, items: list[Point]) -> None:
        items = [self._convenience_tuple_convert(item) for item in items]
        if not all(isinstance(item, Point) for item in items):
            raise TypeError("All items in the list must be Point objects.")
        super().extend(items)

    def insert(self, index: int, item: Point) -> None:
        item = self._convenience_tuple_convert(item)
        if not isinstance(item, Point):
            raise TypeError("Only Point objects can be inserted into PointList.")
        super().insert(index, item)

    @property
    def xarr(self) -> np.ndarray:
        """
        Get the x-coordinates of the points in the list as a numpy array.

        Returns
        -------
        np.ndarray
            An array of x-coordinates.
        """
        return np.array([point.x for point in self])

    @property
    def yarr(self) -> np.ndarray:
        """
        Get the y-coordinates of the points in the list as a numpy array.

        Returns
        -------
        np.ndarray
            An array of y-coordinates.
        """
        return np.array([point.y for point in self])

    def __repr__(self) -> str:
        """
        Return a string representation of the PointList.

        Returns
        -------
        str
            A string representation of the PointList.
        """
        return f"PointList({', '.join(repr(point) for point in self)})"
