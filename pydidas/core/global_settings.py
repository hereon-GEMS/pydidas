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

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalSettings']

from PyQt5 import QtCore


class _GlobalSettings(QtCore.QObject):
    """
    Class which holds global settings. This class must only be instanciated
    through its factory, therefore guaranteeing that only a single instance
    exists.
    """
    def __init__(self, **kwargs):
        """Setup method"""
        self._params = {}

    def register_param(self, key, default_entry=None):
        """
        Register a parameter.

        This method registers a parameter key and sets a default_entry, if
        supplid. The default entry can be any object and no type checking
        is implemented. It is the responsibility of the individual frames
        and processes who write and read data to verify that the data format
        is correct.

        Parameters
        ----------
        key : str
            The reference key for this parameter.
        default_entry : object, optional
            The default value for this key. The default is None.

        Raises
        ------
        KeyError
            If the key already exists.

        Returns
        -------
        None.
        """
        if key in self._params:
            raise KeyError(f'Key {key} is already registered with '
                           'GlobalSettings.')
        self._params[key] = default_entry

    def is_set(self, key):
        """
        Check if the key exists and the entry is not empty.

        Parameters
        ----------
        key : str
            The reference key for this parameter.

        Returns
        -------
        bool
            The flag whether the key exists and its value is not None.
        """
        if key in self._params and self._params[key] is not None:
            return True
        return False

    def key_exists(self, key):
        """
        Check if the key exists.

        Parameters
        ----------
        key : str
            The reference key for this parameter.

        Returns
        -------
        bool
            The flag whether the key exists.
        """
        if key in self._params:
            return True
        return False


    def get_param(self, key):
        """
        Read method to return the Parameter for the given key.

        Parameters
        ----------
        key : str
            The reference key for this parameter.

        Raises
        ------
        KeyError
            If the key does not exist.

        Returns
        -------
        object
            The Parameter stored for the reference key.
        """
        if key not in self._params:
            raise KeyError(f'The key {key} is not registered with '
                           'GlobalSettings!')
        return self._params[key]

    def set(self, key, value):
        """
        Set a parameter value.

        Parameters
        ----------
        key : str
            The parameter identifier key.
        value : object
            The new value for the parameter. Depending upon the parameter,
            value can take any form (number, string, object, ...).

        Raises
        ------
        KeyError
            If the key does not exist.

        Returns
        -------
        None.
        """
        if key not in self._params:
            raise KeyError(f'The key {key} is not registered with '
                           'GlobalSettings!')
        self._params[key].value = value

    def get(self, key):
        """
        Read method to return the Parameter value for the given key.

        Parameters
        ----------
        key : str
            The reference key for this parameter.

        Raises
        ------
        KeyError
            If the key does not exist.

        Returns
        -------
        object
            The value stored for the Parameter referenced by key.
        """
        if key not in self._params:
            raise KeyError(f'The key {key} is not registered with '
                           'GlobalSettings!')
        return self._params[key].value

    def get_all_keys(self):
        """
        Get all registered keys.

        Returns
        -------
        keys : list
            A list of all the keys which are registered.
        """
        return list(self._params.keys())

    def get_all_refkeys(self):
        """
        Get the reference keys for all registered parameters.

        Returns
        -------
        list
            A list with all the reference keys of all registered parameters.
        """
        _list = []
        for key in self._params:
            _list.append(self._params[key].refkey)
        return _list


class _GlobalSettingsFactory:
    """
    Factory to create a Singleton.
    """
    def __init__(self):
        """
        Setup method.
        """
        self._instance = None

    def __call__(self):
        """
        Get the instance of GlobalSettings

        Returns
        -------
        GlobalSettings
            The instance of the GlobalSettings class.
        """
        if not self._instance:
            self._instance = _GlobalSettings()
        return self._instance


GlobalSettings = _GlobalSettingsFactory()
