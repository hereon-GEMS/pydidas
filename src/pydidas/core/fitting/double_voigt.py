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
Module with the DoubleVoigt class for fitting a double Voigt peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DoubleVoigt"]


from pydidas.core.fitting.voigt import Voigt


class DoubleVoigt(Voigt):
    """
    Class for fitting a double Voigt function.

    This class uses the scipy.special.voigt_profile to calculate the function values.

    V(x) = (
        A0 * voigt_profile(x - center0, sigma0, gamma0)
        + A1 * voigt_profile(x - center1, sigma1, gamma1)
        + bg_0 + x * bg_1
    )

    where A<i> is the amplitude, sigma<i> and gamma<i> are the widths of the
    Gaussian and Lorentzian shares and center<i> are the center positions. bg_0
    is an optional background offset and bg_1 is the (optional) first order term
    for the background.

    The fit results will be given in form of a tuple c:

    c : tuple[Real]
        The tuple with the function parameters.
        c[0] : amplitude 0
        c[1] : sigma 0
        c[2] : gamma 0
        c[3] : center 0
        c[4] : amplitude 1
        c[5] : sigma 1
        c[6] : gamma 1
        c[7] : center 1
        c[8], optional : A background offset.
        c[9], optional : The polynomial coefficient for a first order background.
    """

    name = "Double Voigt"
    num_peaks = 2
    param_bounds_low = Voigt.param_bounds_low * num_peaks
    param_bounds_high = Voigt.param_bounds_high * num_peaks
    param_labels = [f"{key}{i}" for i in range(num_peaks) for key in Voigt.param_labels]
