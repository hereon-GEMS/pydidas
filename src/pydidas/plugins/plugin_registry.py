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
The PluginRegistry class stores Plugin information and allows to get the classes.

The PluginRegistry allows to handle paths and search these paths for pydidas
Plugins and keep a registry of all the class objects for the user to access.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import importlib
import inspect
import warnings
from pathlib import Path
from typing import Literal, Union

from qtpy import QtCore

from pydidas.core import PydidasQsettingsMixin, UserConfigError
from pydidas.core.constants import GENERIC_PLUGIN_PATH
from pydidas.core.utils import find_valid_python_files
from pydidas.plugins import BasePlugin


class PluginRegistry(QtCore.QObject, PydidasQsettingsMixin):
    """
    Class to hold references of plugins.

    Plugins can be accessed by their class names or by their plugin_name properties.
    For details, please refer to the individual methods.

    Note that the PluginRegistry is a class which should not normally be
    accessed directly but generally through its 'PluginCollection' singleton.

    Parameters
    ----------
    **kwargs : dict
        Supported kwargs are:

        plugin_path : Union[str, list[Path], None], optional
            The search directory for plugins. A single path can be supplies
            as string. Multiple paths can be supplied in a single string
            separated by ";;" or as a list. None will call to the default
            paths. The default is None.
        force_initialization : bool, optional
            Keyword to force initialization at creation. By default, the
            PluginCollection is initialized the first time it is used.
            The default is False.
    """

    sig_updated_plugins = QtCore.Signal()

    def __init__(self, **kwargs: dict):
        QtCore.QObject.__init__(self)
        PydidasQsettingsMixin.__init__(self)
        self.plugins = {}
        self._plugin_types = {}
        self._plugin_names = {}
        self._plugin_basic_types = {}
        self._plugin_paths = []
        self._config = {
            "initial_plugin_path": self.__get_plugin_path_from_kwargs(**kwargs),
            "initialized": False,
            "must_emit_signal": False,
            "use_generic_plugins": kwargs.get("use_generic_plugins", True),
        }
        if kwargs.get("force_initialization", False):
            self.verify_is_initialized()

    @staticmethod
    def __get_plugin_path_from_kwargs(**kwargs: dict) -> list[Path]:
        """
        Get the plugin path(s) from the calling keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            The calling keyword arguments

        Returns
        -------
        _path : list[Path]
            The plugin paths. If None, no paths have been specified.
        """
        _path = kwargs.get("plugin_path", None)
        if _path is None:
            return []
        if isinstance(_path, str):
            _path = [Path(item.strip()) for item in _path.split(";;") if item != ""]
        if isinstance(_path, Path):
            _path = [_path]
        if isinstance(_path, (list, set, tuple)):
            _path = [Path(_p) for _p in _path]
        _existing_paths = [_p for _p in _path if _p.is_dir()]
        if len(_existing_paths) < len(_path):
            warnings.warn(
                "Non-existent paths were found in the stored Plugin paths and have "
                "been removed. Please check the pydidas plugin paths."
            )
        return _existing_paths

    def verify_is_initialized(self):
        """
        Verify that the instance is initialized.

        During initialization, the PluginCollection processes all specified
        paths.

        This method is called internally in every public method to make sure
        that the PluginCollection is always initialized before any user
        interaction occurs.
        """
        if self._config["initialized"]:
            return
        if self._config["use_generic_plugins"]:
            self.find_and_register_plugins(GENERIC_PLUGIN_PATH)
            for _cls in BasePlugin.base_classes:
                self.check_and_register_class(_cls)
        self.find_and_register_plugins(*self._get_user_plugin_paths())
        self._config["initialized"] = True
        if self._config["must_emit_signal"]:
            self.sig_updated_plugins.emit()

    def _get_user_plugin_paths(self) -> list[Path]:
        """
        Get the user-set plugin paths.

        The user-set paths can either be specified during initialization
        (with the `plugin_path` keyword) or they are loaded from the QSettings.

        Returns
        -------
        plugin_paths : list
            A list of plugin paths.
        """
        if self._config["initial_plugin_path"]:
            _paths = self._config["initial_plugin_path"]
        else:
            _paths = self.get_q_settings_plugin_paths()
        for _path_to_check in [Path(), GENERIC_PLUGIN_PATH]:
            if _path_to_check in _paths:
                _paths.remove(_path_to_check)
        return _paths

    def get_q_settings_plugin_paths(self) -> list[Path]:
        """
        Get the plugin path from the global QSettings.

        This method also strips non-existent paths from the list of results.

        Returns
        -------
        list[Path]
            A list with all stored path entries.
        """
        _paths = self.q_settings_get("user/plugin_path")
        if _paths is None:
            return []
        _paths = [Path(_key) for _key in _paths.split(";;")]
        _existing_paths = [_path for _path in _paths if _path.is_dir()]
        if len(_existing_paths) < len(_paths):
            warnings.warn(
                "Non-existent paths were found in the stored Plugin paths and have "
                "been removed. Please check the pydidas plugin paths."
            )
            self.q_settings_set(
                "user/plugin_path", ";;".join(str(_path) for _path in _existing_paths)
            )
        return _existing_paths

    def find_and_register_plugins(
        self, *plugin_paths: tuple[Path], reload: bool = True
    ):
        """
        Find plugins in the given path(s) and register them in the PluginCollection.

        Parameters
        ----------
        plugin_paths : tuple[Path]
            Any number of file system paths.
        reload : bool, optional
            Flag to handle reloading of plugins if a plugin with an identical
            name is encountered. If False, these plugins will be skipped.
        """
        for _path in plugin_paths:
            if not isinstance(_path, Path):
                raise UserConfigError(
                    "Only pathlib.Paths are valid entries for plugin paths!"
                )
            if _path != Path() and _path.is_dir():
                self._find_and_register_plugins_in_path(_path, reload)
        if self._config["initialized"]:
            self.sig_updated_plugins.emit()
        else:
            self._config["must_emit_signal"] = True

    def _find_and_register_plugins_in_path(self, path: Path, reload: bool = True):
        """
        Find the plugin in a specific path.

        Parameters
        ----------
        path : Path
            The file system search path.
        reload : bool, optional
            Flag to handle reloading of plugins if a plugin with an identical
            name is encountered. If False, these plugins will be skipped.
        """
        self._store_plugin_path(path)
        _modules = self._get_valid_modules_and_filenames(path)
        for _modname, _file in _modules.items():
            _class_members = self.__get_classes_in_module(_modname, _file)
            for _name, _cls in _class_members:
                self.check_and_register_class(_cls, reload)

    def _store_plugin_path(self, plugin_path: Path, verbose: bool = False):
        """
        Store the plugin path.

        Parameters
        ----------
        plugin_path : Path
            The plugin path.
        verbose : bool, optional
            Keyword to toggle printed warnings. The default is False
        """
        if plugin_path in self._plugin_paths + [GENERIC_PLUGIN_PATH]:
            if verbose and plugin_path in self._plugin_paths:
                print("Warning. Storing same path again: {str(plugin_path)}")
            return
        if plugin_path.exists():
            self._plugin_paths.append(plugin_path)
        _paths = ";;".join(str(_path) for _path in self._plugin_paths)
        self.q_settings_set("user/plugin_path", _paths)

    @staticmethod
    def _get_valid_modules_and_filenames(path: Union[Path, str]) -> dict[str, Path]:
        """
        Get all module names in a specified path (including subdirectories).

        Parameters
        ----------
        path : Union[str, Path]
            The file system path.

        Returns
        -------
        _modules : dict
            A list with the module names and their relative paths.
        """
        if isinstance(path, str):
            path = Path(path)
        _files = find_valid_python_files(path)
        _dirpath = path if path.is_dir() else path.parent
        _modules = {
            ".".join(_file.relative_to(_dirpath).parts).removesuffix(".py"): _file
            for _file in _files
        }
        return _modules

    @staticmethod
    def __get_classes_in_module(modname: str, filepath: Path) -> list[tuple[str, type]]:
        """
        Import a module from a file and get all class members of the module.

        Parameters
        ----------
        modname : str
            The registration name of the module
        filepath : str
            The full file path of the module.

        Returns
        -------
        cls_members : list[tuple[str, type]]
            A list with class members with entries for each class in the
            form of (name, class).
        """
        spec = importlib.util.spec_from_file_location(modname, filepath)
        tmp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tmp_module)
        cls_members = inspect.getmembers(tmp_module, inspect.isclass)
        del spec, tmp_module
        return cls_members

    def check_and_register_class(self, class_: type, reload: bool = False):
        """
        Check whether a class is a valid plugin and register it.

        Parameters
        ----------
        class_ : type
            The class object.
        reload : bool
            Flag to enable reloading of plugins. If True, new plugins will
            overwrite older stored plugins. The default is False.
        """
        _class_bases = [
            ".".join([_cls.__module__, _cls.__name__])
            for _cls in inspect.getmro(class_)
        ]
        if "pydidas.plugins.base_plugin.BasePlugin" not in _class_bases:
            return
        if class_.is_basic_plugin() is True:
            self._plugin_basic_types[class_.__name__] = class_
            return
        if class_.__name__ not in self.plugins:
            self.__add_new_class(class_)
        elif reload:
            self.remove_plugin_from_collection(class_)
            self.__add_new_class(class_)

    def __add_new_class(self, class_: type):
        """
        Add a new class to the collection.

        Parameters
        ----------
        class_ : type
            The class object.
        """
        if class_.plugin_name in self._plugin_names:
            _old_cls = self._plugin_names[class_.plugin_name]
            _message = (
                "A different class with the same plugin name "
                f"`{class_.plugin_name}` has already been registered. "
                "Adding this class would destroy the consistency of "
                "the PluginCollection: "
                f"Registered class: `{_old_cls}`; New class: `{class_}`"
            )
            raise KeyError(_message)
        self.plugins[class_.__name__] = class_
        self._plugin_types[class_.__name__] = (
            -1 if class_.is_basic_plugin() else class_.plugin_type
        )
        self._plugin_names[class_.plugin_name] = class_.__name__

    def remove_plugin_from_collection(self, class_: type):
        """
        Remove a Plugin from the PluginCollection.

        Parameters
        ----------
        class_ : type
            The class object to be removed.
        """
        if class_.__name__ in self.plugins:
            del self.plugins[class_.__name__]
            del self._plugin_types[class_.__name__]
            del self._plugin_names[class_.plugin_name]

    def get_all_plugin_names(self) -> list[str]:
        """
        Get a list of all the plugin names currently registered.

        Returns
        -------
        names : list
            The list of all the plugin names.
        """
        self.verify_is_initialized()
        return list(self.plugins.keys())

    def get_plugin_by_plugin_name(self, plugin_name: str) -> type:
        """
        Get a plugin by its plugin name.

        Parameters
        ----------
        plugin_name : str
            The plugin_name property of the class.

        Returns
        -------
        plugin : pydidas.plugins.BasePlugin
            The Plugin class.
        """
        self.verify_is_initialized()
        if plugin_name in self._plugin_names:
            return self.plugins[self._plugin_names[plugin_name]]
        raise KeyError(
            f"No plugin with plugin_name `{plugin_name}` has been registered!"
        )

    def get_plugin_by_name(self, name: str) -> type:
        """
        Get a plugin by its class name.

        Parameters
        ----------
        name : str
            The class name of the plugin.

        Returns
        -------
        plugin : pydidas.plugins.BasePlugin
            The Plugin class.
        """
        self.verify_is_initialized()
        if name in self.plugins:
            return self.plugins[name]
        if name in self._plugin_basic_types:
            return self._plugin_basic_types[name]
        raise KeyError(f"No plugin with name `{name}` has been registered!")

    def get_all_plugins(self) -> list[type]:
        """
        Get a list of all plugins.

        Returns
        -------
        list
            A list with all the Plugin classes.
        """
        self.verify_is_initialized()
        return list(self.plugins.values())

    def get_all_plugins_of_type(
        self, plugin_type: Literal["base", "input", "proc", "output"]
    ):
        """
        Get all Plugins of a specific type (base, input, proc, or output).

        Parameters
        ----------
        plugin_type : Literal["base", "input", "proc", "output"]
            The type of the demanded plugins.

        Returns
        -------
        list
            A list with all Plugins which have the specified type.
        """
        self.verify_is_initialized()
        if plugin_type == "base":
            return list(self._plugin_basic_types.values())
        _key = {"base": -1, "input": 0, "proc": 1, "output": 2}[plugin_type]
        _res = []
        for _name, _plugin in self.plugins.items():
            if self._plugin_types[_name] == _key:
                _res.append(_plugin)
        return _res

    @property
    def registered_paths(self) -> list[Path]:
        """
        Get all the paths which have been registered in the PluginCollection.

        Returns
        -------
        list[Path]
            The list of all registered paths.
        """
        self.verify_is_initialized()
        return self._plugin_paths[:]

    def unregister_plugin_path(self, path: Union[str, Path]):
        """
        Unregister the given path from the PluginCollection.

        Parameters
        ----------
        path : Union[str, Path]
            The path to the directory containing the plugins.

        Raises
        ------
        UserConfigError
            If the given path is not registered.
        """
        if isinstance(path, str):
            path = Path(path)
        if path not in self._plugin_paths:
            raise UserConfigError(
                f"The given path `{str(path)}` is not registered with the "
                "PluginCollection."
            )
        self._plugin_paths.remove(path)
        self._config["initial_plugin_path"] = list(self._plugin_paths)
        self.q_settings_set(
            "user/plugin_path", ";;".join(str(_path) for _path in self._plugin_paths)
        )
        self.clear_collection(confirmation=True)
        self.verify_is_initialized()

    def unregister_all_paths(self, confirmation: bool = False):
        """
        Unregister all paths.

        Parameters
        ----------
        confirmation : bool, optional
            Confirmation flag to prevent accidentally unregistering all paths. The
            default is False.
        """
        if not confirmation:
            print("Confirmation for unregistering all paths was not given. Aborting...")
            return
        self._config["initial_plugin_path"] = []
        self.q_settings_set("user/plugin_path", None)
        self.clear_collection(True)

    def clear_collection(self, confirmation: bool = False):
        """
        Clear the collection and remove all registered plugins.

        Parameters
        ----------
        confirmation : bool, optional
            Confirmation flag which needs to be True to proceed. The default
            is False.
        """
        if confirmation:
            self.plugins = {}
            self._plugin_types = {}
            self._plugin_names = {}
            self._plugin_paths = []
            self._config["initialized"] = False
            self.sig_updated_plugins.emit()
            return
        print("No confirmation was given: The PluginCollection has not been reset.")
