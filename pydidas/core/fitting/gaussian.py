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
Module with the gaussian function for fitting
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitFuncBase"]

from numpy import exp, pi, where, amax, amin, inf

from .fit_func_base import FitFuncBase
from .fit_func_meta import FitFuncMeta


class Gaussian(FitFuncBase, metaclass=FitFuncMeta):
    """
    Class for fitting a Gaussian function.
    """

    func_name = "Gaussian"
    param_bounds_low = [0, 0, -inf]
    param_bounds_high = [inf, inf, inf]
    param_labels = ["amplitude", "sigma", "center"]

    @classmethod
    def function(cls, c, x):
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
            c[4], optional: The polynomial coefficient for a first order background.
        x : np.ndarray
            The x data points.

        Returns
        -------
        np.ndarray
            The function values for the given x values.
        """
        _gauss = (
            c[0] * (2 * pi) ** (-0.5) / c[1] * exp(-((x - c[2]) ** 2) / (2 * c[1] ** 2))
        )
        if len(c) == 3:
            return _gauss
        if len(c) == 4:
            return _gauss + c[3]
        if len(c) == 5:
            return _gauss + c[3] + c[4] * x
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
        if amin(y) < 0:
            y = y - amin(y)
        # get the points where the function value is larger than half the maximum
        _high_x = where(y >= 0.5 * amax(y))[0]
        if _high_x.size == 0:
            return [0, (x[-1] - x[0]) / 5, (x[0] + x[-1]) / 2]
        _sigma = (x[_high_x[-1]] - x[_high_x[0]]) / 2.35

        # estimate the amplitude based on the maximum data height and the
        # height of the normalized distribution which is
        # 1 / (sqrt(2 * PI) * sigma) = 1 / (0.40 * sigma)
        _amp = (amax(y) - amin(y)) * 2.5 * _sigma
        _center = x[y.argmax()]
        return [_amp, _sigma, _center]
