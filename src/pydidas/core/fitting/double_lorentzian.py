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
Module with the DoubleLorentzian class for fitting a double Lorentzian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DoubleLorentzian"]


from typing import Tuple

from numpy import pi

from pydidas.core.fitting.lorentzian import Lorentzian
from pydidas.core.fitting.multi_peak_mixin import MultiPeakMixin


class DoubleLorentzian(MultiPeakMixin, Lorentzian):
    """
    Class for fitting a double Lorentzian function.

    The double Lorentzian function has the general form

    L(x) = (
        A0 / pi * (Gamma0/ 2) / ((x - center0)**2 + (Gamma0/ 2)**2 )
        + A1 / pi * (Gamma1/ 2) / ((x - center1)**2 + (Gamma1/ 2)**2 )
        + bg_0 + x * bg_1
    )

    where A0, A1 are the amplitudes, Gamma0, Gamma1 are the FWHMs, center0, center1
    are the centers. bg_0 is an optional background offset and bg_1 is the (optional)
    first order term for the background.
    """

    name = "Double Lorentzian"
    num_peaks = 2
    param_bounds_low = Lorentzian.param_bounds_low * num_peaks
    param_bounds_high = Lorentzian.param_bounds_high * num_peaks
    param_labels = [
        f"{key}{i}" for i in range(num_peaks) for key in Lorentzian.param_labels
    ]

    @staticmethod
    def fwhm(c: Tuple[float]) -> Tuple[float]:
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float, float]
            The function FWHMs for the first an second peak.
        """
        return (c[1], c[4])

    @staticmethod
    def area(c: Tuple[float]) -> Tuple[float]:
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal to the amplitude term.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.

        Returns
        -------
        Tuple[float]
            The areas of the two peaks defined through the given parameters c.
        """
        return (c[0], c[3])

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
        return (c[2], c[5])

    @staticmethod
    def amplitude(c: Tuple) -> float:
        """
        Get the amplitude of the peaks from the values of the fitted parameters.

        For a Lorentzian function, this corresponds to

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
        return (2 * c[0] / pi / c[1], 2 * c[3] / pi / c[4])
