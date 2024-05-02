# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
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
from pydidas.plugins import (
    BaseFitPlugin,
    BasePlugin,
    InputPlugin,
    OutputPlugin,
    ProcPlugin,
)
from pydidas.plugins.plugin_registry import PluginRegistry
from pydidas.unittest_objects import create_plugin_class


class TestPluginRegistry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._dummy_path = Path(tempfile.mkdtemp())
        cls.n_per_type = 8
        cls.n_plugin = 3 * cls.n_per_type
        cls._good_filenames = [Path("test.py"), Path("test_2.py"), Path("test3.py")]
        cls._bad_filenames = [
            Path(".test.py"),
            Path("__test.py"),
            Path("test.txt"),
            Path("another_test.pyc"),
            Path("compiled.py~"),
        ]
        cls._syspath = copy.copy(sys.path)
        cls._qsettings = PydidasQsettings()
        cls._qsettings_plugin_path = cls._qsettings.value("user/plugin_path")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._dummy_path)
        cls._qsettings.set_value("user/plugin_path", cls._qsettings_plugin_path)
        sys.path = cls._syspath

    def setUp(self):
        self._pluginpath = Path(tempfile.mkdtemp())
        self._otherpaths = []
        self._class_names = []
        self._qsettings.set_value("user/plugin_path", "")

    def tearDown(self):
        shutil.rmtree(self._pluginpath)
        for _path in self._otherpaths:
            shutil.rmtree(_path)

    def get_registry_with_random_plugins(self):
        PC = PluginRegistry(use_generic_plugins=False)
        for num in range(self.n_plugin):
            _class = create_plugin_class(num % 3, number=num // 3)
            PC.check_and_register_class(_class)
        for _base in [BasePlugin, BaseFitPlugin, InputPlugin, OutputPlugin, ProcPlugin]:
            PC.check_and_register_class(_base)
        return PC

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

    def test_init__w_generic_plugins(self):
        for _generic in [True, False]:
            with self.subTest(_generic=_generic):
                PC = PluginRegistry(use_generic_plugins=_generic)
                self.assertIsInstance(PC, PluginRegistry)
                self.assertEqual(PC._config["use_generic_plugins"], _generic)
                self.assertEqual(len(PC.plugins), 0)

    def test_init__w_plugin_paths(self):
        for _path, _target in [
            [None, []],
            ["a_path", []],
            ["first_path;;second_path", []],
            [Path("path"), []],
            [str(self._pluginpath), [self._pluginpath]],
            [
                ";;".join((str(self._pluginpath), str(self._dummy_path))),
                [self._pluginpath, self._dummy_path],
            ],
            [self._pluginpath, [self._pluginpath]],
            [
                [self._pluginpath, self._dummy_path],
                [self._pluginpath, self._dummy_path],
            ],
            [
                [str(self._pluginpath), str(self._dummy_path)],
                [self._pluginpath, self._dummy_path],
            ],
            [
                [self._pluginpath, self._dummy_path.joinpath("dummy")],
                [self._pluginpath],
            ],
        ]:
            with self.subTest(_path=_path):
                PC = PluginRegistry(plugin_path=_path)
                self.assertIsInstance(PC, PluginRegistry)
                self.assertEqual(PC._config["initial_plugin_path"], _target)

    def test_init__w_forced_init(self):
        PC = PluginRegistry(force_initialization=True)
        self.assertIsInstance(PC, PluginRegistry)
        self.assertTrue(len(PC.plugins) > 0)

    def test_clear_collection__no_confirmation(self):
        PC = PluginRegistry(force_initialization=True)
        with io.StringIO() as buf, redirect_stdout(buf):
            PC.clear_collection()
        self.assertTrue(len(PC.plugins) > 0)

    def test_clear_collection__with_confirmation(self):
        PC = PluginRegistry()
        PC.clear_collection(True)
        for _key in ["plugins", "_plugin_types", "_plugin_names"]:
            self.assertEqual(getattr(PC, _key), {})

    def test_registered_paths(self):
        PC = PluginRegistry(plugin_path=self._pluginpath)
        _paths = PC.registered_paths
        self.assertEqual(_paths, [Path(self._pluginpath)])

    def test_get_all_plugins_of_type__base(self):
        PC = PluginRegistry(plugin_path=self._pluginpath)
        _plugins = PC.get_all_plugins_of_type("base")
        self.assertTrue(len(_plugins) >= 4)

    def test_get_all_plugins_of_type__input(self):
        PC = self.get_registry_with_random_plugins()
        for _type, _base in [
            ["input", InputPlugin],
            ["proc", ProcPlugin],
            ["output", OutputPlugin],
        ]:
            with self.subTest(_type=_type):
                _plugins = PC.get_all_plugins_of_type(_type)
                self.assertEqual(len(_plugins), self.n_per_type)
                for _plugin in _plugins:
                    self.assertTrue(issubclass(_plugin, _base))

    def test_get_all_plugins(self):
        PC = self.get_registry_with_random_plugins()
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_get_plugin_by_name__no_name(self):
        PC = PluginRegistry(plugin_path=self._pluginpath)
        _name = get_random_string(16)
        with self.assertRaises(KeyError):
            PC.get_plugin_by_name(_name)

    def test_get_plugin_by_name__known_name(self):
        PC = self.get_registry_with_random_plugins()
        _name = list(PC.plugins.keys())[0]
        _plugin = PC.get_plugin_by_name(_name)
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_plugin_by_name__base_plugin(self):
        PC = self.get_registry_with_random_plugins()
        _plugin = PC.get_plugin_by_name("BasePlugin")
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_all_plugin_names(self):
        PC = self.get_registry_with_random_plugins()
        _names = PC.get_all_plugin_names()
        self.assertEqual(len(_names), self.n_plugin)
        for _name in _names:
            self.assertIsInstance(_name, str)

    def test_get_plugin_by_plugin_name__known_name(self):
        PC = self.get_registry_with_random_plugins()
        _name = list(PC._plugin_names.keys())[0]
        _plugin = PC.get_plugin_by_plugin_name(_name)
        self.assertTrue(issubclass(_plugin, BasePlugin))

    def test_get_plugin_by_plugin_name__no_name(self):
        PC = self.get_registry_with_random_plugins()
        with self.assertRaises(KeyError):
            PC.get_plugin_by_plugin_name(get_random_string(16))

    def test_remove_plugin_from_collection__new_items(self):
        PC = self.get_registry_with_random_plugins()
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC.remove_plugin_from_collection(_new_cls)
        self.assertEqual(len(PC.plugins), self.n_plugin)

    def test_remove_plugin_from_collection__existing_item(self):
        PC = self.get_registry_with_random_plugins()
        _name = PC.get_all_plugin_names()[0]
        PC.remove_plugin_from_collection(PC.plugins[_name])
        self.assertNotIn(_name, PC.plugins)

    def test_add_new_class(self):
        PC = self.get_registry_with_random_plugins()
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC._PluginRegistry__add_new_class(_new_cls)
        self.assertTrue(_new_cls.__name__ in PC.plugins)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_add_new_class__duplicate_plugin_name(self):
        PC = self.get_registry_with_random_plugins()
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2 = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2.plugin_name = _new_cls.plugin_name
        PC._PluginRegistry__add_new_class(_new_cls)
        with self.assertRaises(KeyError):
            PC._PluginRegistry__add_new_class(_new_cls2)

    def test_check_and_register_class__new_class(self):
        self.n_plugin = 2
        PC = self.get_registry_with_random_plugins()
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        PC.check_and_register_class(_new_cls)
        self.assertEqual(PC.plugins[_new_cls.__name__], _new_cls)

    def test_check_and_register_class__wrong_class(self):
        self.n_plugin = 2
        PC = self.get_registry_with_random_plugins()
        PC.check_and_register_class(float)
        self.assertEqual(len(PC.get_all_plugins()), self.n_plugin)

    def test_check_and_register_class__new_class_with_same_name(self):
        self.n_plugin = 2
        _new_cls = create_plugin_class(0, number=self.n_plugin + 1)
        _new_cls2 = create_plugin_class(0, number=self.n_plugin + 2)
        _new_cls2.__name__ = _new_cls.__name__
        _new_cls2.plugin_name = _new_cls.plugin_name
        for _reload in [True, False]:
            PC = self.get_registry_with_random_plugins()
            with self.subTest(_reload=_reload):
                PC.check_and_register_class(_new_cls)
                PC.check_and_register_class(_new_cls2, reload=_reload)
                self.assertEqual(
                    PC.plugins[_new_cls.__name__], _new_cls2 if _reload else _new_cls
                )

    def test_import_module_and_get_classes_in_module(self):
        _dirs, _mods = self.create_plugin_file_tree(width=1, depth=1)
        _fname = os.path.join(_dirs[0], self._good_filenames[0])
        PC = self.get_registry_with_random_plugins()
        _members = PC._PluginRegistry__get_classes_in_module("some other name", _fname)
        _classes = [_cls for _name, _cls in _members]
        for _cls in [InputPlugin, ProcPlugin, OutputPlugin]:
            self.assertIn(_cls, _classes)

    def test_get_valid_modules_and_filenames__simple_path(self):
        PC = PluginRegistry(plugin_path=self._pluginpath)
        self.populate_with_python_files(self._pluginpath)
        _modules = set(PC._get_valid_modules_and_filenames(self._pluginpath).keys())
        _target = self.get_modules_from_dirs([self._pluginpath])
        self.assertEqual(_modules, _target)

    def test_get_valid_modules_and_filenames__path_tree(self):
        PC = PluginRegistry(plugin_path=self._pluginpath)
        _dirs, _mods = self.create_plugin_file_tree()
        _modules = set(PC._get_valid_modules_and_filenames(self._pluginpath).keys())
        _target = self.get_modules_from_dirs(_dirs)
        self.assertEqual(_modules, _target)

    def test_store_plugin_path__no_path(self):
        PC = PluginRegistry(
            use_generic_plugins=False,
            force_initialization=True,
        )
        _path = self._pluginpath.joinpath(get_random_string(8))
        PC._store_plugin_path(_path)
        _qplugin_path = self._qsettings.value("user/plugin_path")
        self.assertEqual(_qplugin_path, "")
        self.assertNotIn(_path, PC._plugin_paths)

    def test_store_plugin_path__existing_paths(self):
        PC = PluginRegistry(
            plugin_path=self._pluginpath,
            use_generic_plugins=False,
            force_initialization=True,
        )
        for _ in range(3):
            _new_path = Path(tempfile.mkdtemp())
            self._otherpaths.append(_new_path)
            PC._store_plugin_path(_new_path)
        _paths = [self._pluginpath] + self._otherpaths
        _qplugin_path = self._qsettings.value("user/plugin_path")
        self.assertEqual(_qplugin_path, ";;".join(str(p) for p in _paths))
        for _path in self._otherpaths:
            self.assertIn(_path, PC._plugin_paths)

    def test_find_and_register_plugins_in_path__path_does_not_exist(self):
        _path = self._pluginpath.joinpath(get_random_string(8))
        PC = PluginRegistry(use_generic_plugins=False)
        PC._find_and_register_plugins_in_path(_path)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__path_empty(self):
        PC = PluginRegistry(use_generic_plugins=False)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), 0)

    def test_find_and_register_plugins_in_path__single_file(self):
        PC = PluginRegistry()
        _dirs, _mods = self.create_plugin_file_tree(depth=1, width=1)
        _fname = _dirs[0].joinpath(self._good_filenames[0])
        PC._find_and_register_plugins_in_path(_fname)
        self.assertEqual(len(PC.plugins), 1)

    def test_find_and_register_plugins_in_path__populated(self):
        self.populate_with_python_files(self._pluginpath)
        PC = PluginRegistry(use_generic_plugins=False)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), len(self._good_filenames))

    def test_find_and_register_plugins_in_path__w_pathlib_Path(self):
        self.populate_with_python_files(self._pluginpath)
        PC = PluginRegistry(plugin_path=Path(self._pluginpath))
        PC.clear_collection(True)
        PC._find_and_register_plugins_in_path(self._pluginpath)
        self.assertEqual(len(PC.plugins), len(self._good_filenames))

    def test_find_and_register_plugins__single_path(self):
        _dirs, _mods = self.create_plugin_file_tree()
        PC = PluginRegistry(use_generic_plugins=False)
        self.assertEqual(len(PC.plugins), 0)
        PC.find_and_register_plugins(self._pluginpath)
        self.assertEqual(len(_mods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_find_and_register_plugins__multiple_paths(self):
        _dirs, _mods = self.create_plugin_file_tree()
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        _dirs2, _mods2 = self.create_plugin_file_tree(self._otherpaths[0])
        PC = PluginRegistry(use_generic_plugins=False)
        PC.find_and_register_plugins(self._pluginpath, self._otherpaths[0])
        _newmods = _mods | _mods2
        self.assertEqual(len(_newmods), len(PC.plugins))
        self.assertEqual(set(PC.plugins.keys()), set(self._class_names))

    def test_get_q_settings_plugin_paths__no_path_set(self):
        self._qsettings.set_value("user/plugin_path", None)
        PC = PluginRegistry(use_generic_plugins=False)
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual(_qplugin_path, [])

    def test_get_q_settings_plugin_paths__single_path(self):
        PC = PluginRegistry(use_generic_plugins=False)
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
        PC = PluginRegistry()
        self._qsettings.set_value("user/plugin_path", ";;".join(str(p) for p in _paths))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual(_paths, _qplugin_path)

    def test_get_q_settings_plugin_paths__multiple_nonexistent_paths(self):
        _paths = [
            self._pluginpath.joinpath("test1"),
            self._pluginpath.joinpath("some/other/path"),
            self._pluginpath.joinpath("test_23.456"),
        ]
        PC = PluginRegistry()
        self._qsettings.set_value("user/plugin_path", ";;".join(str(p) for p in _paths))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual([], _qplugin_path)
        self.assertEqual(self._qsettings.value("user/plugin_path"), "")

    def test_get_q_settings_plugin_paths__mixed_existing_paths(self):
        _paths = [
            self._pluginpath.joinpath("test1"),
            self._pluginpath,
            self._pluginpath.joinpath("test_23.456"),
            self._dummy_path,
        ]
        PC = PluginRegistry()
        self._qsettings.set_value("user/plugin_path", ";;".join(str(p) for p in _paths))
        _qplugin_path = PC.get_q_settings_plugin_paths()
        self.assertEqual(_qplugin_path, [self._pluginpath, self._dummy_path])
        self.assertEqual(
            self._qsettings.value("user/plugin_path"),
            ";;".join(str(p) for p in [self._pluginpath, self._dummy_path]),
        )

    def test_get_user_plugin_path__w_plugin_path(self):
        PC = PluginRegistry(plugin_path=self._dummy_path)
        _path = PC._get_user_plugin_paths()
        self.assertEqual(_path, [self._dummy_path])

    def test_get_user_plugin_path__no_pp_no_q_path(self):
        PC = PluginRegistry()
        for _val in [None, ""]:
            with self.subTest(_val=_val):
                self._qsettings.set_value("user/plugin_path", _val)
                _path = PC._get_user_plugin_paths()
                self.assertEqual(_path, [])

    def test_get_user_plugin_path__no_pp_q_path_nonexistent(self):
        _path = Path("some/path/to/nowhere")
        PC = PluginRegistry()
        self._qsettings.set_value("user/plugin_path", str(_path))
        _newpath = PC._get_user_plugin_paths()
        self.assertEqual(_newpath, [])

    def test_get_user_plugin_path__no_pp_q_path_existent(self):
        _path = self._pluginpath.joinpath("some/path/to/somewhere")
        os.makedirs(_path)
        PC = PluginRegistry()
        self._qsettings.set_value("user/plugin_path", str(_path))
        _newpath = PC._get_user_plugin_paths()
        self.assertEqual(_newpath, [_path])

    def test_unregister_plugin_path(self):
        self.create_plugin_file_tree()
        PC = PluginRegistry(
            use_generic_plugins=False,
            plugin_path=self._pluginpath,
            force_initialization=True,
        )
        # add two paths after initialization
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        _new_path, _new_path2 = self._otherpaths
        _, _ = self.create_plugin_file_tree(path=_new_path, width=2, depth=2)
        PC.find_and_register_plugins(_new_path)
        _new_class_names = tuple(self._class_names)
        _, _ = self.create_plugin_file_tree(path=_new_path2, width=2, depth=2)
        PC.find_and_register_plugins(_new_path2)
        _qpaths = self._qsettings.q_settings_get("user/plugin_path")
        for _path in [self._pluginpath] + self._otherpaths:
            self.assertIn(str(_path), _qpaths)
        self.assertEqual(set(self._class_names), set(PC.get_all_plugin_names()))
        PC.unregister_plugin_path(_new_path2)
        _qpaths = self._qsettings.q_settings_get("user/plugin_path")
        for _path in [self._pluginpath, _new_path]:
            self.assertIn(str(_path), _qpaths)
        self.assertNotIn(str(_new_path2), _qpaths)
        self.assertEqual(set(_new_class_names), set(PC.get_all_plugin_names()))
        self.assertEqual(PC.registered_paths, [self._pluginpath, _new_path])
        self.assertNotIn(_new_path2, PC.get_q_settings_plugin_paths())

    def test_unregister_plugin_path__wrong_path(self):
        self.create_plugin_file_tree()
        PC = PluginRegistry(plugin_path=self._pluginpath, use_generic_plugins=False)
        self._otherpaths.append(Path(tempfile.mkdtemp()))
        with self.assertRaises(UserConfigError):
            PC.unregister_plugin_path(self._otherpaths[0])

    def test_unregister_all_paths(self):
        for _ in range(3):
            _new_path = Path(tempfile.mkdtemp())
            self._otherpaths.append(_new_path)
            _, _ = self.create_plugin_file_tree(path=_new_path, width=2, depth=2)
        PC = PluginRegistry(
            use_generic_plugins=False,
            plugin_path=self._otherpaths,
            force_initialization=True,
        )
        for _path in self._otherpaths:
            self.assertIn(_path, PC.registered_paths)
        PC.unregister_all_paths(True)
        self.assertEqual(PC.registered_paths, [])

    def test__wrong_path_in_qsettings(self):
        _path = self._pluginpath.joinpath(get_random_string(8))
        self._qsettings.set_value("user/plugin_path", str(_path))
        PC = PluginRegistry(force_initialization=True, use_generic_plugins=False)
        self.assertNotIn(_path, PC.registered_paths)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        unittest.main()
