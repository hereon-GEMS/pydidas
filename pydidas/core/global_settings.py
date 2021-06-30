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

"""Module with the _GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['_GlobalSettings']

from PyQt5 import QtCore

from pydidas.core.singleton_factory import SingletonFactory


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
        """
        if key in self._params:
            raise KeyError(f'Key {key} is already registered with '
                           '_GlobalSettings.')
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
                           '_GlobalSettings!')
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
        """
        if key not in self._params:
            raise KeyError(f'The key {key} is not registered with '
                           '_GlobalSettings!')
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
                           '_GlobalSettings!')
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


GlobalSettings = SingletonFactory(_GlobalSettings)
