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
Module with the DoubleVoigt class for fitting a double Voigt peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DoubleVoigt"]


from typing import Tuple

from numpy import inf
from scipy.special import voigt_profile

from .utils import DoublePeakMixin
from .voigt import Voigt


class DoubleVoigt(DoublePeakMixin, Voigt):
    """
    Class for fitting a double Voigt function.
    """

    name = "Double Voigt"
    param_bounds_low = [0, 0, 0, -inf, 0, 0, 0, -inf]
    param_bounds_high = [inf, inf, inf, inf, inf, inf, inf, inf]
    param_labels = [
        "amplitude1",
        "sigma1",
        "gamma1",
        "center1",
        "amplitude2",
        "sigma2",
        "gamma2",
        "center2",
    ]
    num_peaks = 2

    @staticmethod
    def fwhm(c: Tuple) -> Tuple[float]:
        """
        Get the FWHM of the fit from the values of the parameters.

        The FWHM for the Voigt function is determined according to Kielkopf:
        John F. Kielkopf: New approximation to the Voigt function with applications
        to spectral-line profile analysis. 8. Auflage. Vol. 63. Journal of the Optical
        Society of America, 1973.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float, float]
            The function FWHMs for the first an second peak.
        """
        return (
            0.5343 * c[2] + (0.2169 * c[2] ** 2 + 5.545177 * c[1] ** 2) ** 0.5,
            0.5343 * c[6] + (0.2169 * c[6] ** 2 + 5.545177 * c[5] ** 2) ** 0.5,
        )

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
        return (c[0], c[4])

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
        return (c[3], c[7])

    @staticmethod
    def amplitude(c: Tuple) -> float:
        """
        Get the amplitude of the peaks from the values of the fitted parameters.

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
            c[0] * voigt_profile(0, c[1], c[2]),
            c[4] * voigt_profile(0, c[5], c[6]),
        )
