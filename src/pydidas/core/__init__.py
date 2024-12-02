# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import sub-packages:
from . import constants
from . import generic_params
from . import io_registry
from . import utils

__all__.extend(["constants", "generic_params", "io_registry", "utils"])

# import exceptions first to be used in other modules
from .exceptions import *

# import __all__ items from modules:
from .base_app import *
from .dataset import *
from .generic_parameters import *
from .hdf5_key import *
from .object_with_parameter_collection import *
from .parameter import *
from .parameter_collection import *
from .parameter_collection_mixin import *
from .pydidas_q_settings import *
from .pydidas_q_settings_mixin import *
from .singleton_factory import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import base_app

__all__.extend(base_app.__all__)
del base_app

from . import dataset

__all__.extend(dataset.__all__)
del dataset

from . import exceptions

__all__.extend(exceptions.__all__)
del exceptions

from . import generic_parameters

__all__.extend(generic_parameters.__all__)
del generic_parameters

from . import hdf5_key

__all__.extend(hdf5_key.__all__)
del hdf5_key

from . import object_with_parameter_collection

__all__.extend(object_with_parameter_collection.__all__)
del object_with_parameter_collection

from . import parameter

__all__.extend(parameter.__all__)
del parameter

from . import parameter_collection

__all__.extend(parameter_collection.__all__)
del parameter_collection

from . import parameter_collection_mixin

__all__.extend(parameter_collection_mixin.__all__)
del parameter_collection_mixin

from . import singleton_factory

__all__.extend(singleton_factory.__all__)
del singleton_factory

from . import pydidas_q_settings

__all__.extend(pydidas_q_settings.__all__)
del pydidas_q_settings

from . import pydidas_q_settings_mixin

__all__.extend(pydidas_q_settings_mixin.__all__)
del pydidas_q_settings_mixin
