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
The diffraction_exp_context package includes the base DiffractionExperiment class and
a singleton instance for describing a diffraction experiment (detector, geometry) and
importers/exporters for different formats as well as a registry metaclass to handle
actual imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import __all__ items from modules:
# even though not explicitly used, the import is necessary for python to read
# the code and to register the classes in the metaclass registry
from . import diff_exp_io_hdf5, diff_exp_io_poni, diff_exp_io_yaml
from .diff_exp import *
from .diff_exp_context import *
from .diff_exp_io import *
from .diff_exp_io_base import *


__all__ = (
    diff_exp.__all__
    + diff_exp_context.__all__
    + diff_exp_io.__all__
    + diff_exp_io_base.__all__
)

# Clean up the namespace:
del (
    diff_exp,
    diff_exp_context,
    diff_exp_io,
    diff_exp_io_base,
    diff_exp_io_yaml,
    diff_exp_io_poni,
    diff_exp_io_hdf5,
)
