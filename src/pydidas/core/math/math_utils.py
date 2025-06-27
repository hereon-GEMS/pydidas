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
The math_utils module includes functions for mathematical operations used in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ray_intersects_with_detector"]


import numpy as np

from pydidas.core.math.point import Point
from pydidas.core.math.point_list import PointList


def ray_intersects_with_detector(
    center: Point, chi: float, shape: tuple[int, int]
) -> PointList:
    """
    Calculate the point where a ray from the detector center hits the detector's edge.

    Parameters
    ----------
    center : Point
        The center (cx, cy) coordinates.
    chi : float
        The angle from the center point in rad.
    shape : tuple[int, int]
        The detector shape (in pixels), given as (ny, nx).

    Returns
    -------
    intersections : PointList
        The positions of the intersection points between ray and detector boundaries.
    """
    _ny, _nx = shape
    _intersects = PointList()
    chi = np.round(np.mod(chi, 2 * np.pi), 6)  # normalize angle to [0, 2pi]
    sign_sin_chi = np.sign(np.sin(chi))  # calculate here to avoid multiple calls
    cos_chi = np.cos(chi)  # calculate here to avoid multiple calls
    sign_cos_chi = np.sign(cos_chi)  # calculate here to avoid multiple calls
    if abs(cos_chi) < 1e-6 and (0 <= center.x <= _nx):
        for _y in [0, _ny]:
            if sign_sin_chi == np.sign(_y - center.y):
                _intersects.append(Point(center.x, _y))
        return _intersects
    _ray_m = np.tan(chi)
    _ray_y0 = center.y - _ray_m * center.x
    # intersections with vertical edges:
    for _x in [0, _nx]:
        _y = np.round(_ray_m * (_x - center.x) + center.y, 5)
        # only add intersections if the ray is pointing towards the edge
        if (0 <= _y <= _ny) and (sign_cos_chi == np.sign(_x - center.x)):
            _intersects.append(Point(_x, _y))
    if _ray_m != 0:
        # intersections with horizontal edges:
        for _y in [0, _ny]:
            _x = np.round((_y - center.y) / _ray_m + center.x)
            # only add intersections if the ray is pointing towards the edge
            if (0 <= _x <= _nx) and (sign_sin_chi == np.sign(_y - center.y)):
                _intersects.append((float(_x), float(_y)))
    # ensure that the first intersection is the one closest to the center
    if (
        len(_intersects) == 2
        and (_intersects[0] - center).r > (_intersects[1] - center).r
    ):
        _intersects.reverse()
    return _intersects
