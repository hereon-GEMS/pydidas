# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The constants module holds constant nmumber defitions needed in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['LAMBDA_IN_A_TO_E', 'LAMBDA_IN_M_TO_E',
           'BASE_PLUGIN', 'INPUT_PLUGIN', 'PROC_PLUGIN',
           'OUTPUT_PLUGIN', 'pyFAI_UNITS', 'pyFAI_METHOD']

import scipy.constants


LAMBDA_IN_A_TO_E = 1e10 * (scipy.constants.h * scipy.constants.c
                    / ( scipy.constants.e * 1e3))
"""
float :
    The conversion factor to change a wavelength in Angstrom to an energy in
    keV.
"""

LAMBDA_IN_M_TO_E = (scipy.constants.h * scipy.constants.c
                    / ( scipy.constants.e * 1e3))
"""
float :
    The conversion factor to change a wavelength in meter to an energy in
    keV.
"""

BASE_PLUGIN = -1
INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

pyFAI_UNITS = {'Q / nm^-1': 'q_nm^-1',
               'Q / A^-1': 'q_A^-1',
               '2theta / deg': '2th_deg',
               '2theta / rad': '2th_rad',
               'r / mm': 'r_mm',
               'chi / deg': 'chi_deg',
               'chi / rad': 'chi_rad'}

pyFAI_METHOD = {'CSR': 'csr',
                'CSR OpenCL': 'csr ocl',
                'LUT': 'lut',
                'LUT OpenCL': 'lut ocl'}
