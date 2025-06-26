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
# MERCHANTABILITY or _NESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The point_list module defines a PointList class for managing a list of Point objects.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PointList"]


import numpy as np

from pydidas.core.math.point import Point


class PointList(list):
    def append(self, item: Point) -> None:
        if not isinstance(item, Point):
            raise TypeError("Only Point objects can be added to PointList.")
        super().append(item)

    def extend(self, items: list[Point]) -> None:
        if not all(isinstance(item, Point) for item in items):
            raise TypeError("All items in the list must be Point objects.")
        super().extend(items)

    def insert(self, index: int, item: Point) -> None:
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
