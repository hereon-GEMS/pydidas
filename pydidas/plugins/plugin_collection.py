# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
information about all Plugins and to get the plugin classwes to instantiate
them.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PluginCollection"]

import importlib
import os
import inspect

from qtpy import QtCore

from ..core import SingletonFactory, PydidasQsettingsMixin
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
        if _plugin_path is None:
            _plugin_path = self.__get_generic_plugin_path()
        self._config = {"initial_plugin_path": _plugin_path, "initialized": False}
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
            _path = [item.strip() for item in _path.split(";;")]
        return _path

    def __get_generic_plugin_path(self):
        """
        Get the generic plugin path(s).

        Returns
        -------
        plugin_path : list
            A list of plugin paths.
        """
        plugin_path = self.get_q_settings_plugin_path()
        if plugin_path == [""] or plugin_path is None:
            plugin_path = get_generic_plugin_path()
        return plugin_path

    def get_q_settings_plugin_path(self):
        """
        Get the plugin path from the global QSettings

        Returns
        -------
        Union[None, list]
            None if not QSettings has been defined, else a list of path
            entries.
        """
        _path = self.q_settings_get_value("global/plugin_path")
        if isinstance(_path, str):
            return _path.split(";;")
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
            self._find_and_register_plugins_in_path(_path, reload)
        self.sig_updated_plugins.emit()

    def _find_and_register_plugins_in_path(self, path, reload=True):
        """
        Find the plugin in a specific path.

        Parameters
        ----------
        path : str
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
        plugin_path : str
            The plugin path as string
        verbose : bool, optional
            Keyword to toggle printed warnings. The default is False
        """
        if plugin_path in self.__plugin_paths:
            if verbose:
                print("Warning. Storing same path again: ", plugin_path)
            return
        if os.path.exists(plugin_path):
            self.__plugin_paths.append(plugin_path)
        _paths = ";;".join(self.__plugin_paths)
        self.q_settings_set_key("global/plugin_path", _paths)

    @staticmethod
    def _get_valid_modules_and_filenames(path):
        """
        Get all module names in a specified path (including subdirectories).

        Parameters
        ----------
        path : str
            The file system path.

        Returns
        -------
        _modules : list
            A list with the module names.
        """
        _files = find_valid_python_files(path)
        _path = path.replace(os.sep, "/")
        _path = _path + (not _path.endswith("/")) * "/"
        _modules = {}
        for _file in _files:
            _file = _file.replace(os.sep, "/")
            _tmpmod = _file.removesuffix(".py").removeprefix(_path)
            _mod = _tmpmod.replace("/", ".")
            _modules[_mod] = _file
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
        self.find_and_register_plugins(*self._config["initial_plugin_path"])
        self._config["initialized"] = True

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
        for _name in self.plugins:
            if self.__plugin_types[_name] == _key:
                _res.append(self.plugins[_name])
        return _res

    def get_all_registered_paths(self):
        """
        Get all the paths which have been registered in the PluginCollection.

        Returns
        -------
        list
            The list of all registered paths.
        """
        self.verify_is_initialized()
        return self.__plugin_paths[:]

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
            self.sig_updated_plugins.emit()
        else:
            print(
                "The confirmation flag was not given. The PluginCollection "
                "has not been reset."
            )


PluginCollection = SingletonFactory(_PluginCollection)
