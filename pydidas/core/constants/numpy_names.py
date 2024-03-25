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
The colors module holds color names and RGB codes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "NUMPY_DATATYPES",
]

import numpy as np


NUMPY_DATATYPES = {
    "boolean (1 bit integer)": np.bool_,
    "float 16 bit": np.half,
    "float 32 bit": np.single,
    "float 64 bit": np.double,
    "float 128 bit": np.longdouble,
    "int 8 bit": np.int8,
    "int 16 bit": np.int16,
    "int 32 bit": np.int32,
    "int 64 bit": np.int64,
    "unsigned int 8 bit": np.uint8,
    "unsigned int 16 bit": np.uint16,
    "unsigned int 32 bit": np.uint32,
    "unsigned int 64 bit": np.uint64,
}
