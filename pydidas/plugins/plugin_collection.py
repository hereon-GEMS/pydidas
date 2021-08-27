# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the PluginCollection Singleton class."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginCollection']

import importlib
import os
import inspect
import sys

from ..core import SingletonFactory, PydidasQsettingsMixin
from ..core.utilities import flatten_list
from .plugin_collection_util_funcs import (
    get_generic_plugin_path, trim_filename,
    plugin_type_check, plugin_consistency_check)


class _PluginCollection(PydidasQsettingsMixin):
    """
    Class to hold references of all plugins
    """
    def __init__(self, **kwargs):
        """
        Setup method.

        Parameters
        ----------
        plugin_path : str, optional
            The search directory for plugins. The default is None.
        """
        plugin_path = kwargs.get('plugin_path', None)
        PydidasQsettingsMixin.__init__(self)
        plugin_paths = self.__process_plugin_path(plugin_path)
        self.plugins = {}
        self.__plugin_type_register = {}
        self.find_plugins(plugin_paths)

    def __process_plugin_path(self, plugin_path):
        """
        Process the plugin path(s) and add them to sys.path.

        Parameters
        ----------
        plugin_path : Union[list, str, None]
            The plugin path as string, a list of paths or None. If None,
            the method will default to the QSettings first and if unsuccessful
            to the generic plugin path.

        Returns
        -------
        plugin_path : list
            A list of plugin paths.
        """
        if not plugin_path:
            plugin_path = self.__get_q_settings_plugin_path()
            if plugin_path is None:
                plugin_path = get_generic_plugin_path()
        plugin_path = ([plugin_path] if isinstance(plugin_path, str)
                       else plugin_path)
        for _path in plugin_path:
            if _path not in sys.path:
                sys.path.insert(0, _path)
        return plugin_path

    def __get_q_settings_plugin_path(self):
        """
        Get the plugin path from the global QSettings

        Returns
        -------
        Union[None, list]
            None if not QSettings has been defined, else a list of path
            entries.
        """
        _path = self.q_settings_get_global_value('plugin_path')
        if _path is not None:
            return _path.split(';;')
        return _path

    def find_plugins(self, plugin_paths, reload=True):
        """
        Find plugins in the given paths.

        Parameters
        ----------
        path : str
            The file system search path.
        reload : bool, optional
            Flag to handle reloading of plugins if a plugin with an identical
            name is encountered. If False, these plugins will be skipped.
        """
        for _path in plugin_paths:
            self.__find_plugins_in_path(_path, reload)

    def __find_plugins_in_path(self, path, reload=True):
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
        _modules = self.get_modules(path)
        for _mod in _modules:
            spec = importlib.util.find_spec(_mod)
            _m = spec.loader.load_module()
            clsmembers = inspect.getmembers(_m, inspect.isclass)
            for _name, _cls in clsmembers:
                self.__check_and_register_class(_cls, reload)
            del _m

    def get_modules(self, path):
        """
        Get all module names in a specified path (including subdirectories)

        Parameters
        ----------
        path : str
            The file system path.

        Returns
        -------
        _modules : list
            A list with the module names.
        """
        _files = self.find_files(path)
        _path = path.replace(os.sep, '/')
        _path = _path + (not _path.endswith('/')) * '/'
        _modules = []
        for _file in _files:
            _file = _file.replace(os.sep, '/')
            _tmpmod = _file.removesuffix('.py').removeprefix(_path)
            _mod = _tmpmod.replace('/', '.')
            _modules.append(_mod)
        return _modules

    def find_files(self, path):
        """
        Search for all python files in path and subdirectories.

        This method will search the specified path recursicely for all
        python files, defined as files with a .py extension.
        It will ignore protected files /directories (starting with "__")
        and hidden files / directories (starting with ".").

        Parameters
        ----------
        path : str
            The file system path to search.
        rel_path : str
            The relative path (if recursing). Default is None.

        Returns
        -------
        list
            A list with the full filesystem path of python files in the
            directory and its subdirectories.
        """
        path = trim_filename(path)
        _entries = [os.path.join(path, item) for item in os.listdir(path)
                    if not (item.startswith('__') or item.startswith('.'))]
        _dirs = [item for item in _entries if os.path.isdir(item)]
        _files = [item for item in _entries if os.path.isfile(item)]
        _results = flatten_list(
            [self.find_files(os.path.join(path, entry)) for entry in _dirs])
        _results += [f for f in _files if f.endswith('.py')]
        return _results

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
        if not plugin_consistency_check(class_):
            return
        if class_.__name__ not in self.plugins:
            self.__add_new_class(class_)
        elif reload:
            self.__remove_old_item(class_)
            self.__add_new_class(class_)

    def __add_new_class(self, class_):
        """
        Add a new class to the collection.

        Parameters
        ----------
        name : str
            The registration name
        class_ : type
            The class object.
        """

        self.plugins[class_.__name__] = class_
        self.__plugin_type_register[class_.__name__] = plugin_type_check(class_)

    def __remove_old_item(self, class_):
        """
        Remove an old item from the collection.

        Note: If a class with the same class name is reloaded but has been
        registered to a different name, this is removed as well.

        Parameters
        ----------
        name : str
            The reference name of the Plugin.
        class_ : type
            The class object.
        """
        if class_.__name__ in self.plugins:
            del self.plugins[class_.__name__]
            del self.__plugin_type_register[class_.__name__]

    def get_all_plugin_names(self):
        """
        Get a list of all the plugin names currently registered.

        Returns
        -------
        names : list
            The list of all the plugin names.
        """
        return list(self.plugins.keys())

    def get_plugin_by_name(self, name):
        """
        Get a plugin by its plugin name.

        Parameters
        ----------
        name : str
            The name of the plugin.

        Returns
        -------
        plugin : pydidas.plugins.BasePlugin
            The Plugin class.
        """
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
        _key = {'base': -1, 'input': 0, 'proc': 1, 'output': 2}[plugin_type]
        _res = []
        for _name in self.plugins:
            if self.__plugin_type_register[_name] == _key:
                _res.append(self.plugins[_name])
        return _res

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
            self.__plugin_type_register = {}

PluginCollection = SingletonFactory(_PluginCollection)
