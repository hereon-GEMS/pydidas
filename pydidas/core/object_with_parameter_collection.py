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
The ObjectWithParameterCollection is a class which includes a
ParameterCollection and is serializable (ie. pickleable).
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ObjectWithParameterCollection']

import warnings
from copy import copy

from qtpy import QtCore

from .parameter_collection import ParameterCollection
from .pydidas_q_settings_mixin import PydidasQsettingsMixin
from .parameter_collection_mixin import ParameterCollectionMixIn


class ObjectWithParameterCollection(
        ParameterCollectionMixIn, PydidasQsettingsMixin, QtCore.QObject):
    """
    An object with a ParameterCollection.

    This class can be inherited by any class which requires a
    ParameterCollection and access methods defined for it in the
    ParameterCollectionMixIn.
    """
    def __init__(self):
        PydidasQsettingsMixin.__init__(self)
        QtCore.QObject.__init__(self)
        self.params = ParameterCollection()
        self._config = {}

    def __copy__(self):
        """
        Create a copy of the object.

        Returns
        -------
        fm : ObjectWithParameterCollection
            The copy with the same state.
        """
        obj = self.__class__()
        obj.params = self.params.get_copy()
        obj._config = copy(self._config)
        return obj

    def __getstate__(self):
        """
        Get the ObjectWithParameterCollection state for pickling.

        Returns
        -------
        state : dict
            The state dictionary.
        """
        _state = {'params': self.params.get_copy(),
                  '_config': copy(self._config)}
        return _state

    def __setstate__(self, state):
        """
        Set the ObjectWithParameterCollection state from a pickled state.

        Parameters
        ----------
        state : dict
            The pickled state.
        """
        for _key, _value in state.items():
            setattr(self, _key, _value)

    def __hash__(self):
        """
        Get a hash value.

        The hash value is based on the associated ParameterCollection and
        additional data in the _config dictionary.

        Returns
        -------
        int
            The hash value.
        """
        _config_keys = []
        _config_vals = []
        _param_hash = hash(self.params)
        for _key, _val in self._config.items():
            _config_keys.append(hash(_key))
            try:
                _hash = hash(_val)
                _config_vals.append(_hash)
            except TypeError:
                warnings.warn(f'Could not hash the dictionary value "{_val}".')
        return hash((_param_hash, tuple(_config_keys), tuple(_config_vals)))
