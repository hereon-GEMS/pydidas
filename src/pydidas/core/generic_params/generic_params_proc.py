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
The generic_params_experiment module holds all the required data to create generic
Parameters for the experiment context.
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_PROC"]


from pydidas.core.constants import ASCII_TO_UNI


GENERIC_PARAMS_PROC = {
    "d_spacing_unit": {
        "type": str,
        "default": "Angstrom",
        "name": "d-spacing unit",
        "choices": ["Angstrom", "nm"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            f"The output d-spacing unit. {ASCII_TO_UNI['Angstrom']} for Angstroms "
            "and nm for nanometers."
        ),
    },
}
