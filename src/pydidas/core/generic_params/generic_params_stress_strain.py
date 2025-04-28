# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
The generic_params_other module holds all the required data to create generic
Parameters which are are not included in other specialized modules.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_STRESS_STRAIN"]


GENERIC_PARAMS_STRESS_STRAIN = {
    ###############################
    # Generic processing parameters
    ###############################
    "sin_square_chi_low_fit_limit": {
        "type": float,
        "default": 0,
        "name": "Lower bounds for fitting",
        "choices": None,
        "unit": "",
        "range": (0, 1),
        "allow_None": False,
        "tooltip": (
            "The lower boundary for the fitting range (in sin^2(chi)). This "
            "parameter is used to set the lower limit for the fitting range and "
            "it allows to ignore the first few points of the data."
        ),
    },
    "sin_square_chi_high_fit_limit": {
        "type": float,
        "default": 1,
        "name": "Upper bounds for fitting",
        "choices": None,
        "unit": "",
        "range": (0, 1),
        "allow_None": False,
        "tooltip": (
            "The upper boundary for the fitting range (in sin^2(chi)). This "
            "parameter is used to set the upper limit for the fitting range and "
            "it allows to ignore the last few points of the data."
        ),
    },
}
