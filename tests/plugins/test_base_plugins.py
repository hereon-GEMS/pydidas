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

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import random
import tempfile
import shutil
import os
import copy
import sys
from PyQt5 import QtCore

from pydidas.unittest_objects.dummy_plugin_collection import (
    DummyPluginCollection, get_random_string, create_plugin_class)

from pydidas.plugins import BasePlugin, InputPlugin, ProcPlugin, OutputPlugin
from pydidas.plugins.base_plugins import (INPUT_PLUGIN, PROC_PLUGIN,
                                          OUTPUT_PLUGIN)
from pydidas.core import Parameter, ParameterCollection

class TestBasePlugins(unittest.TestCase):

    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._class_names = []

    def tearDown(self):
        shutil.rmtree(self._pluginpath)

    def get_random_class_def(self, store_name=False):
        _plugin = random.choice(['InputPlugin', 'ProcPlugin', 'OutputPlugin'])
        _name = get_random_string(11)
        _str = ('from pydidas.plugins import InputPlugin, ProcPlugin, '
                f'OutputPlugin\n\nclass {_name.upper()}({_plugin}):'
                '\n    basic_plugin = False'
                f'\n    plugin_name = "{_name}"'
                '\n\n    def __init__(self, **kwargs):'
                '\n        super().__init__(**kwargs)'
                f'\n\nclass {get_random_string(11)}:'
                '\n    ...')
        if store_name:
            self._class_names.append(_name.upper())
        return _str

    def test_create_input_plugin(self):
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        self.assertIsInstance(plugin(), BasePlugin)

    def test_get_class_description(self):
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        _text = plugin.get_class_description()
        self.assertIsInstance(_text, str)

    def test_get_class_description_as_dict(self):
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        _doc = plugin.get_class_description_as_dict()
        self.assertIsInstance(_doc, dict)
        for _key, _value in _doc.items():
            self.assertIsInstance(_key, str)
            self.assertIsInstance(_value, str)

    def test_init__plain(self):
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        obj = plugin()
        self.assertIsInstance(obj, BasePlugin)

    def test_init__with_param(self):
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        _param = Parameter('test', str, default='test')
        obj = plugin(_param)
        self.assertTrue('test' in obj.params)

    def test_init__with_param_overwriting_default(self):
        _original_param = Parameter('test', str, default='original test')
        plugin = create_plugin_class(INPUT_PLUGIN, INPUT_PLUGIN)
        plugin.default_params.add_param(_original_param)
        _param = Parameter('test', str, default='test')
        obj = plugin(_param)
        self.assertEqual(obj.get_param_value('test'), _param.value)

    #TODO generic params

if __name__ == "__main__":
    unittest.main()
