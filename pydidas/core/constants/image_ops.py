# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The image_ops module holds function definitions for applying rotations / mirroring
to images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "IMAGE_OPS",
    "rot_180",
    "rot_90_cw",
    "rot_90_ccw",
]

import numpy as np


def rot_180(image):
    """
    Rotate an image by 180 degree.

    Parameters
    ----------
    image : np.ndarray.
        The input image.

    Returns
    -------
    np.ndarray
        The rotated image.
    """
    return np.rot90(image, k=2)


def rot_90_cw(image):
    """
    Rotate an image by 90 degree clockwise, i.e. mathematically negative.

    Parameters
    ----------
    image : np.ndarray.
        The input image.

    Returns
    -------
    np.ndarray
        The rotated image.
    """
    return np.rot90(image, k=-1)


def rot_90_ccw(image):
    """
    Rotate an image by 90 degree counter-clockwise, i.e. mathematically positive.

    Parameters
    ----------
    image : np.ndarray.
        The input image.

    Returns
    -------
    np.ndarray
        The rotated image.
    """
    return np.rot90(image, k=1)


IMAGE_OPS = {
    "Flip left/right": np.fliplr,
    "Flip up/down": np.flipud,
    "Rot 180deg": rot_180,
    "Rot 90deg clockwise": rot_90_cw,
    "Rot 90deg counter-clockwise": rot_90_ccw,
}
