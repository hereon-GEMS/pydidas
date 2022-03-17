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
The constants module holds constant nmumber defitions needed in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GAUSSIAN', 'LORENTZIAN', 'PSEUDO_VOIGT']


import numpy as np


def GAUSSIAN(c, x, data, bg_order=None):
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
    if bg_order is None:
        return (c[0] * np.exp(-(x - c[2]) ** 2 / (2. * c[1]** 2))) - data
    if bg_order == 0:
        return (c[0] * np.exp(-(x - c[2]) ** 2 / (2. * c[1]** 2))
                + c[3] - data)
    if bg_order == 1:
        return (c[0] * np.exp(-(x - c[2]) ** 2 / (2. * c[1]** 2))
                + c[3] + c[4] * x - data)


def LORENTZIAN(c, x, data, bg_order=None):
    """
    Function to fit a Lorentzian to data points.

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
    if bg_order is None:
        return c[0] / (1 + ((x - c[2]) / c[1]) ** 2) - data
    if bg_order == 0:
        return c[0] / (1 + ((x - c[2]) / c[1]) ** 2) + c[3] - data
    if bg_order == 1:
        return c[0] / (1 + ((x - c[2]) / c[1]) ** 2) + c[3] + c[4] * x - data


def PSEUDO_VOIGT(c, x, data, bg_order=None):
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
     fit function with the following Parameters:
    """
    return ((1 - c[0]) * GAUSSIAN(c[1:], x, data, bg_order)
            + c[0] * LORENTZIAN(c[1:], x, data, bg_order))
