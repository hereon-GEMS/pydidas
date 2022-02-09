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
The core package defines base classes used throughout the full pydidas
suite.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from PyQt5 import QtCore

# import sub-packages:
from . import constants
from . import io_registry
from . import utils
__all__.extend(['constants', 'io_registry', 'utils'])

# import __all__ items from modules:
from .base_app import *
from .dataset import *
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


# if not existing, initialize all QSettings with the default values from the
# default Parameters to avoid having "None" keys returned.
settings = QtCore.QSettings('Hereon', 'pydidas')
for _key in constants.QSETTINGS_GLOBAL_KEYS:
    _val = settings.value(f'global/{_key}')
    if _val is None:
        _param = get_generic_parameter(_key)
        settings.setValue(f'global/{_key}', _param.default)
del settings
del QtCore
