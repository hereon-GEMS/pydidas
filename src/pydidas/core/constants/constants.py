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
The constants module holds constant number defitions needed in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "LAMBDA_IN_A_TO_E",
    "LAMBDA_IN_M_TO_E",
    "BASE_PLUGIN",
    "INPUT_PLUGIN",
    "PROC_PLUGIN",
    "OUTPUT_PLUGIN",
    "PROC_PLUGIN_GENERIC",
    "PROC_PLUGIN_IMAGE",
    "PROC_PLUGIN_INTEGRATED",
    "PROC_PLUGIN_STRESS_STRAIN",
    "PROC_PLUGIN_TYPE_NAMES",
    "PLUGIN_TYPE_NAMES",
    "FLOAT_REGEX",
]


import re

import scipy.constants


LAMBDA_IN_A_TO_E = 1e10 * (
    scipy.constants.h * scipy.constants.c / (scipy.constants.e * 1e3)
)
"""
float :
    The conversion factor to change a wavelength in Angstrom to an energy in
    keV.
"""

LAMBDA_IN_M_TO_E = scipy.constants.h * scipy.constants.c / (scipy.constants.e * 1e3)
"""
float :
    The conversion factor to change a wavelength in meter to an energy in
    keV.
"""

BASE_PLUGIN = -1
INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

PROC_PLUGIN_GENERIC = 10
PROC_PLUGIN_IMAGE = 11
PROC_PLUGIN_INTEGRATED = 12
PROC_PLUGIN_STRESS_STRAIN = 13

PROC_PLUGIN_TYPE_NAMES = {
    PROC_PLUGIN_GENERIC: "Generic processing plugins",
    PROC_PLUGIN_IMAGE: "Processing plugins for image data",
    PROC_PLUGIN_INTEGRATED: "Processing plugins for integrated data",
    PROC_PLUGIN_STRESS_STRAIN: "Processing plugins for stress-strain analysis",
}

PLUGIN_TYPE_NAMES = {
    INPUT_PLUGIN: "Input plugins",
    PROC_PLUGIN: "Processing plugins",
    OUTPUT_PLUGIN: "Output plugins",
} | PROC_PLUGIN_TYPE_NAMES


FLOAT_REGEX = re.compile(
    r"\s*[+-]?[0-9]*\.?[0-9]+(?:[e][+-]?[0-9]+)?\s*"
    r"|\s*[+-]?[0-9]+\.?[0-9]*(?:[e][+-]?[0-9]+)?\s*"
)
