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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the FitFuncBase class which all fitting functions should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitFuncBase"]


import numpy as np


class FitFuncBase:
    """
    Base class for fit functinos
    """

    func_name = "base fit function"
    param_bounds_low = []
    param_bounds_high = []
    param_labels = []
    num_peaks = 1

    @classmethod
    def guess_fit_start_params(cls, x, y):
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        """
        return []

    @classmethod
    def function(cls, c, x):
        """
        The fitting function.

        Parameters
        ----------
        c : tuple
            The function parameters.
        x : np.ndarray
            The x points to compute the function values.

        Returns
        -------
        np.ndarray
            The function values at the positions x.
        """
        return x

    @classmethod
    def delta(cls, c, x, data):
        """
        Get the difference between the fit and the data.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.
        x : np.ndarray
            The x points to calculate the function values.
        data : np.ndarray
            The data values.

        Returns
        -------
        np.ndarray
            The difference of function - data
        """
        return cls.function(c, x) - data

    @classmethod
    def area(cls, c):
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal to the amplitude term.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function area.
        """
        return c[0]

    @classmethod
    def calculate_background_params(cls, x, y, bg_order):
        """
        Calculate the parameters for the background and remove it from the values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        bg_order : Union[None, 0, 1]
            The order of the background.

        Returns
        -------
        y : np.ndarray
            The background-corrected values
        bg_params : list
            The parameters to describe the background.
        """
        if bg_order is None:
            return y, []
        if bg_order not in [0, 1]:
            raise ValueError("The selected background order is not supported")
        if bg_order == 0:
            _bg0 = np.amin(y)
            y = y - _bg0
            return y, [_bg0]
        _bg1 = (y[-1] - y[0]) / (x[-1] - x[0])
        _bg0 = y[0] - _bg1 * x[0]
        y = y - (_bg1 * x + _bg0)
        return y, [_bg0, _bg1]

    @classmethod
    def fwhm(cls, c):
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function FWHM.
        """
        raise NotImplementedError(
            "The FWHM method must be implemented by the specific FitFunc"
        )
