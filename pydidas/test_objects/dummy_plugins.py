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

import numpy as np

from pydidas.plugins import InputPlugin, ProcPlugin, OutputPlugin
from pydidas.plugins.plugin_collection import _PluginCollection


_typemap = {0: 'input', 1: 'proc', 2: 'output'}


def get_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def create_plugin_class(number, plugin_type):
    if plugin_type == 0:
        cls = copy.copy(InputPlugin)
    elif plugin_type == 1:
        cls = copy.copy(ProcPlugin)
    elif plugin_type == 2:
        cls = copy.copy(OutputPlugin)
    _name = get_random_string(10)
    _cls = type(_name, cls.__bases__, dict(cls.__dict__))
    _cls.plugin_name = _name
    _cls.number = number
    _cls.__doc__ = get_random_string(600)
    return _cls

try:
    _path = tempfile.mkdtemp()
    DummyPluginCollection = _PluginCollection(_path)
    for num in range(21):
        _class = create_plugin_class(num // 3, num % 3)
        DummyPluginCollection._PluginCollection__plugin_names.append(
            _class.__name__)
        DummyPluginCollection.plugins[_typemap[num % 3]][_class.__name__] = (
            _class)
except:
    raise
finally:
    shutil.rmtree(_path)
