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
Module with the Lorentz function for fitting
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitFuncBase"]

from numpy import pi, where, amax, amin, inf

from .fit_func_base import FitFuncBase
from .fit_func_meta import FitFuncMeta


class Lorentzian(FitFuncBase, metaclass=FitFuncMeta):
    """
    Class for fitting a Lorentzian function.
    """

    func_name = "Lorentzian"
    param_bounds_low = [0, 0, -inf]
    param_bounds_high = [inf, inf, inf]
    param_labels = ["amplitude", "gamma", "center"]

    @classmethod
    def function(cls, c, x):
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
        _lorentz = c[0] / pi * (0.5 * c[1]) / ((x - c[2]) ** 2 + (0.5 * c[1]) ** 2)
        if len(c) == 3:
            return _lorentz
        if len(c) == 4:
            return _lorentz + c[3]
        if len(c) == 5:
            return _lorentz + c[3] + c[4] * x
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
        # get the points where the function value is larger than half the maximum
        _high_x = where(y >= 0.5 * amax(y))[0]
        _gamma = (x[_high_x[-1]] - x[_high_x[0]]) / 2

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is
        # 1 / (sqrt(2 * PI) * sigma) = 1 / (0.40 * sigma)
        _amp = (amax(y) - amin(y)) * _gamma * pi

        _center = x[y.argmax()]
        return [_amp, _gamma, _center]
