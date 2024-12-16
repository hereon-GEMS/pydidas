# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Module with the Voigt class for fitting a Voigt peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Voigt"]


from typing import List, Tuple, Union

from numpy import amax, amin, inf, ndarray
from scipy.special import voigt_profile

from pydidas.core.fitting.fit_func_base import FitFuncBase


class Voigt(FitFuncBase):
    """
    Class for fitting a Voigt function.
    """

    name = "Voigt"
    param_bounds_low = [0, 0, 0, -inf]
    param_bounds_high = [inf, inf, inf, inf]
    param_labels = ["amplitude", "sigma", "gamma", "center"]
    num_peak_params = 4
    center_param_index = 3

    @staticmethod
    def func(c: Tuple, x: ndarray) -> ndarray:
        """
        Get function values for a Voigt function.

        The Voigt function is a convolution of a Gaussian and Lorentzian profile.
        Note that the "gamma" used is the HWHM, i.e. Gamma / 2.

        Parameters
        ----------
        c : Tuple
            The tuple with the function parameters.
            c[0] : amplitude
            c[1] : sigma
            c[2] : gamma
            c[3] : center
        x : ndarray
            The input x data points.

        Returns
        -------
        ndarray
            The Voigt function values for the input parameters.
        """
        return c[0] * voigt_profile(x - c[3], c[1], c[2])

    @classmethod
    def guess_peak_start_params(
        cls, x: ndarray, y: ndarray, index: Union[None, int], **kwargs: dict
    ) -> List[float]:
        """
        Guess the starting parameters for a Voigt peak fit.

        Parameters
        ----------
        x : np.ndarray
            The x data points.
        y : np.ndarray
            The function data points to be fitted.
        index : Union[None, str]
            The peak index. Use None for a non-indexed single peak or the integer peak
            number (starting with 1).
        **kwargs : dict
            Optional keyword arguments.

        Returns
        -------
        List[float]
            The list with estimated amplitude, width and center parameters.
        """
        if amin(y) < 0:
            y = y + max(amin(y), -0.2 * amax(y))
            y[y < 0] = 0
        _center_start = kwargs.get(f"center{index}_start", x[y.argmax()])
        if "bounds" in kwargs:
            _bounds_index = 3 if index is None else 4 * index + 3
            _center_start = max(kwargs.get("bounds")[0][_bounds_index], _center_start)
            _center_start = min(kwargs.get("bounds")[1][_bounds_index], _center_start)
        _ycenter = cls.get_y_value(_center_start, x, y)
        _high_x = cls.get_fwhm_indices(_center_start, _ycenter, x, y)

        index = "" if index is None else str(index)
        _gamma_start = kwargs.get(f"width{index}_start", None)
        if _gamma_start is not None:
            _gamma_start = _gamma_start / 2
            _sigma_start = _gamma_start
        else:
            if _high_x.size > 1:
                _gamma_start = 0.34 * (x[_high_x[-1]] - x[_high_x[0]])
                _sigma_start = 0.34 * (x[_high_x[-1]] - x[_high_x[0]])
            elif _high_x.size == 1:
                _gamma_start = 0.34 * (x[1] - x[0])
                _sigma_start = 0.34 * (x[1] - x[0])
            else:
                _gamma_start = (x[-1] - x[0]) / 6
                _sigma_start = (x[-1] - x[0]) / 6
        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution
        _amp = (_ycenter - amin(y)) / voigt_profile(0, _sigma_start, _gamma_start)
        return [_amp, _sigma_start, _gamma_start, _center_start]

    @classmethod
    def fwhm(cls, c: Tuple[float]) -> float:
        """
        Get the FWHM of the fit from the values of the parameters.

        The FWHM for the Voigt function is determined according to Kielkopf:
        John F. Kielkopf: New approximation to the Voigt function with applications
        to spectral-line profile analysis. 8. Auflage. Vol. 63. Journal of the Optical
        Society of America, 1973.

        The factor for using gamma instead of Gamma has been implemented in the
        two numerical factors for c[2].

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function FWHM.
        """
        return 1.0686 * c[2] + (0.8676 * c[2] ** 2 + 5.545177 * c[1] ** 2) ** 0.5

    @staticmethod
    def amplitude(c: Tuple[float]) -> float:
        """
        Get the amplitude of the peak from the values of the fitted parameters.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function amplitude.
        """
        return c[0] * voigt_profile(0, c[1], c[2])
