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
Module with the DoubleLorentzian class for fitting a double Lorentzian peak to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DoubleLorentzian"]


from pydidas.core.fitting.lorentzian import Lorentzian


class DoubleLorentzian(Lorentzian):
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
