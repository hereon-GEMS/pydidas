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
The core.fitting package defines generic functions for fitting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# Import all fit functions to have them available in the
# fitting MetaClass
from . import (
    double_gaussian,
    double_lorentzian,
    double_voigt,
    gaussian,
    lorentzian,
    triple_gaussian,
    triple_lorentzian,
    triple_voigt,
    voigt,
)
from .fit_func_base import *
from .fit_func_meta import *


__all__ = fit_func_base.__all__ + fit_func_meta.__all__

# Clean up the namespace:
del (
    fit_func_base,
    fit_func_meta,
    voigt,
    lorentzian,
    gaussian,
    double_gaussian,
    double_lorentzian,
    double_voigt,
    triple_gaussian,
    triple_lorentzian,
    triple_voigt,
)
