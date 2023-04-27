# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "rot_matrix_rx",
    "rot_matrix_ry",
    "rot_matrix_rz",
    "pyfai_rot_matrix",
    "get_chi_from_x_and_y",
    "fit_ellipse_from_points",
    "fit_detector_center_and_tilt_from_points",
    "fit_circle_from_points",
    "calc_points_on_ellipse",
    "line_intersection_with_detector",
]

import warnings

import numpy as np
from numpy import cos, sin
from scipy.optimize import leastsq

from ..exceptions import UserConfigError


def rot_matrix_rx(theta):
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


def rot_matrix_ry(theta):
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


def rot_matrix_rz(theta):
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


def pyfai_rot_matrix(theta1, theta2, theta3):
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


def get_chi_from_x_and_y(x, y):
    """
    Get the chi position in degree.

    Parameters
    ----------
    x : float
        The input value for the x coordinate.
    y : float
        The input value for the y coordinate.

    Returns
    -------
    float
        The chi value based on the input variables.
    """
    if x == 0 and y >= 0:
        _chi = np.pi / 2
    elif x == 0 and y < 0:
        _chi = 3 * np.pi / 2
    else:
        _chi = np.arctan(y / x)
    if x < 0:
        _chi += np.pi
    return np.mod(_chi, 2 * np.pi)


def fit_detector_center_and_tilt_from_points(xpoints, ypoints):
    """
    Fit the detector center, tilt and tilt plane from points.

    This function allows to extract the detector geometry in Fit2d style from a number
    of points.

    The conversion to center, axes and rotation of the major axes with respect to the
    cartesian axes are performed based on the formulas from
    https://mathworld.wolfram.com/Ellipse.html
    The coefficients for b, d, e from Halir & Flusser differ by a factor of 2 from the
    coefficients used in mathworld (and mathworld does not use 'e' as parameter).

    Parameters
    ----------
    xpoints : np.ndarray
        The x positions of the points to fit.
    ypoints : np.ndarray
        The y positions of the points to fit.

    Returns
    -------
    center_x : float
        The x center position.
    center_y : float
        The y center position.
    tilt : float
        The tilt angle in radians.
    tilt_plane : float
        The tilt plane orientation in radians.
    coeffs : tuple
        The ellipse coefficients
    """
    if xpoints.size < 5:
        raise UserConfigError(
            "A fit of an ellipse requires at least 5 input points to define a unique "
            "solution."
        )
    _coeffs = fit_ellipse_from_points(xpoints, ypoints)
    _cx, _cy, _tilt, _tilt_plane, _ax = get_ellipse_params_from_coeffs(_coeffs)
    return _cx, _cy, _tilt, _tilt_plane, _coeffs


def fit_ellipse_from_points(xpoints, ypoints):
    """
    Fit an ellipse from the given points.

    This is a Python implementation based on the Matlab algorithm from Halir and Flusser
    adapted from "Numerically stable direct least squares fitting of ellipses" (1998).
    The nomenclature and function parametrization is taken from the paper as well.
    Note that the return parameters are adjusted to be consistent with Wolfram's
    mathworld formula: https://mathworld.wolfram.com/Ellipse.html
    Return parameters are also normed to a = 1 for consistency.

    Parameters
    ----------
    xpoints : np.ndarray
        The x positions of the points to fit.
    ypoints : np.ndarray
        The y positions of the points to fit.

    Returns
    -------
    coeffs : np.ndarray
        The coefficients for the formula
        F(x; y) = ax**2 + 2bxy + cy**2 + 2dx + 2fy + g = 0
    """
    D1 = np.column_stack((xpoints**2, xpoints * ypoints, ypoints**2))
    D2 = np.column_stack((xpoints, ypoints, np.ones(xpoints.size)))
    S1 = np.matmul(D1.T, D1)
    S2 = np.matmul(D1.T, D2)
    S3 = np.matmul(D2.T, D2)
    T = np.matmul(-np.linalg.inv(S3), S2.T)
    M = S1 + np.matmul(S2, T)
    inv_C1 = np.array(((0, 0, 0.5), (0, -1, 0), (0.5, 0, 0)))
    M = np.matmul(inv_C1, M)
    _eigenvals, _eigenvecs = np.linalg.eig(M)
    _cond = 4 * _eigenvecs[0] * _eigenvecs[2] - _eigenvecs[1] ** 2
    _a1 = _eigenvecs[:, _cond > 0]
    coeffs = np.concatenate((_a1, np.matmul(T, _a1))).squeeze()
    coeffs[1] = coeffs[1] / 2
    coeffs[3] = coeffs[3] / 2
    coeffs[4] = coeffs[4] / 2
    return coeffs / coeffs[0]


