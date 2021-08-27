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

from pydidas.unittest_objects.dummy_plugin_collection import (
    DummyPluginCollection, get_random_string, create_plugin_class)
from pydidas.plugins.plugin_collection import _PluginCollection
from pydidas.plugins import BasePlugin, InputPlugin, ProcPlugin, OutputPlugin
from pydidas.core.utilities import flatten_list

class TestPluginCollection(unittest.TestCase):

    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        self.n_per_type = 8
        self.n_plugin = 3 * self.n_per_type
        self._good_filenames = ['test.py', 'test_2.py', 'test3.py']
        self._bad_filenames = ['.test.py', '__test.py', 'test.txt',
                               'another_test.pyc', 'compiled.py~']
        self._syspath = copy.copy(sys.path)

    def tearDown(self):
        shutil.rmtree(self._pluginpath)
        sys.path = self._syspath

    def create_dir_tree(self, path=None, depth=3, width=2):
        path = self._pluginpath if path is None else path
        _dirs = []
        for _width in range(width):
            _dir = os.path.join(path, get_random_string(8))
            os.makedirs(_dir)
            with open(os.path.join(_dir, '__init__.py'), 'w') as f:
                f.write(' ')
            if depth > 1:
                _dirs += self.create_dir_tree(_dir, width=width, depth=depth-1)
            else:
                _dirs += [_dir]
        return _dirs

    def populate_with_python_files(self, dirs):
        self._class_names = []
        if isinstance(dirs, str):
            dirs = [dirs]
        for _dir in dirs:
            for _name in self._good_filenames:
                with open(os.path.join(_dir, _name), 'w') as f:
                    f.write(self.get_random_class_def(store_name=True))
            for _name in self._bad_filenames:
                with open(os.path.join(_dir, _name), 'w') as f:
                    f.write(self.get_random_class_def())

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

    def get_modules_from_dirs(self, dirs):
        _n = len(self._pluginpath) + 1
        _mods = []
        _names = [_name.strip('.py') for _name in self._good_filenames]
        for _dir in dirs:
            _new_module = _dir[_n:].replace(os.sep, '.')
            for _name in _names:
                _mods.append(f'{_new_module}.{_name}'.strip('.'))
        return set(_mods)

    def test_init__no_path(self):
        PC = DummyPluginCollection(n_plugins=0)
        self.assertIsInstance(PC, _PluginCollection)
        self.assertEqual(len(PC.get_all_plugins()), 0)

    def test_clear_collection__no_confirmation(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        PC.clear_collection()
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_clear_collection__with_confirmation(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        PC.clear_collection(True)
        self.assertEqual(PC.plugins, {})
        self.assertEqual(PC._PluginCollection__plugin_type_register, {})

    def test_get_all_plugins_of_type__base(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _plugins = PC.get_all_plugins_of_type('base')
        self.assertEqual(_plugins, [])

    def test_get_all_plugins_of_type__input(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _plugins = PC.get_all_plugins_of_type('input')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(InputPlugin in _plugin.__bases__)

    def test_get_all_plugins_of_type__proc(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _plugins = PC.get_all_plugins_of_type('proc')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(ProcPlugin in _plugin.__bases__)

    def test_get_all_plugins_of_type__output(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _plugins = PC.get_all_plugins_of_type('output')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(OutputPlugin in _plugin.__bases__)

    def test_get_all_plugins(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_get_plugin_by_name__no_name(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _name = get_random_string(12)
        with self.assertRaises(KeyError):
            PC.get_plugin_by_name(_name)

    def test_get_plugin_by_name__known_name(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _name = list(PC.plugins.keys())[0]
        _plugin = PC.get_plugin_by_name(_name)
        self.assertTrue(BasePlugin in _plugin.__bases__[0].__bases__)

    def test_get_all_plugin_names(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _names = PC.get_all_plugin_names()
        self.assertEqual(len(_names), self.n_plugin)
        for _name in _names:
            self.assertIsInstance(_name, str)

    def test_remove_old_item__new_items(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__remove_old_item(_new_cls)
        self.assertEqual(len(PC.plugins), self.n_plugin)

    def test_remove_old_item__existing_item(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _name = PC.get_all_plugin_names()[0]
        PC._PluginCollection__remove_old_item(PC.plugins[_name])
        self.assertFalse(_name in PC.plugins)

    def test_add_new_class(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__add_new_class(_new_cls)
        self.assertTrue(_new_cls.__name__ in PC.plugins)
        self.assertEqual(PC.plugins[_new_cls.__name__ ], _new_cls)

    def test_check_and_register_class__new_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__check_and_register_class(_new_cls)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__wrong_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _name = get_random_string(12)
        PC._PluginCollection__check_and_register_class(float)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)
        self.assertFalse(_name in PC.get_all_plugin_names())

    def test_check_and_register_class__new_class_with_same_name_no_reload(
            self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        _new_cls2 = create_plugin_class(self.n_plugin + 2, 0)
        _new_cls2.__name__ = _new_cls.__name__
        PC._PluginCollection__check_and_register_class(_new_cls)
        PC._PluginCollection__check_and_register_class(_new_cls2)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__new_class_with_same_name_reload(
            self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        _new_cls2 = create_plugin_class(self.n_plugin + 2, 0)
        _new_cls2.__name__ = _new_cls.__name__
        PC._PluginCollection__check_and_register_class(_new_cls)
        PC._PluginCollection__check_and_register_class(_new_cls2, reload=True)
        self.assertEqual(PC.plugins[_new_cls2.__name__], _new_cls2)

    def test_find_files__no_path(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _files = PC.find_files(self._pluginpath)
        self.assertEqual(_files, [])

    def test_find_files__simple_path(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        self.populate_with_python_files(self._pluginpath)
        _files = set(PC.find_files(self._pluginpath))
        _target = set([os.path.join(self._pluginpath, _file)
                        for _file in self._good_filenames])
        self.assertEqual(_files, _target)

    def test_find_files__path_tree(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _dirs = self.create_dir_tree()
        self.populate_with_python_files(_dirs)
        _files = set(PC.find_files(self._pluginpath))
        _target = set(flatten_list(
            [[os.path.join(_dir, _file)
              for _file in self._good_filenames] for _dir in _dirs]))
        self.assertEqual(_files, _target)

    def test_get_modules__no_path(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _modules = PC.get_modules(self._pluginpath)
        self.assertEqual(_modules, [])

    def test_get_modules__simple_path(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        self.populate_with_python_files(self._pluginpath)
        _modules = set(PC.get_modules(self._pluginpath))
        _target = self.get_modules_from_dirs([self._pluginpath])
        self.assertEqual(_modules, _target)

    def test_get_modules__path_tree(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin)
        _dirs = self.create_dir_tree()
        self.populate_with_python_files(_dirs)
        _modules = set(PC.get_modules(self._pluginpath))
        _target = self.get_modules_from_dirs(_dirs)
        self.assertEqual(_modules, _target)

    def test_find_plugins_in_path(self):
        sys.path.insert(0, self._pluginpath)
        PC = DummyPluginCollection(n_plugins=0)
        _dirs = self.create_dir_tree()
        self.populate_with_python_files(_dirs)
        PC._PluginCollection__find_plugins_in_path(self._pluginpath)
        _mods = self.get_modules_from_dirs(_dirs)
        self.assertEqual(len(_mods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))


if __name__ == "__main__":
    unittest.main()
