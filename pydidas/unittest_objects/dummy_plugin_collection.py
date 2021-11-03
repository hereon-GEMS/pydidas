# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The DummyPluginCollection module holds the DummyPluginCollection class used
for testing as well as the "create_plugin_class" function which can be used
to create plugin classes dynamically.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['get_random_string', 'create_plugin_class', 'DummyPluginCollection']

import random
import copy
import string
import inspect

from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import InputPlugin, ProcPlugin, OutputPlugin, BasePlugin
from pydidas.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                               OUTPUT_PLUGIN)
from pydidas.plugins.plugin_collection import _PluginCollection


def get_random_string(length):
    """
    Get a random string of a specific length.

    Parameters
    ----------
    length : int
        The length of the output string.

    Returns
    -------
    str
        The random string.
    """
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def create_base_class(base):
    """
    Create a single-use base class for a temporary plugin to allow
    managemant of classs attributes.

    Parameters
    ----------
    cls : type
        The base class to be duplicated.

    Returns
    -------
    _cls : type
        A duplicate with a unique set of class attributes.
    """
    _cls = type(f'Test{base.__name__}', (base,),
                {key: copy.copy(val)
                 for key, val in base.__dict__.items()
                 if not inspect.ismethod(getattr(base, key))})
    _cls.default_params = base.default_params.get_copy()
    _cls.generic_params = base.generic_params.get_copy()
    return _cls


def create_plugin_class(number, plugin_type, use_filename=True):
    """
    Create a unique Plugin class with random attributes.

    Parameters
    ----------
    number : int
        A number. Can be used to identify plugins.
    plugin_type : int
        The type code for each plugin.
    use_filename : bool, optional
        Keyword (for input plugins only) to setup the class with either the
        "filename" or "first_file" Parameter. The default is True.

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
    _cls.basic_plugin = False
    _cls.plugin_name = f'Plugin {_name}'
    _cls.number = number
    _cls.params = ParameterCollection()
    if plugin_type == 0:
        if use_filename:
            if 'first_file' in _cls.default_params:
                del _cls.default_params['first_file']
            if 'filename' not in _cls.default_params:
                _cls.default_params.add_param(get_generic_parameter(
                    'filename'))
        else:
            if 'filename' in _cls.default_params:
                del _cls.default_params['filename']
            if 'first_file' not in _cls.default_params:
                _cls.default_params.add_param(get_generic_parameter(
                    'first_file'))
    _cls.__doc__ = get_random_string(600)
    return _cls


class DummyPluginCollection(_PluginCollection):
    """
    Create a unique DummyPluginCollection with a defined path and a number
    of random plugins.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _nplugins = kwargs.get('n_plugins', 21)
        for num in range(_nplugins):
            _class = create_plugin_class(num // 3, num % 3)
            self._PluginCollection__add_new_class(_class)
