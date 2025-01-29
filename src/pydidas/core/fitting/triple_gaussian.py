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
Module with the TripleGaussian class for fitting a triple Gaussian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TripleGaussian"]


from pydidas.core.fitting.gaussian import Gaussian


class TripleGaussian(Gaussian):
    """
    Class for fitting a triple Gaussian function to data.

    The triple Gaussian function has the general form

    f(x) = A0 * (2 * pi)**(-0.5) / sigma0 * exp(-(x - mu0)**2 / ( 2 * sigma0**2))
           + A1 * (2 * pi)**(-0.5) / sigma1 * exp(-(x - mu1)**2 / ( 2 * sigma1**2))
           + A2 * (2 * pi)**(-0.5) / sigma2 * exp(-(x - mu2)**2 / ( 2 * sigma2**2))
           + bg_0 + x * bg_1

    where A0, A1, A2 are the amplitudes, mu0mu0, , mu1 are the expectation values,
    and sigma0, sigma1, sigma2 is the variance. A polinomial background of 0th or
    1st order can be added by using additional coefficients.
    bg_0 is an optional background offset and bg_1 is the (optional) first order
    term for the background.

    The fit results will be given in form of a tuple c:

    c : tuple
        The tuple with the function parameters.
        c[0] : amplitude 0
        c[1] : sigma 0
        c[2] : expectation value 0
        c[3] : amplitude 1
        c[4] : sigma 1
        c[5] : expectation value 1
        c[6] : amplitude 2
        c[7] : sigma 2
        c[8] : expectation value 2
        c[9], optional : A background offset.
        c[10], optional : The polynomial coefficient for a first order background.
    """

    name = "Triple Gaussian"
    num_peaks = 3
    param_bounds_low = Gaussian.param_bounds_low * num_peaks
    param_bounds_high = Gaussian.param_bounds_high * num_peaks
    param_labels = [
        f"{key}{i}" for i in range(num_peaks) for key in Gaussian.param_labels
    ]
