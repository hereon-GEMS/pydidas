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
Module with the TripleLorentzian class for fitting a triple Lorentzian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TripleLorentzian"]


from pydidas.core.fitting.lorentzian import Lorentzian


class TripleLorentzian(Lorentzian):
    """
    Class for fitting a triple Lorentzian function.

    The triple Lorentzian function has the general form

    L(x) = (
        A0 / pi * (Gamma0/ 2) / ((x - center0)**2 + (Gamma0/ 2)**2 )
        + A1 / pi * (Gamma1/ 2) / ((x - center1)**2 + (Gamma1/ 2)**2 )
        + A2 / pi * (Gamma2/ 2) / ((x - center2)**2 + (Gamma2/ 2)**2 )
        + bg_0 + x * bg_1
    )

    where A<i> is the amplitude, Gamma<i> is the FWHM, center<i> is the center. bg_0
    is an optional background offset and bg_1 is the (optional) first order term for
    the background.

        The fit results will be given in form of a tuple c:

    c : tuple[Real]
        The tuple with the function parameters.
        c[0] : amplitude 0
        c[1] : Gamma 0
        c[2] : expectation value 0
        c[3] : amplitude 1
        c[4] : Gamma 1
        c[5] : expectation value 1
        c[6] : amplitude 2
        c[7] : Gamma 2
        c[8] : expectation value 2
        c[9], optional : A background offset.
        c[10], optional : The polynomial coefficient for a first order background.
    """

    name = "Triple Lorentzian"
    num_peaks = 3
    param_bounds_low = Lorentzian.param_bounds_low * num_peaks
    param_bounds_high = Lorentzian.param_bounds_high * num_peaks
    param_labels = [
        f"{key}{i}" for i in range(num_peaks) for key in Lorentzian.param_labels
    ]
