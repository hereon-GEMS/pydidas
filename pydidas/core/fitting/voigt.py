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
Module with the Voigt function for fitting
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitFuncBase"]

from numpy import where, amax, amin, inf
from scipy.special import voigt_profile

from .fit_func_base import FitFuncBase
from .fit_func_meta import FitFuncMeta


class Voigt(FitFuncBase, metaclass=FitFuncMeta):
    """
    Class for fitting a Voigt function.
    """

    func_name = "Voigt"
    param_bounds_low = [0, 0, 0, -inf]
    param_bounds_high = [inf, inf, inf, inf]
    param_labels = ["amplitude", "sigma", "gamma", "center"]

    @classmethod
    def function(cls, c, x):
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

        Returns
        -------
        list
            The list with the starting fit parameters.
        """
        # guess that both distributions have the same weight, i.e. the generic values
        # are divided by 2:
        _high_x = where(y >= 0.5 * amax(y))[0]
        _sigma = 0.3 * (x[_high_x[-1]] - x[_high_x[0]])
        _gamma = 0.3 * (x[_high_x[-1]] - x[_high_x[0]])

        # estimate the amplitude based on the maximum data height and the
        # amplitude of a function with the average of both distributions
        _amp = (amax(y) - amin(y)) / voigt_profile(0, _sigma, _gamma)
        _center = x[y.argmax()]
        return [_amp, _sigma, _gamma, _center]
