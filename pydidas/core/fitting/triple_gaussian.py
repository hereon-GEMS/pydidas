# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the TripleGaussian class for fitting a triple Gaussian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TripleGaussian"]


from typing import Tuple

from numpy import inf

from .gaussian import Gaussian
from .utils import TriplePeakMixin


class TripleGaussian(TriplePeakMixin, Gaussian):
    """
    Class for fitting a triple Gaussian function to data.

    The triple Gaussian function has the general form

    f(x) = A1 * (2 * pi)**(-0.5) / sigma1 * exp(-(x - mu1)**2 / ( 2 * sigma1**2))
           + A2 * (2 * pi)**(-0.5) / sigma2 * exp(-(x - mu2)**2 / ( 2 * sigma2**2))
           + A3 * (2 * pi)**(-0.5) / sigma3 * exp(-(x - mu3)**2 / ( 2 * sigma3**2))
           + bg_0 + x * bg_1

    where A1, A2 are the amplitudes, mu1, mu2 are the expectation values, and
    sigma1, sigma2 is the variance. A polinomial background of 0th or 1st order
    can be added by using additional coefficients.
    bg_0 is an optional background offset and bg_1 is the (optional) first order
    term for the background.

    The fit results will be given in form of a tuple c:

    c : tuple
        The tuple with the function parameters.
        c[0] : amplitude 1
        c[1] : sigma 1
        c[2] : expectation value 1
        c[3] : amplitude 2
        c[4] : sigma 2
        c[5] : expectation value 2
        c[6] : amplitude 3
        c[7] : sigma 3
        c[8] : expectation value 3
        c[9], optional : A background offset.
        c[10], optional : The polynomial coefficient for a first order background.
    """

    name = "Triple Gaussian"
    param_bounds_low = [0, 0, -inf, 0, 0, -inf, 0, 0, -inf]
    param_bounds_high = [inf, inf, inf, inf, inf, inf, inf, inf, inf]
    param_labels = [
        "amplitude1",
        "sigma1",
        "center1",
        "amplitude2",
        "sigma2",
        "center2",
        "amplitude3",
        "sigma3",
        "center3",
    ]
    num_peaks = 3

    @staticmethod
    def fwhm(c: Tuple) -> Tuple[float]:
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float, float]
            The function FWHMs for the first an second peak.
        """
        return (2.354820 * c[1], 2.354820 * c[4], 2.354820 * c[7])

    @staticmethod
    def area(c: Tuple) -> Tuple[float]:
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal to the amplitude term.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float]
            The areas of the two peaks defined through the given parameters c.
        """
        return (c[0], c[3], c[6])

    @staticmethod
    def center(c: Tuple[float]) -> Tuple[float]:
        """
        Get the center positions.

        Parameters
        ----------
        c : Tuple[float]
            The fitted parameters.

        Returns
        -------
        Tuple[float]
            The center positions of the peaks.
        """
        return (c[2], c[5], c[8])

    @staticmethod
    def amplitude(c: Tuple) -> Tuple[float]:
        """
        Get the amplitude of the peaks from the values of the fitted parameters.

        For a Gaussian function, this corresponds to

        I_peak = A / (sigma * sqrt(2 * Pi))

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float]
            The peaks' amplitude.
        """
        return (
            0.39894228 * c[0] / c[1],
            0.39894228 * c[3] / c[4],
            0.39894228 * c[6] / c[7],
        )
