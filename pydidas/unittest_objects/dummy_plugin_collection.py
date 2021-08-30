# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import random
import copy
import string
import tempfile
import shutil

from pydidas.core import ParameterCollection
from pydidas.plugins import InputPlugin, ProcPlugin, OutputPlugin
from pydidas.plugins.plugin_collection import _PluginCollection


_typemap = {0: 'input', 1: 'proc', 2: 'output'}


def get_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def create_plugin_class(number, plugin_type):
    if plugin_type == 0:
        cls = InputPlugin
    elif plugin_type == 1:
        cls = ProcPlugin
    elif plugin_type == 2:
        cls = OutputPlugin
    _name = get_random_string(10)
    _cls = type(_name, (cls,), dict(cls.__dict__))
    _cls.basic_plugin = False
    _cls.plugin_name = f'Plugin {_name}'
    _cls.number = number
    _cls.params = ParameterCollection()
    _cls.__doc__ = get_random_string(600)
    return _cls


class DummyPluginCollection(_PluginCollection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _nplugins = kwargs.get('n_plugins', 21)
        for num in range(_nplugins):
            _class = create_plugin_class(num // 3, num % 3)
            self._PluginCollection__add_new_class(_class)
            # _name = _class.__name__
            # self.plugins[_name] = _class
            # self._PluginCollection__plugin_types[_name] = num % 3
            # self._PluginCollection__plugin_names[_name] = num % 3
