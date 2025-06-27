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
__all__ = [
    "rot_matrix_rx",
    "rot_matrix_ry",
    "rot_matrix_rz",
    "pyfai_rot_matrix",
]


import numpy as np
from numpy import cos, sin


def rot_matrix_rx(theta: float) -> np.ndarray:
    """
    Create the rotation matrix for a rotation around the x-axis of a value of theta.

    Parameters
    ----------
    theta : float
        The rotation angle [in rad]

    Returns
    -------
    matrix : np.ndarray
        The rotation matrix.
    """
    return np.array(
        [[1, 0, 0], [0, cos(theta), -sin(theta)], [0, sin(theta), cos(theta)]]
    )


def rot_matrix_ry(theta: float) -> np.ndarray:
    """
    Create the rotation matrix for a rotation around the y-axis of a value of theta.

    Parameters
    ----------
    theta : float
        The rotation angle [in rad].

    Returns
    -------
    matrix : np.ndarray
        The rotation matrix.
    """
    return np.array(
        [[cos(theta), 0, sin(theta)], [0, 1, 0], [-sin(theta), 0, cos(theta)]]
    )


def rot_matrix_rz(theta: float) -> np.ndarray:
    """
    Create the rotation matrix for a rotation around the z-axis of a value of theta.

    Parameters
    ----------
    theta : float
        The rotation angle [in rad].

    Returns
    -------
    matrix : np.ndarray
        The rotation matrix.
    """
    return np.array(
        [[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, 0, 1]]
    )


def pyfai_rot_matrix(theta1: float, theta2: float, theta3: float) -> np.ndarray:
    """
    Get the combined rotation matrix for pyFAI theta values.

    Note: Rotations must be supplied in pyFAI notation (with theta1 and theta2 defined
    left-handedly).

    Parameters
    ----------
    theta1 : float
        The first rotation angle [in rad].
    theta2 : float
        The second rotation angle [in rad]
    theta3 : float
        The third rotation angle [in rad]


    Returns
    -------
    matrix : np.ndarray
        The combined rotation matrix.
    """
    return np.dot(
        np.dot(rot_matrix_rz(theta3), rot_matrix_ry(-theta2)), rot_matrix_rx(-theta1)
    )
