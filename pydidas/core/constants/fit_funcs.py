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
The fit_funcs module holds definitions for peak-fitting functions and functions
to calculate the delta between the function and given data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "gaussian",
    "gaussian_delta",
    "lorentzian",
    "lorentzian_delta",
    "voigt",
    "voigt_delta"
]

import numpy as np
from scipy.special import voigt_profile

PI = np.pi


def gaussian(c, x):
    """
    Function to fit a Gaussian to data points.

    The Gaussian function has the general form

    f(x) = A * (2 * pi)**(-0.5) / sigma * exp(-(x - mu)**2 / ( 2 * sigma**2))

    where A is the amplitude, mu is the expectation value, and sigma is the
    variance. A polinomial background of 0th or 1st order can be added by
    using additional coefficients.

    Parameters
    ----------
    c : tuple
        The tuple with the function parameters.
        c[0] : Amplitude
        c[1] : sigma
        c[2] : expectation value
        c[3], optional: A background offset.
        c[4], optional: THe polynomial coefficient for a first order background.
    x : np.ndarray
        The x data points.

    Returns
    -------
    np.ndarray
        The function values for the given x values.
    """
    _gauss = c[0] * (2 * PI)**(-0.5) / c[1] * np.exp(-(x - c[2])**2 / ( 2 * c[1]**2))
    if len(c) == 3:
        return _gauss
    if len(c) == 4:
        return _gauss + c[3]
    if len(c) == 5:
        return _gauss + c[3] + c[4] * x
    raise ValueError("The order of the background is not supported.")


def gaussian_delta(c, x, data):
    """
    Function to fit a Gaussian to data points.

    Parameters
    ----------
    c : tuple
        The tuple with the fit parameters.
        c[0] : Amplitude
        c[1] : Sigma
        c[2] : Center
        c[3] : Background order 0 (if used)
        c[4] : Background order 1 (if used)
    x : np.ndarray
        The x data points
    data : np.ndarray
        The data points as reference

    Returns
    -------
    np.ndarray
        The residual between the fit and the data.
    """
    return gaussian(c, x) - data


def lorentzian(c, x):
    """
    Function to generate a Lorentzian profile for a series of x-values.

    The Lorentzian has the general form

    L(x) = A / pi * (GAMMA / 2) / ((x - x0)**2 + (GAMMA / 2)**2 ),

    where A is the amplitude, GAMMA is the FWHM, x0 is the center.

    Parameters
    ----------
    c : tuple
        The tuple with the fit parameters.
        c[0] : Amplitude
        c[1] : Gamma
        c[2] : Center
        c[3], optional: A background offset.
        c[4], optional: THe polynomial coefficient for a first order background.
    x : np.ndarray
        The x data points

    Returns
    -------
    np.ndarray
        The function values for the given x values.
    """
    _lorentz = c[0] / PI * (0.5 * c[1]) / ((x - c[2])**2 + (0.5 * c[1])**2)
    if len(c) == 3:
        return _lorentz
    if len(c) == 4:
        return _lorentz + c[3]
    if len(c) == 5:
        return _lorentz + c[3] + c[4] * x
    raise ValueError("The order of the background is not supported.")


def lorentzian_delta(c, x, data):
    """
    Function to fit a Lorentzian to data points.

    Parameters
    ----------
    c : tuple
        The tuple with the fit parameters.
        c[0] : Amplitude
        c[1] : Gamma
        c[2] : Center
        c[3] : Background order 0 (if used)
        c[4] : Background order 1 (if used)
    x : np.ndarray
        The x data points
    data : np.ndarray
        The data points as reference

    Returns
    -------
    np.ndarray
        The residual between the fit and the data.
    """
    return lorentzian(c, x) - data


def voigt(c, x):
    """
    Function to calculate a Voigt profile (a convolution of a Gaussian and a
    Lorentzian profile).

    Parameters
    ----------
    c : tuple
        The tuple with the fit parameters.
        c[0] : Amplitude
        c[1] : Sigma
        c[2] : Gamma
        c[3] : Center
        c[4] : Background order 0 (if used)
        c[5] : Background order 1 (if used)
    x : np.ndarray
        The x data points

    Returns
    -------
    np.ndarray
        The residual between the fit and the data.
    """
    _voigt = c[0] * voigt_profile(x - c[3], c[1], c[2])
    if len(c) == 4:
        return _voigt
    if len(c) == 5:
        return _voigt + c[4]
    if len(c) == 6:
        return _voigt + c[4] + c[5] * x
    raise ValueError("The order of the background is not supported.")


def voigt_delta(c, x, data):
    """
    Function to fit a Pseudo-Voigt to data points.

    Parameters
    ----------
    c : tuple
        The tuple with the fit parameters.
        c[0] : Fraction (controlling the distribution between Gaussian and
                         Lorentzian functions)
        c[1] : Amplitude
        c[2] : Sigma
        c[3] : Center
        c[4] : Background order 0 (if used)
        c[5] : Background order 1 (if used)
    x : np.ndarray
        The x data points
    data : np.ndarray
        The data points as reference

    Returns
    -------
    np.ndarray
        The residual between the fit and the data.
    """
    return voigt(c, x) - data
