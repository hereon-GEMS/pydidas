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
The core package defines base classes used throughout the full pydidas
suite.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import sub-packages:
from . import constants, generic_params, io_registry, utils

# import items from modules:
from .base_app import *
from .dataset import *

# import exceptions first to be used in other modules
from .exceptions import *
from .generic_parameters import *
from .hdf5_key import *
from .object_with_parameter_collection import *
from .parameter import *
from .parameter_collection import *
from .parameter_collection_mixin import *
from .pydidas_q_settings import *
from .pydidas_q_settings_mixin import *
from .singleton_factory import *


__all__ = ["constants", "generic_params", "io_registry", "utils"] + (
    base_app.__all__
    + dataset.__all__
    + exceptions.__all__
    + generic_parameters.__all__
    + hdf5_key.__all__
    + object_with_parameter_collection.__all__
    + parameter.__all__
    + parameter_collection.__all__
    + parameter_collection_mixin.__all__
    + pydidas_q_settings.__all__
    + pydidas_q_settings_mixin.__all__
    + singleton_factory.__all__
)

# Clean up the namespace
del (
    base_app,
    dataset,
    exceptions,
    generic_parameters,
    hdf5_key,
    object_with_parameter_collection,
    parameter,
    parameter_collection,
    parameter_collection_mixin,
    pydidas_q_settings,
    pydidas_q_settings_mixin,
    singleton_factory,
)
