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
Module with the TripleVoigt class for fitting a triple Voigt peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TripleVoigt"]


from typing import Tuple

from scipy.special import voigt_profile

from .multi_peak_mixin import MultiPeakMixin
from .voigt import Voigt


class TripleVoigt(MultiPeakMixin, Voigt):
    """
    Class for fitting a triple Voigt function.

    This class uses the scipy.special.voigt_profile to calculate the function values.

    V(x) = (
        A0 * voigt_profile(x - center0, sigma0, gamma0)
        + A1 * voigt_profile(x - center1, sigma1, gamma1)
        + A2 * voigt_profile(x - center2, sigma2, gamma2)
        + bg_0 + x * bg_1
    )

    where A<i> is the amplitude, sigma<i> and gamma<i> are the widths of the
    Gaussian and Lorentzian shares and center<i> are the center positions. bg_0
    is an optional background offset and bg_1 is the (optional) first order term
    for the background.

    The fit results will be given in form of a tuple c:

    c : tuple
        The tuple with the function parameters.
        c[0] : amplitude 0
        c[1] : sigma 0
        c[2] : gamma 0
        c[3] : center 0
        c[4] : amplitude 1
        c[5] : sigma 1
        c[6] : gamma 1
        c[7] : center 1
        c[8] : amplitude 2
        c[9] : sigma 2
        c[10] : gamma 2
        c[11] : center 2
        c[12], optional : A background offset.
        c[13], optional : The polynomial coefficient for a first order background.
    """

    name = "Triple Voigt"
    num_peaks = 3
    param_bounds_low = Voigt.param_bounds_low * num_peaks
    param_bounds_high = Voigt.param_bounds_high * num_peaks
    param_labels = [f"{key}{i}" for i in range(num_peaks) for key in Voigt.param_labels]

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
            0.5343 * c[10] + (0.2169 * c[10] ** 2 + 5.545177 * c[9] ** 2) ** 0.5,
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
        return (c[0], c[4], c[8])

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
        return (c[3], c[7], c[11])

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
            c[8] * voigt_profile(0, c[9], c[10]),
        )
