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
from PyQt5 import QtCore

from pydidas.unittest_objects.dummy_plugin_collection import (
    DummyPluginCollection, get_random_string, create_plugin_class)
from pydidas.plugins.plugin_collection import _PluginCollection
from pydidas.plugins.plugin_collection_util_funcs import (
    get_generic_plugin_path)
from pydidas.plugins import BasePlugin, InputPlugin, ProcPlugin, OutputPlugin

class TestPluginCollection(unittest.TestCase):

    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        self._otherpaths = []
        self._class_names = []
        self.n_per_type = 8
        self.n_plugin = 3 * self.n_per_type
        self._good_filenames = ['test.py', 'test_2.py', 'test3.py']
        self._bad_filenames = ['.test.py', '__test.py', 'test.txt',
                               'another_test.pyc', 'compiled.py~']
        self._syspath = copy.copy(sys.path)
        self._qsettings = QtCore.QSettings('Hereon', 'pydidas')
        self._qsettings_plugin_path = self._qsettings.value('global/plugin_path')
        self._qsettings.setValue('global/plugin_path', '')

    def tearDown(self):
        DummyPluginCollection().clear_collection(True)
        shutil.rmtree(self._pluginpath)
        for _path in self._otherpaths:
            shutil.rmtree(_path)
        sys.path = self._syspath
        self._qsettings.setValue('global/plugin_path',
                                 self._qsettings_plugin_path)

    def create_plugin_file_tree(self, path=None, depth=3, width=2):
        path = self._pluginpath if path is None else path
        # sys.path.insert(0, path)
        _dirs = self.create_dir_tree(path, depth, width)
        self.populate_with_python_files(_dirs)
        _mods = self.get_modules_from_dirs(_dirs)
        return _dirs, _mods

    def create_dir_tree(self, path=None, depth=3, width=2):
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

    def test_init__empty_path(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self.assertIsInstance(PC, _PluginCollection)
        self.assertEqual(len(PC.get_all_plugins()), 0)

    def test_clear_collection__no_confirmation(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        PC.clear_collection()
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_clear_collection__with_confirmation(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        PC.clear_collection(True)
        self.assertEqual(PC.plugins, {})
        self.assertEqual(PC._PluginCollection__plugin_types, {})

    def test_get_all_plugins_of_type__base(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _plugins = PC.get_all_plugins_of_type('base')
        self.assertEqual(_plugins, [])

    def test_get_all_plugins_of_type__input(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _plugins = PC.get_all_plugins_of_type('input')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(InputPlugin in _plugin.__bases__)

    def test_get_all_plugins_of_type__proc(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _plugins = PC.get_all_plugins_of_type('proc')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(ProcPlugin in _plugin.__bases__)

    def test_get_all_plugins_of_type__output(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _plugins = PC.get_all_plugins_of_type('output')
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(OutputPlugin in _plugin.__bases__)

    def test_get_all_plugins(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_get_plugin_by_name__no_name(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _name = get_random_string(12)
        with self.assertRaises(KeyError):
            PC.get_plugin_by_name(_name)

    def test_get_plugin_by_name__known_name(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _name = list(PC.plugins.keys())[0]
        _plugin = PC.get_plugin_by_name(_name)
        self.assertTrue(BasePlugin in _plugin.__bases__[0].__bases__)

    def test_get_all_plugin_names(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _names = PC.get_all_plugin_names()
        self.assertEqual(len(_names), self.n_plugin)
        for _name in _names:
            self.assertIsInstance(_name, str)

    def test_remove_plugin_from_collection__new_items(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__remove_plugin_from_collection(_new_cls)
        self.assertEqual(len(PC.plugins), self.n_plugin)

    def test_remove_plugin_from_collection__existing_item(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _name = PC.get_all_plugin_names()[0]
        PC._PluginCollection__remove_plugin_from_collection(PC.plugins[_name])
        self.assertFalse(_name in PC.plugins)

    def test_add_new_class(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__add_new_class(_new_cls)
        self.assertTrue(_new_cls.__name__ in PC.plugins)
        self.assertEqual(PC.plugins[_new_cls.__name__ ], _new_cls)

    def test_check_and_register_class__new_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        PC._PluginCollection__check_and_register_class(_new_cls)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__wrong_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _name = get_random_string(12)
        PC._PluginCollection__check_and_register_class(float)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)
        self.assertFalse(_name in PC.get_all_plugin_names())

    def test_check_and_register_class__new_class_with_same_name_no_reload(
            self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        _new_cls2 = create_plugin_class(self.n_plugin + 2, 0)
        _new_cls2.__name__ = _new_cls.__name__
        PC._PluginCollection__check_and_register_class(_new_cls)
        PC._PluginCollection__check_and_register_class(_new_cls2)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__new_class_with_same_name_reload(
            self):
        self.n_plugin = 2
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _new_cls = create_plugin_class(self.n_plugin + 1, 0)
        _new_cls2 = create_plugin_class(self.n_plugin + 2, 0)
        _new_cls2.__name__ = _new_cls.__name__
        PC._PluginCollection__check_and_register_class(_new_cls)
        PC._PluginCollection__check_and_register_class(_new_cls2, reload=True)
        self.assertEqual(PC.plugins[_new_cls2.__name__], _new_cls2)

    def test_import_module_and_get_classes_in_module(self):
        _dirs, _mods = self.create_plugin_file_tree(width=1, depth=1)
        _fname = os.path.join(_dirs[0], self._good_filenames[0])
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _members = PC._PluginCollection__import_module_and_get_classes_in_module(
            'some other name', _fname)
        _classes = [_cls for _name, _cls in _members]
        for _cls in [InputPlugin, ProcPlugin, OutputPlugin]:
            self.assertIn(_cls, _classes)

    def test_get_valid_modules_and_filenames__simple_path(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        self.populate_with_python_files(self._pluginpath)
        _modules = set(PC._get_valid_modules_and_filenames(
            self._pluginpath).keys())
        _target = self.get_modules_from_dirs([self._pluginpath])
        self.assertEqual(_modules, _target)

    def test_get_valid_modules_and_filenames__path_tree(self):
        PC = DummyPluginCollection(n_plugins=self.n_plugin,
                                   plugin_path=self._pluginpath)
        _dirs, _mods = self.create_plugin_file_tree()
        _modules = set(PC._get_valid_modules_and_filenames(
            self._pluginpath).keys())
        _target = self.get_modules_from_dirs(_dirs)
        self.assertEqual(_modules, _target)

    def test_store_plugin_path__no_path(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        _path = os.path.join(self._pluginpath, get_random_string(8))
        PC._store_plugin_path(_path)
        _qplugin_path = PC.q_settings.value('global/plugin_path')

        self.assertEqual(_qplugin_path, self._pluginpath)
        self.assertNotIn(_path, sys.path)

    def test_store_plugin_path__existing_paths(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        for index in range(3):
            _path = tempfile.mkdtemp()
            self._otherpaths.append(_path)
            PC._store_plugin_path(_path)
        _paths = [self._pluginpath] + self._otherpaths
        _qplugin_path = PC.q_settings.value('global/plugin_path')
        self.assertEqual(_qplugin_path, ';;'.join(_paths))
        for _path in self._otherpaths:
            self.assertIn(_path, PC._PluginCollection__plugin_paths)

    def test_find_and_register_plugins_in_path__path_does_not_exist(self):
        _path = os.path.join(self._pluginpath, get_random_string(8))
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        PC._find_and_register_plugins_in_path(_path)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__path_empty(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__populated(self):
        self.populate_with_python_files(self._pluginpath)
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), len(self._good_filenames))

    def test_find_and_register_plugins__single_path(self):
        _dirs, _mods = self.create_plugin_file_tree()
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        PC.find_and_register_plugins(self._pluginpath)
        self.assertEqual(len(_mods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_find_and_register_plugins__multiple_paths(self):
        _dirs, _mods = self.create_plugin_file_tree()
        self._otherpaths.append(tempfile.mkdtemp())
        _dirs2, _mods2 = self.create_plugin_file_tree(self._otherpaths[0])
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        PC.find_and_register_plugins(self._pluginpath, self._otherpaths[0])
        _newmods = _mods | _mods2
        self.assertEqual(len(_newmods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_get_q_settings_plugin_path__no_path_set(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        _qplugin_path = PC._PluginCollection__get_q_settings_plugin_path()
        self.assertEqual(_qplugin_path, [self._pluginpath])

    def test_get_q_settings_plugin_path__single_path(self):
        self._pluginpath
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._qsettings.setValue('global/plugin_path', self._pluginpath)
        _qplugin_path = PC._PluginCollection__get_q_settings_plugin_path()
        self.assertEqual([self._pluginpath], _qplugin_path)

    def test_get_q_settings_plugin_path__multiple_paths(self):
        _paths = ['test1', 'some/other/path', 'test_23.456']
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._qsettings.setValue('global/plugin_path', ';;'.join(_paths))
        _qplugin_path = PC._PluginCollection__get_q_settings_plugin_path()
        self.assertEqual(_paths, _qplugin_path)

    def test_get_generic_plugin_path__no_q_path(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._qsettings.setValue('global/plugin_path', None)
        _path = PC._PluginCollection__get_generic_plugin_path()
        self.assertEqual(_path, get_generic_plugin_path())

    def test_get_generic_plugin_path__empty_q_path(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._qsettings.setValue('global/plugin_path', '')
        _path = PC._PluginCollection__get_generic_plugin_path()
        self.assertEqual(_path, get_generic_plugin_path())

    def test_get_generic_plugin_path__q_path(self):
        _path = 'some/path/to/nowhere'
        PC = DummyPluginCollection(n_plugins=0, plugin_path=self._pluginpath)
        self._qsettings.setValue('global/plugin_path', _path)
        _newpath = PC._PluginCollection__get_generic_plugin_path()
        self.assertEqual([_path], _newpath)

    def test_get_plugin_path_from_kwargs__no_plugin_path(self):
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False)
        _path = PC._PluginCollection__get_plugin_path_from_kwargs(**kwargs)
        self.assertIsNone(_path)

    def test_get_plugin_path_from_kwargs__single_str(self):
        _entry = '  some string '
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entry)
        _path = PC._PluginCollection__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, [_entry.strip()])

    def test_get_plugin_path_from_kwargs__multi_str(self):
        _entries = ['something', 'another_string', 'this/is/not/a/directory',
                    'this:string:has#special chars']

        _entry = ';;'.join([(random.choice(['', ' ', '   ', '    '])
                             + item
                             + random.choice(['', ' ', '   ', '    ']))
                            for item in _entries])
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entry)
        _path = PC._PluginCollection__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, _entries)

    def test_get_plugin_path_from_kwargs__list(self):
        _entries = ['something', 'another_string', 'this/is/not/a/directory',
                    'this:string:has#special chars']
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entries)
        _path = PC._PluginCollection__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, _entries)

    def test_clear_qsettings(self):
        self._qsettings.setValue('global/plugin_path', get_random_string(30))
        DummyPluginCollection.clear_qsettings()
        self.assertEqual(self._qsettings.value('global/plugin_path'), '')

if __name__ == "__main__":
    unittest.main()