def get_ellipse_params_from_coeffs(coeffs):
    """
    Get the ellipse parameters for center and tilt from the fit parameters.

    Parameters are defined as in Wolfram's mathworld formula:
    https://mathworld.wolfram.com/Ellipse.html

    Parameters
    ----------
    coeffs : tuple
        The tuple with the parameters (a, b, c, d, f, g)

    Returns
    -------
    center_x : float
        The x center position.
    center_y : float
        The y center position.
    tilt : float
        The tilt angle in radians.
    tilt_plane : float
        The tilt plane orientation in radians.
    axes : tuple
        The tuple with the two axes lengths.
    """
    a, b, c, d, f, g = coeffs
    _center_x = (c * d - b * f) / (b**2 - a * c)
    _center_y = (a * f - b * d) / (b**2 - a * c)
    _axes = (
        2
        * (a * f**2 + c * d**2 + g * b**2 - 2 * b * d * f - a * c * g)
        / (b**2 - a * c)
        / (np.array((1, -1)) * ((a - c) ** 2 + 4 * b**2) ** 0.5 - (a + c))
    ) ** 0.5
    if b == 0:
        _tilt_plane = np.pi / 2 if a > c else 0
    else:
        _tilt_plane = 0.5 * np.arctan(2 * b / (a - c)) + (np.pi / 2 if a > c else 0)
    _tilt = np.arccos(np.amin(_axes) / np.amax(_axes))
    return _center_x, _center_y, _tilt, _tilt_plane, _axes


def fit_circle_from_points(xpoints, ypoints):
    """
    Fit a circle from a given list of points.

    xpoints : np.ndarray
        The x positions of the points to fit.
    ypoints : np.ndarray
        The y positions of the points to fit.

    Returns
    -------
    center_x : float
        The x center position.
    center_y : float
        The y center position.
    radius: float
        The circle's radius.
    """

    def circle_distance(c, x, y):
        return (x - c[0]) ** 2 + (y - c[1]) ** 2 - c[2] ** 2

    _c0 = [np.mean(xpoints), np.mean(ypoints), (np.amax(xpoints) - np.amin(xpoints))]
    _c1, _ = leastsq(circle_distance, _c0, args=(xpoints, ypoints))
    return _c1


def calc_points_on_ellipse(coeffs, n_points=144, tmin=0, tmax=2 * np.pi):
    """
    Return npts points on the ellipse described by the params = x0, y0, ap,
    bp, e, phi for values of the parametric variable t between tmin and tmax.

    """
    (a, b, c, d, f, g) = coeffs
    _cx, _cy, _tilt, _tilt_angle, _axes = get_ellipse_params_from_coeffs(coeffs)
    _theta = np.linspace(tmin, tmax, num=n_points)
    _x = (
        _cx
        + _axes[0] * np.cos(_theta) * np.cos(_tilt_angle)
        - _axes[1] * np.sin(_theta) * np.sin(_tilt_angle)
    )
    _y = (
        _cy
        + _axes[0] * np.cos(_theta) * np.sin(_tilt_angle)
        + _axes[1] * np.sin(_theta) * np.cos(_tilt_angle)
    )
    return _x, _y


def line_intersection_with_detector(center, point, shape):
    """
    Calculate the point where a line hits the detector's edge.

    Parameters
    ----------
    center : tuple
        The center (cx, cy) coordinates.
    point : tuple
        The selected point's (x, y) coordinates.
    shape : tuple
        The detector shape (in pixels).

    Returns
    -------
    tuple
        The point on the detector frame intersecting the defined line.
    """
    _cx, _cy = center
    _px, _py = point
    _ny, _nx = shape
    _det_cp = _cx * _py - _cy * _px

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            _intersect_bottom_x = -_det_cp * _nx / ((_cy - _py) * (_nx))
        except ZeroDivisionError:
            _intersect_bottom_x = 1e9
        _intersect_bottom_y = 0

        _intersect_left_x = 0
        try:
            _intersect_left_y = _det_cp * _ny / ((_cx - _px) * _ny)
        except ZeroDivisionError:
            _intersect_left_y = 1e9
        _is_left = (np.round(_intersect_left_x, 2), np.round(_intersect_left_y, 2))

        try:
            _intersect_top_x = ((_cx - _px) * (_ny * _nx) - _det_cp * _nx) / (
                (_cy - _py) * _nx
            )
        except ZeroDivisionError:
            _intersect_top_x = 1e9
        _intersect_top_y = _ny

        _intersect_right_x = _nx
        try:
            _intersect_right_y = (_det_cp * _ny + (_cy - _py) * _nx * _ny) / (
                (_cx - _px) * (_ny) + (_cy - _py) * (_nx - _nx)
            )
        except ZeroDivisionError:
            _intersect_right_y = 1e9
        _is_right = (np.round(_intersect_right_x, 2), np.round(_intersect_right_y, 2))

    if _py >= _cy:
        if 0 <= _intersect_top_x <= _nx and 0 <= _intersect_top_y <= _ny:
            return np.round(_intersect_top_x, 2), np.round(_intersect_top_y, 2)
        if _px >= _cx:
            return _is_right
        return _is_left
    else:
        if 0 <= _intersect_bottom_x <= _nx and 0 <= _intersect_bottom_y <= _ny:
            return np.round(_intersect_bottom_x, 2), np.round(_intersect_bottom_y, 2)
        if _px >= _cx:
            return _is_right
        return _is_left
