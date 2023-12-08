# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import io
import os
import random
import shutil
import sys
import tempfile
import unittest
import warnings
from contextlib import redirect_stdout
from pathlib import Path

from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin, InputPlugin, OutputPlugin, ProcPlugin
from pydidas.plugins.plugin_collection import PluginRegistry
from pydidas.plugins.plugin_collection_util_funcs import get_generic_plugin_path
from pydidas.unittest_objects import DummyPluginCollection, create_plugin_class


class TestPluginRegistry(unittest.TestCase):
    def setUp(self):
        self._pluginpath = Path(tempfile.mkdtemp())
        self._otherpaths = []
        self._class_names = []
        self.n_per_type = 8
        self.n_plugin = 3 * self.n_per_type
        self._good_filenames = [Path("test.py"), Path("test_2.py"), Path("test3.py")]
        self._bad_filenames = [
            Path(".test.py"),
            Path("__test.py"),
            Path("test.txt"),
            Path("another_test.pyc"),
            Path("compiled.py~"),
        ]
        self._syspath = copy.copy(sys.path)
        self._qsettings = PydidasQsettings()
        self._qsettings_plugin_path = self._qsettings.value("user/plugin_path")
        self._qsettings.set_value("user/plugin_path", "")

    def tearDown(self):
        DummyPluginCollection().clear_collection(True)
        shutil.rmtree(self._pluginpath)
        for _path in self._otherpaths:
            shutil.rmtree(_path)
        sys.path = self._syspath
        self._qsettings.set_value("user/plugin_path", self._qsettings_plugin_path)

    def create_plugin_file_tree(self, path=None, depth=3, width=2):
        path = self._pluginpath if path is None else path
        _dirs = self.create_dir_tree(path, depth, width)
        self.populate_with_python_files(_dirs)
        _mods = self.get_modules_from_dirs(_dirs, path)
        return _dirs, _mods

    def create_dir_tree(self, path=None, depth=3, width=2):
        _dirs = []
        for _width in range(width):
            _dir = path.joinpath(get_random_string(8))
            _dir.mkdir()
            with open(_dir.joinpath("__init__.py"), "w") as f:
                f.write(" ")
            if depth > 1:
                _dirs += self.create_dir_tree(_dir, width=width, depth=depth - 1)
            else:
                _dirs += [_dir]
        return _dirs

    def populate_with_python_files(self, dirs):
        if isinstance(dirs, Path):
            dirs = [dirs]
        for _dir in dirs:
            for _name in self._good_filenames:
                with open(_dir.joinpath(_name), "w") as f:
                    f.write(self.get_random_class_def(store_name=True))
            for _name in self._bad_filenames:
                with open(_dir.joinpath(_name), "w") as f:
                    f.write(self.get_random_class_def())

    def get_random_class_def(self, store_name=False):
        _plugin = random.choice(["InputPlugin", "ProcPlugin", "OutputPlugin"])
        _name = get_random_string(11)
        _str = (
            "from pydidas.plugins import BasePlugin, InputPlugin, "
            "ProcPlugin, OutputPlugin\n"
            f"\nclass {_name.upper()}({_plugin}):"
            "\n    basic_plugin = False"
            f'\n    plugin_name = "{_name}"'
            "\n\n    def __init__(self, **kwargs: dict):"
            "\n        super().__init__(**kwargs)"
            f"\n\nclass {get_random_string(11)}:"
            "\n    ..."
        )
        if store_name:
            self._class_names.append(_name.upper())
        return _str

    def get_modules_from_dirs(self, dirs, root=None):
        root = self._pluginpath if root is None else root
        _mods = []
        _names = [_name.stem for _name in self._good_filenames]
        for _dir in dirs:
            _new_module = ".".join(_dir.relative_to(root).parts)
            for _name in _names:
                _mods.append(f"{_new_module}.{_name}".strip("."))
        return set(_mods)

    def test_init__empty(self):
        PC = DummyPluginCollection(n_plugins=0, plugin_path="", test_mode=True)
        self.assertIsInstance(PC, PluginRegistry)
        self.assertEqual(len(PC.get_all_plugins()), 0)

    def test_init__empty_path(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self.assertIsInstance(PC, PluginRegistry)
        self.assertEqual(len(PC.get_all_plugins()), 0)

    def test_init__wrong_path(self):
        PC = DummyPluginCollection(
            n_plugins=0,
            plugin_path=self._pluginpath.joinpath("no_such_path"),
            test_mode=True,
        )
        self.assertIsInstance(PC, PluginRegistry)
        self.assertEqual(len(PC.get_all_plugins()), 0)

    def test_clear_collection__no_confirmation(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        with io.StringIO() as buf, redirect_stdout(buf):
            PC.clear_collection()
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_clear_collection__with_confirmation(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        PC.clear_collection(True)
        self.assertEqual(PC.plugins, {})
        self.assertEqual(PC._PluginRegistry__plugin_types, {})
        self.assertEqual(PC._PluginRegistry__plugin_names, {})

    def test_registered_paths(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _paths = PC.registered_paths
        self.assertEqual(_paths, [Path(self._pluginpath)])

    def test_get_all_plugins_of_type__base(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _plugins = PC.get_all_plugins_of_type("base")
        self.assertTrue(len(_plugins) >= 4)

    def test_get_all_plugins_of_type__input(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _plugins = PC.get_all_plugins_of_type("input")
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(issubclass(_plugin, InputPlugin))

    def test_get_all_plugins_of_type__proc(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _plugins = PC.get_all_plugins_of_type("proc")
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(issubclass(_plugin, ProcPlugin))

    def test_get_all_plugins_of_type__output(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _plugins = PC.get_all_plugins_of_type("output")
        self.assertEqual(len(_plugins), self.n_per_type)
        for _plugin in _plugins:
            self.assertTrue(issubclass(_plugin, OutputPlugin))

    def test_get_all_plugins(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_get_plugin_by_name__no_name(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = get_random_string(12)
        with self.assertRaises(KeyError):
            PC.get_plugin_by_name(_name)

    def test_get_plugin_by_name__known_name(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = list(PC.plugins.keys())[0]
        _plugin = PC.get_plugin_by_name(_name)
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_plugin_by_name__base_plugin(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        PC.verify_is_initialized()
        _plugin = PC.get_plugin_by_name("BasePlugin")
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_all_plugin_names(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _names = PC.get_all_plugin_names()
        self.assertEqual(len(_names), self.n_plugin)
        for _name in _names:
            self.assertIsInstance(_name, str)

    def test_get_plugin_by_plugin_name__known_name(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = list(PC._PluginRegistry__plugin_names.keys())[0]
        _plugin = PC.get_plugin_by_plugin_name(_name)
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_plugin_by_plugin_name__no_name(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = get_random_string(12)
        with self.assertRaises(KeyError):
            PC.get_plugin_by_plugin_name(_name)

    def test_remove_plugin_from_collection__new_items(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC._PluginRegistry__remove_plugin_from_collection(_new_cls)
        self.assertEqual(len(PC.plugins), self.n_plugin)

    def test_remove_plugin_from_collection__existing_item(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = PC.get_all_plugin_names()[0]
        PC._PluginRegistry__remove_plugin_from_collection(PC.plugins[_name])
        self.assertFalse(_name in PC.plugins)

    def test_add_new_class(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC._PluginRegistry__add_new_class(_new_cls)
        self.assertTrue(_new_cls.__name__ in PC.plugins)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_add_new_class__duplicate_plugin_name(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2 = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2.plugin_name = _new_cls.plugin_name
        PC._PluginRegistry__add_new_class(_new_cls)
        with self.assertRaises(KeyError):
            PC._PluginRegistry__add_new_class(_new_cls2)

    def test_check_and_register_class__new_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC._PluginRegistry__check_and_register_class(_new_cls)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__wrong_class(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _name = get_random_string(12)
        PC._PluginRegistry__check_and_register_class(float)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)
        self.assertFalse(_name in PC.get_all_plugin_names())

    def test_check_and_register_class__new_class_with_same_name_no_reload(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2 = create_plugin_class(0, number=self.n_plugin + 2)
        _new_cls2.__name__ = _new_cls.__name__
        PC._PluginRegistry__check_and_register_class(_new_cls)
        PC._PluginRegistry__check_and_register_class(_new_cls2)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__new_class_with_same_name_reload(self):
        self.n_plugin = 2
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2 = create_plugin_class(0, number=self.n_plugin + 2)
        _new_cls2.__name__ = _new_cls.__name__
        _new_cls2.plugin_name = _new_cls.plugin_name
        PC._PluginRegistry__check_and_register_class(_new_cls)
        PC._PluginRegistry__check_and_register_class(_new_cls2, reload=True)
        self.assertEqual(PC.plugins[_new_cls2.__name__], _new_cls2)

    def test_import_module_and_get_classes_in_module(self):
        _dirs, _mods = self.create_plugin_file_tree(width=1, depth=1)
        _fname = os.path.join(_dirs[0], self._good_filenames[0])
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _members = PC._PluginRegistry__get_classes_in_module("some other name", _fname)
        _classes = [_cls for _name, _cls in _members]
        for _cls in [InputPlugin, ProcPlugin, OutputPlugin]:
            self.assertIn(_cls, _classes)

    def test_get_valid_modules_and_filenames__simple_path(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        self.populate_with_python_files(self._pluginpath)
        _modules = set(PC._get_valid_modules_and_filenames(self._pluginpath).keys())
        _target = self.get_modules_from_dirs([self._pluginpath])
        self.assertEqual(_modules, _target)

    def test_get_valid_modules_and_filenames__path_tree(self):
        PC = DummyPluginCollection(
            n_plugins=self.n_plugin, plugin_path=self._pluginpath
        )
        _dirs, _mods = self.create_plugin_file_tree()
        _modules = set(PC._get_valid_modules_and_filenames(self._pluginpath).keys())
        _target = self.get_modules_from_dirs(_dirs)
        self.assertEqual(_modules, _target)

    def test_store_plugin_path__no_path(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.verify_is_initialized()
        _path = self._pluginpath.joinpath(get_random_string(8))
        PC._store_plugin_path(_path)
        _qplugin_path = Path(self._qsettings.value("user/plugin_path"))
        self.assertEqual(_qplugin_path, self._pluginpath)
        self.assertNotIn(_path, sys.path)

    def test_store_plugin_path__existing_paths(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.verify_is_initialized()
        for _ in range(3):
            self._otherpaths.append(Path(tempfile.mkdtemp()))
            _path = self._otherpaths[-1]
            PC._store_plugin_path(_path)
        _paths = [self._pluginpath] + self._otherpaths
        _qplugin_path = self._qsettings.value("user/plugin_path")
        self.assertEqual(_qplugin_path, ";;".join(str(p) for p in _paths))
        for _path in self._otherpaths:
            self.assertIn(_path, PC._PluginRegistry__plugin_paths)

    def test_find_and_register_plugins_in_path__path_does_not_exist(self):
        _path = self._pluginpath.joinpath(get_random_string(8))
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.clear_collection(True)
        PC._find_and_register_plugins_in_path(_path)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__path_empty(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.clear_collection(True)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__single_file(self):
        PC = DummyPluginCollection(n_plugins=0)
        PC.clear_collection(True)
        _dirs, _mods = self.create_plugin_file_tree(depth=1, width=1)
        _fname = _dirs[0].joinpath(self._good_filenames[0])
        PC._find_and_register_plugins_in_path(_fname)
        self.assertEqual(len(PC.plugins), 1)

    def test_find_and_register_plugins_in_path__populated(self):
        self.populate_with_python_files(self._pluginpath)
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.clear_collection(True)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), len(self._good_filenames))

    def test_find_and_register_plugins_in_path__w_pathlib_Path(self):
        self.populate_with_python_files(self._pluginpath)
        PC = DummyPluginCollection(n_plugins=0, plugin_path=Path(self._pluginpath))
        PC.clear_collection(True)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), len(self._good_filenames))

    def test_find_and_register_plugins__single_path(self):
        _dirs, _mods = self.create_plugin_file_tree()
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.clear_collection(True)
        PC.find_and_register_plugins(self._pluginpath)
        self.assertEqual(len(_mods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_find_and_register_plugins__multiple_paths(self):
        _dirs, _mods = self.create_plugin_file_tree()
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        _dirs2, _mods2 = self.create_plugin_file_tree(self._otherpaths[0])
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        PC.clear_collection(True)
        PC.find_and_register_plugins(self._pluginpath, self._otherpaths[0])
        _newmods = _mods | _mods2
        self.assertEqual(len(_newmods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_find_and_register_plugins__multiple_paths_w_pathlib_Path(self):
        _dirs, _mods = self.create_plugin_file_tree()
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        _dirs2, _mods2 = self.create_plugin_file_tree(self._otherpaths[0])
        PC = DummyPluginCollection(n_plugins=0, plugin_path=Path(self._pluginpath))
        PC.clear_collection(True)
        PC.find_and_register_plugins(Path(self._pluginpath), Path(self._otherpaths[0]))
        _newmods = _mods | _mods2
        self.assertEqual(len(_newmods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_get_q_settings_plugin_paths__no_path_set(self):
        self._qsettings.set_value("user/plugin_path", None)
        PC = DummyPluginCollection(n_plugins=0, test_mode=True)
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual(_qplugin_path, [None])

    def test_get_q_settings_plugin_paths__single_path(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", str(self._pluginpath))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual([self._pluginpath], _qplugin_path)

    def test_get_q_settings_plugin_paths__multiple_paths(self):
        _paths = [
            self._pluginpath.joinpath("test1"),
            self._pluginpath.joinpath("some/other/path"),
            self._pluginpath.joinpath("test_23.456"),
        ]
        for _path in _paths:
            os.makedirs(_path)
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", ";;".join(str(p) for p in _paths))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual(_paths, _qplugin_path)

    def test_get_q_settings_plugin_paths__multiple_nonexistent_paths(self):
        _paths = [
            self._pluginpath.joinpath("test1"),
            self._pluginpath.joinpath("some/other/path"),
            self._pluginpath.joinpath("test_23.456"),
        ]
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", ";;".join(str(p) for p in _paths))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual([], _qplugin_path)
        self.assertEqual(self._qsettings.value("user/plugin_path"), "")

    def test_get_generic_plugin_path__no_q_path(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", None)
        _path = PC._PluginRegistry__get_generic_plugin_paths()
        self.assertEqual(_path, get_generic_plugin_path())

    def test_get_generic_plugin_path__empty_q_path(self):
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", "")
        _path = PC._PluginRegistry__get_generic_plugin_paths()
        self.assertEqual(_path, get_generic_plugin_path())

    def test_get_generic_plugin_path__q_path_nonexistent(self):
        _path = Path("some/path/to/nowhere")
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", str(_path))
        _newpath = PC._PluginRegistry__get_generic_plugin_paths()
        self.assertEqual([], _newpath)

    def test_get_generic_plugin_path__q_path_existent(self):
        _path = self._pluginpath.joinpath("some/path/to/nowhere")
        os.makedirs(_path)
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._qsettings.set_value("user/plugin_path", str(_path))
        _newpath = PC._PluginRegistry__get_generic_plugin_paths()
        self.assertEqual([_path], _newpath)

    def test_get_plugin_path_from_kwargs__no_plugin_path(self):
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False)
        _path = PC._PluginRegistry__get_plugin_path_from_kwargs(**kwargs)
        self.assertIsNone(_path)

    def test_get_plugin_path_from_kwargs__single_str(self):
        _entry = Path("  some string ")
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entry)
        _path = PC._PluginRegistry__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, [_entry])

    def test_get_plugin_path_from_kwargs__multi_str(self):
        _entries = [
            Path("something"),
            Path("another_string"),
            Path("this/is/not/a/directory"),
            Path("this:string:has#special chars"),
        ]

        _entry = ";;".join(
            [
                (
                    random.choice(["", " ", "   ", "    "])
                    + str(item)
                    + random.choice(["", " ", "   ", "    "])
                )
                for item in _entries
            ]
        )
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entry)
        _path = PC._PluginRegistry__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, _entries)

    def test_get_plugin_path_from_kwargs__list(self):
        _entries = [
            "something",
            "another_string",
            "this/is/not/a/directory",
            "this:string:has#special chars",
        ]
        PC = DummyPluginCollection(n_plugins=0)
        kwargs = dict(some_entry=12, something=False, plugin_path=_entries)
        _path = PC._PluginRegistry__get_plugin_path_from_kwargs(**kwargs)
        self.assertEqual(_path, _entries)

    def test_unregister_plugin_path(self):
        self.create_plugin_file_tree()
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        # add two paths after initialization
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        _new_path = self._otherpaths[0]
        _new_path2 = self._otherpaths[1]
        _, _ = self.create_plugin_file_tree(path=_new_path, width=2, depth=2)
        PC.find_and_register_plugins(_new_path)
        _new_class_names = tuple(self._class_names)
        _, _ = self.create_plugin_file_tree(path=_new_path2, width=2, depth=2)
        PC.find_and_register_plugins(_new_path2)
        self.assertEqual(set(self._class_names), set(PC.get_all_plugin_names()))
        PC.unregister_plugin_path(_new_path2)
        self.assertEqual(set(_new_class_names), set(PC.get_all_plugin_names()))
        self.assertEqual(set(PC.registered_paths), set((self._pluginpath, _new_path)))
        self.assertNotIn(_new_path2, PC.get_q_settings_plugin_paths())

    def test_unregister_plugin_path__wrong_path(self):
        self.create_plugin_file_tree()
        PC = DummyPluginCollection(
            n_plugins=0, plugin_path=self._pluginpath, test_mode=True
        )
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        with self.assertRaises(UserConfigError):
            PC.unregister_plugin_path(self._otherpaths[0])

    def test__wrong_path_in_qsettings(self):
        _path = self._pluginpath.joinpath(get_random_string(8))
        self._qsettings.set_value("user/plugin_path", str(_path))
        PC = DummyPluginCollection(n_plugins=0)
        self.assertNotIn(_path, PC.registered_paths)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.main()
