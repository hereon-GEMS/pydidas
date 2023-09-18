# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the PluginCollection Singleton class which is used for storing
information about all Plugins and to get the plugin classes to instantiate
them.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PluginCollection", "get_generic_plugin_path"]

import importlib
import inspect
from pathlib import Path

from qtpy import QtCore

from ..core import PydidasQsettingsMixin, SingletonFactory, UserConfigError
from ..core.utils import find_valid_python_files
from .plugin_collection_util_funcs import get_generic_plugin_path, plugin_type_check


class _PluginCollection(QtCore.QObject, PydidasQsettingsMixin):
    """
    Class to hold references of all plugins
    """

    sig_updated_plugins = QtCore.Signal()

    def __init__(self, **kwargs):
        """
        Setup method.

        Parameters
        ----------
        plugin_path : Union[str, list], optional
            The search directory for plugins. A single path can be supplies
            as string. Multiple paths can be supplied in a single string
            separated by ";;" or as a list. None will call to the default
            paths. The default is None.
        """
        QtCore.QObject.__init__(self)
        self.plugins = {}
        self.__plugin_types = {}
        self.__plugin_names = {}
        self.__plugin_paths = []
        PydidasQsettingsMixin.__init__(self)
        _plugin_path = self.__get_plugin_path_from_kwargs(**kwargs)
        self._config = {
            "initial_plugin_path": _plugin_path,
            "initialized": False,
            "must_emit_signal": False,
        }
        if kwargs.get("force_initialization", False):
            self.verify_is_initialized()

    @staticmethod
    def __get_plugin_path_from_kwargs(**kwargs):
        """
        Get the plugin path(s) from the calling keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            The calling keyword arguments

        Returns
        -------
        _path : Union[list, None]
            The plugin paths. If None, no paths have been specified.
        """
        _path = kwargs.get("plugin_path", None)
        if isinstance(_path, str):
            _path = [Path(item.strip()) for item in _path.split(";;") if item != ""]
        if isinstance(_path, Path):
            _path = [_path]
        return _path

    def __get_generic_plugin_paths(self):
        """
        Get the generic plugin path(s).

        Returns
        -------
        plugin_paths : list
            A list of plugin paths.
        """
        plugin_paths = self.get_q_settings_plugin_paths()
        if plugin_paths == [Path()] or plugin_paths is None:
            plugin_paths = get_generic_plugin_path()
        return plugin_paths

    def get_q_settings_plugin_paths(self):
        """
        Get the plugin path from the global QSettings

        Returns
        -------
        Union[None, list]
            None if not QSettings has been defined, else a list of path
            entries.
        """
        _path = self.q_settings_get("user/plugin_path")
        if isinstance(_path, str):
            return [Path(_key) for _key in _path.split(";;")]
        if isinstance(_path, Path):
            return [_path]
        return _path

    def find_and_register_plugins(self, *plugin_paths, reload=True):
        """
        Find plugins in the given path(s) and register them in the
        PluginCollection.

        Parameters
        ----------
        plugin_paths : tuple
            Any number of file system paths in string format.
        reload : bool, optional
            Flag to handle reloading of plugins if a plugin with an identical
            name is encountered. If False, these plugins will be skipped.
        """
        for _path in plugin_paths:
            if isinstance(_path, str):
                _path = Path(_path)
            if _path != Path():
                self._find_and_register_plugins_in_path(_path, reload)
        if self._config["initialized"]:
            self.sig_updated_plugins.emit()
        else:
            self._config["must_emit_signal"] = True

    def _find_and_register_plugins_in_path(self, path, reload=True):
        """
        Find the plugin in a specific path.

        Parameters
        ----------
        path : pathlib.Path
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
                self.__check_and_register_class(_cls, reload)

    def _store_plugin_path(self, plugin_path, verbose=False):
        """
        Store the plugin path.

        Parameters
        ----------
        plugin_path : pathlib.Path
            The plugin path.
        verbose : bool, optional
            Keyword to toggle printed warnings. The default is False
        """
        if plugin_path in self.__plugin_paths:
            if verbose:
                print("Warning. Storing same path again: {str(plugin_path)}")
            return
        if plugin_path.exists():
            self.__plugin_paths.append(plugin_path)
        _paths = ";;".join(str(_path) for _path in self.__plugin_paths)
        self.q_settings_set("user/plugin_path", _paths)

    @staticmethod
    def _get_valid_modules_and_filenames(path):
        """
        Get all module names in a specified path (including subdirectories).

        Parameters
        ----------
        path : Union[str, pathlib.Path]
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
    def __get_classes_in_module(modname, filepath):
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
        clsmembers : tuple
            A tuple of the class members with entries for each class in the
            form of (name, class).
        """
        spec = importlib.util.spec_from_file_location(modname, filepath)
        tmp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tmp_module)
        clsmembers = inspect.getmembers(tmp_module, inspect.isclass)
        del spec, tmp_module
        return clsmembers

    def __check_and_register_class(self, class_, reload=False):
        """
        Check whether a class is a valid plugin and register it.

        Parameters
        ----------
        name : str
            The class description name
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
        if class_.__name__ not in self.plugins:
            self.__add_new_class(class_)
        elif reload:
            self.__remove_plugin_from_collection(class_)
            self.__add_new_class(class_)

    def __add_new_class(self, class_):
        """
        Add a new class to the collection.

        Parameters
        ----------
        class_ : type
            The class object.
        """
        if class_.plugin_name in self.__plugin_names:
            _old_cls = self.__plugin_names[class_.plugin_name]
            _message = (
                "A different class with the same plugin name "
                f'"{class_.plugin_name}" has already been registered.'
                " Adding this class would destroy the consistency of "
                "the PluginCollection: "
                f"Registered class: {_old_cls}; New class: {class_}"
            )
            raise KeyError(_message)
        self.plugins[class_.__name__] = class_
        self.__plugin_types[class_.__name__] = plugin_type_check(class_)
        self.__plugin_names[class_.plugin_name] = class_.__name__

    def __remove_plugin_from_collection(self, class_):
        """
        Remove a Plugin from the PluginCollection.

        Parameters
        ----------
        class_ : type
            The class object to be removed.
        """
        if class_.__name__ in self.plugins:
            del self.plugins[class_.__name__]
            del self.__plugin_types[class_.__name__]
            del self.__plugin_names[class_.plugin_name]

    def verify_is_initialized(self):
        """
        Verify that the PluginCollection is initialized and that the default
        plugin paths have been processed.

        This method is called internally in every public method to make sure
        that the PluginCollection is always initialized before any user
        interaction occurs.
        """
        if self._config["initialized"]:
            return
        _plugin_path = (
            self._config["initial_plugin_path"]
            if self._config["initial_plugin_path"] is not None
            else self.__get_generic_plugin_paths()
        )
        self.find_and_register_plugins(*_plugin_path)
        self._config["initialized"] = True
        if self._config["must_emit_signal"]:
            self.sig_updated_plugins.emit()

    def get_all_plugin_names(self):
        """
        Get a list of all the plugin names currently registered.

        Returns
        -------
        names : list
            The list of all the plugin names.
        """
        self.verify_is_initialized()
        return list(self.plugins.keys())

    def get_plugin_by_plugin_name(self, plugin_name):
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
        if plugin_name in self.__plugin_names:
            return self.plugins[self.__plugin_names[plugin_name]]
        raise KeyError(
            f'No plugin with plugin_name "{plugin_name}" has been' " registered!"
        )

    def get_plugin_by_name(self, name):
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
        raise KeyError(f'No plugin with name "{name}" has been registered!')

    def get_all_plugins(self):
        """
        Get a list of all plugins.

        Returns
        -------
        list
            A list with all the Plugin classes.
        """
        self.verify_is_initialized()
        return list(self.plugins.values())

    def get_all_plugins_of_type(self, plugin_type):
        """
        Get all Plugins of a specific type (base, input, proc, or output).

        Parameters
        ----------
        plugin_type : str, any of 'base', 'input', proc', 'output'
            The type of the demanded plugins.

        Returns
        -------
        list :
            A list with all Plugins which have the specified type.
        """
        self.verify_is_initialized()
        _key = {"base": -1, "input": 0, "proc": 1, "output": 2}[plugin_type]
        _res = []
        for _name, _plugin in self.plugins.items():
            if self.__plugin_types[_name] == _key:
                _res.append(_plugin)
        return _res

    @property
    def registered_paths(self):
        """
        Get all the paths which have been registered in the PluginCollection.

        Returns
        -------
        list
            The list of all registered paths.
        """
        self.verify_is_initialized()
        return self.__plugin_paths[:]

    def unregister_plugin_path(self, path):
        """
        Unregister the given path from the PluginCollection.

        Parameters
        ----------
        path : Union[str, pathlib.Path]
            The path to the directory containing the plugins.

        Raises
        ------
        UserConfigError
            If the given path is not registered.
        """
        if isinstance(path, str):
            path = Path(path)
        if path not in self.__plugin_paths:
            raise UserConfigError(
                f"The given path '{str(path)}' is not registered with the "
                "PluginCollection."
            )
        self.__plugin_paths.remove(path)
        self._config["initial_plugin_path"] = list(self.__plugin_paths)
        self.clear_collection(confirmation=True)
        self.verify_is_initialized()

    def unregister_all_paths(self, confirmation=False):
        """
        Unregister all paths.

        Parameters
        ----------
        confirmation : bool, optional
            Confirmation flag to prevent accidentially unregistering all paths. The
            default is False.
        """
        if not confirmation:
            print("Confirmation for unregistering all paths was not given. Aborting...")
            return
        self.q_settings_set("user/plugin_path", None)
        self.clear_collection(True)

    def clear_collection(self, confirmation=False):
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
            self.__plugin_types = {}
            self.__plugin_names = {}
            self.__plugin_paths = []
            self._config["initialized"] = False
            self.sig_updated_plugins.emit()
        else:
            print(
                "The confirmation flag was not given. The PluginCollection "
                "has not been reset."
            )


PluginCollection = SingletonFactory(_PluginCollection)
