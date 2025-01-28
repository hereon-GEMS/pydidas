# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the Gaussian class for fitting a Gaussian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Gaussian"]

from numbers import Real
from typing import Dict, Optional

from numpy import amax, amin, exp, inf, ndarray, pi

from pydidas.core.fitting.fit_func_base import FitFuncBase


class Gaussian(FitFuncBase):
    """
    Class for fitting a Gaussian function.
    """

    name = "Gaussian"
    param_bounds_low = [0, 1e-20, -inf]
    param_bounds_high = [inf, inf, inf]
    param_labels = ["amplitude", "sigma", "center"]
    num_peak_params = 3
    center_param_index = 2
    amplitude_param_index = 0

    @staticmethod
    def func(c: tuple[Real], x: ndarray) -> ndarray:
        """
        Get function values for a Gaussian function.

        The Gaussian function has the general form

        f(x) = A * (2 * pi)**(-0.5) / sigma * exp(-(x - mu)**2 / ( 2 * sigma**2))
               + bg_0 + x * bg_1

        where A is the amplitude, mu is the expectation value, and sigma is the
        variance. A polynomial background of 0th or 1st order can be added by
        using additional coefficients.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.
            c[0] : amplitude
            c[1] : sigma
            c[2] : expectation value
        x : ndarray
            The input x data points.

        Returns
        -------
        ndarray
            The Gaussian function values for the input parameters.
        """
        return (
            c[0] * (2 * pi) ** (-0.5) / c[1] * exp(-((x - c[2]) ** 2) / (2 * c[1] ** 2))
        )

    @classmethod
    def guess_peak_start_params(
        cls, x: ndarray, y: ndarray, index: Optional[int], **kwargs: Dict
    ) -> tuple[Real]:
        """
        Guess the starting parameters for a Gaussian peak fit.

        Parameters
        ----------
        x : np.ndarray
            The x data points.
        y : np.ndarray
            The function data points to be fitted.
        index : Optional[int]
            The peak index. Use None for a non-indexed single peak or the
             integer peak number (starting with 1).
        **kwargs : dict
            Optional keyword arguments.

        Returns
        -------
        tuple[Real]
            The list with estimated amplitude, width and center parameters.
        """
        if amin(y) < 0:
            y = y + max(amin(y), -0.2 * amax(y))
            y[y < 0] = 0

        _center_start = kwargs.get(f"center{index}_start", x[y.argmax()])
        if "bounds" in kwargs:
            _bounds_index = 2 if index is None else 3 * index + 2
            _center_start = max(kwargs.get("bounds")[0][_bounds_index], _center_start)
            _center_start = min(kwargs.get("bounds")[1][_bounds_index], _center_start)

        _ycenter = cls.get_y_value(_center_start, x, y)
        _high_x = cls.get_fwhm_indices(_center_start, _ycenter, x, y)

        index = "" if index is None else str(index)
        _sigma_start = kwargs.get(f"width{index}_start", None)
        if _sigma_start is None:
            if _high_x.size > 1:
                _sigma_start = (x[_high_x[-1]] - x[_high_x[0]]) / 2.35
            elif _high_x.size == 1:
                _sigma_start = x[1] - x[0]
            else:
                _sigma_start = (x[-1] - x[0]) / 5

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is
        # 1 / (sqrt(2 * PI) * sigma) = 1 / (0.40 * sigma)
        _amp = (_ycenter - amin(y)) * 2.5 * _sigma_start
        return _amp, _sigma_start, _center_start

    @classmethod
    def fwhm(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the FWHM of the fit from the values of the fitted parameters.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Real
            The function FWHM(s) at all peak positions.
        """
        return tuple(
            2.3548200450 * c[_i] for _i in [1 + 3 * _ii for _ii in range(cls.num_peaks)]
        )

    @classmethod
    def amplitude(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the amplitude of the peak from the values of the fitted parameters.

        For a Gaussian function, this corresponds to

        I_peak = A / (sigma * sqrt(2 * Pi))

        Parameters
        ----------
        c : tuple[Real]
            The tuple with the function parameters.

        Returns
        -------
        tuple[Real]
            The function amplitude(s) at all peak positions.
        """
        return tuple(
            0.39894228 * c[0 + 3 * _i] / c[1 + 3 * _i] for _i in range(cls.num_peaks)
        )
