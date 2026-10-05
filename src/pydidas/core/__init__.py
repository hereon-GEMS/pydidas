# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import sub-packages:
from . import constants, generic_params, io_registry, lazy_imports, utils

# import items from modules:
from .base_app import BaseApp
from .config_dict import ConfigDict
from .config_dict_mixin import ConfigDictMixin
from .dataset import Dataset
from .exceptions import (
    FileReadError,
    PydidasConfigError,
    PydidasGuiError,
    UserConfigError,
)
from .generic_parameters import get_generic_param_collection, get_generic_parameter
from .object_with_parameter_collection import ObjectWithParameterCollection
from .parameter import Parameter
from .parameter_classes import Hdf5key, NXdataKey
from .parameter_collection import ParameterCollection
from .parameter_collection_mixin import ParameterCollectionMixIn
from .pydidas_q_settings import PydidasQsettings
from .pydidas_q_settings_mixin import PydidasQsettingsMixin
from .singleton import QtSingleton, Singleton


__all__: list[str] = (
    # modules:
    ["constants", "generic_params", "io_registry", "utils", "lazy_imports"]
    # exceptions:
    + ["FileReadError", "UserConfigError", "PydidasConfigError", "PydidasGuiError"]
    # objects:
    + [
        "BaseApp",
        "ConfigDict",
        "ConfigDictMixin",
        "Dataset",
        "Hdf5key",
        "NXdataKey",
        "ObjectWithParameterCollection",
        "Parameter",
        "ParameterCollection",
        "ParameterCollectionMixIn",
        "PydidasQsettings",
        "PydidasQsettingsMixin",
        "Singleton",
        "QtSingleton",
    ]
    # functions:
    + ["get_generic_param_collection", "get_generic_parameter"]
    # exceptions:
    + exceptions.__all__
)
