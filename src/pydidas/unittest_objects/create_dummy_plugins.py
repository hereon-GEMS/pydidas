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
The create_dummy_plugins module includes functions to create plugin classes dynamically
for testing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_base_class", "create_plugin_class"]


import copy
import inspect

from qtpy import QtCore

from pydidas.core.constants import BASE_PLUGIN, INPUT_PLUGIN, OUTPUT_PLUGIN, PROC_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin, InputPlugin, OutputPlugin, ProcPlugin


def create_base_class(base: type) -> type:
    """
    Create a single-use base class for a temporary plugin.

    This single-use class is required to allow management of class attributes.

    Parameters
    ----------
    base : type
        The base class to be duplicated.

    Returns
    -------
    _cls : type
        A duplicate with a unique set of class attributes.
    """
    _cls = type(
        f"Test{base.__name__}",
        (base,),
        {
            key: copy.copy(val)
            for key, val in base.__dict__.items()
            if not (
                inspect.ismethod(getattr(base, key))
                or isinstance(val, (QtCore.SignalInstance, QtCore.QMetaObject))
            )
        },
    )
    _cls.default_params = base.default_params.copy()
    _cls.generic_params = base.generic_params.copy()
    return _cls


def create_plugin_class(plugin_type: int, number: int = 0) -> type:
    """
    Create a unique Plugin class with random attributes.

    Parameters
    ----------
    plugin_type : int
        The type code for each plugin.
    number : int, optional
        A number. Can be used to identify plugins. The default is 0.

    Returns
    -------
    _cls : pydidas.plugins.BasePlugin subclass
        A concrete implementation of BasePlugin, InputPlugin, ProcPlugin,
        or OutputPlugin.
    """
    if plugin_type == BASE_PLUGIN:
        _cls = create_base_class(BasePlugin)
    if plugin_type == INPUT_PLUGIN:
        _cls = create_base_class(InputPlugin)
    elif plugin_type == PROC_PLUGIN:
        _cls = create_base_class(ProcPlugin)
    elif plugin_type == OUTPUT_PLUGIN:
        _cls = create_base_class(OutputPlugin)
    _name = get_random_string(10)
    _cls = type(_name, (_cls,), dict(_cls.__dict__))
    _cls.plugin_name = f"Plugin {_name}"
    _cls.number = number
    _cls.__doc__ = get_random_string(600)
    return _cls
