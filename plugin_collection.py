# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:13:34 2021

@author: ogurreck
"""
import importlib
import os
import inspect
import sys
import plugins.base_plugins as base_plugins

class PluginCollection:
    """
    Class to hold references of all plugins
    """

    def __init__(self, plugin_path=None):
        """
        Setup method.

        Parameters
        ----------
        directory : str, optional
            The search directory for plugins. The default is None.

        Returns
        -------
        None.

        """
        if not plugin_path:
            plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
        self.plugins = {}
        self.plugins['base'] = {}
        self.plugins['proc'] = {}
        self.plugins['input'] = {}
        self.plugins['output'] = {}
        self.find_plugins(plugin_path)

    def find_files(self, path):
        """
        Search for all python files in path.

        This method will search the specified path recursicely for all
        python files.

        Parameters
        ----------
        path : str
            The file system path to search.
        rel_path : str
            The relative path (if recursing). Default is None.

        Returns
        -------
        None.

        """
        path = path if not os.path.isfile(path) else os.path.dirname(path)
        _results = []
        _entries = [os.path.join(path, item) for item in os.listdir(path)
                   if (item[:2] != '__' and item[0] != '.')]
        _dirs = [item for item in _entries if os.path.isdir(item)]
        _files = [item for item in _entries if os.path.isfile(item)]
        for entry in _dirs:
            _results += self.find_files(os.path.join(path, entry))
        _results += [item for item in _files
                     if (item[:2] != '__' and item[0] != '.' and
                         item[-3:] == '.py')]
        return _results

    def find_plugins(self, path, reload=True):
        """
        Find plugins in the specified path.

        Parameters
        ----------
        path : str
            The file system search path.
        reload : bool
            Keyword to toggle reloading of plugins. Default is True.

        Returns
        -------
        None.

        """
        _modules = [item[len(path)+len(os.sep):-3].replace(os.sep, '.')
                  for item in self.find_files(path)]
        if len(_modules) == 0:
            return
        for _mod in _modules:
            spec = importlib.util.find_spec(_mod)
            _m = spec.loader.load_module()
            clsmembers = inspect.getmembers(_m, inspect.isclass)
            for _name, _cls in clsmembers:
                if not self.plugin_consistency_check(_cls):
                    continue
                if (_cls.basic_plugin and
                    (_name not in self.plugins['base'] or reload)):
                    self.plugins['base'][_name] = _cls
                for ptype, key in [[base_plugins.INPUT_PLUGIN, 'input'],
                                   [base_plugins.PROC_PLUGIN, 'proc'],
                                   [base_plugins.OUTPUT_PLUGIN, 'output']]:
                    if (not _cls.basic_plugin and
                        _cls.plugin_type == ptype and
                        (_name not in self.plugins[key] or reload)):
                        self.plugins[key][_name] = _cls
            del _m

    @staticmethod
    def plugin_consistency_check(cls_item):
        """
        Verify that plugins pass a rudimentary sanity check.

        Parameters
        ----------
        cls_item : plugin object
            A plugin object.

        Returns
        -------
        bool.
            Returns True if consistency check succeeded and False otherwise.
        """
        if (hasattr(cls_item, 'basic_plugin') and
            hasattr(cls_item, 'plugin_type') and
            hasattr(cls_item, 'execute')):
            return True
        return False
