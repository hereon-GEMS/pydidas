# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The ObjectWithParameterCollection is a serializable (i.e., pickleable) class.

It includes a ParameterCollection object.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ObjectWithParameterCollection"]


import warnings
from copy import copy, deepcopy
from typing import Any, Self

from qtpy import QtCore

from pydidas.core.parameter_collection_mixin import ParameterCollectionMixIn
from pydidas.core.pydidas_q_settings_mixin import PydidasQsettingsMixin


class ObjectWithParameterCollection(
    ParameterCollectionMixIn, PydidasQsettingsMixin, QtCore.QObject
):
    """
    An object with a ParameterCollection.

    This class can be inherited by any class which requires a
    ParameterCollection and access methods defined for it in the
    ParameterCollectionMixIn.

    Note: The logic and code for handling the parameter collection are
    implemented in the ParameterCollectionMixIn class. This is done
    to allow adding the parameter collection to any class with a base class
    other than QObject, e.g., for QWidgets. A duplicate inheritance of
    QObject is not possible.
    """

    def __init__(self, **kwargs: Any) -> None:
        QtCore.QObject.__init__(self, parent=kwargs.get("parent", None))
        PydidasQsettingsMixin.__init__(self)
        ParameterCollectionMixIn.__init__(self)
        self._config: dict[str, Any] = {}

    def __copy__(self) -> Self:
        """
        Create a copy of the object.

        Returns
        -------
        obj : ObjectWithParameterCollection
            The copy with the same state.
        """
        obj = self.__class__()
        obj.params = self.params.copy()
        obj._config = copy(self._config)
        return obj

    def __deepcopy__(self, memo: dict) -> Self:
        """
        Create a deepcopy of the object.

        Parameters
        ----------
        memo : dict
            The copylib's memo dictionary of items already copied.

        Returns
        -------
        obj : ObjectWithParameterCollection
            The copy with the same state.
        """
        obj = self.__class__()
        obj.params = self.params.copy()
        obj._config = deepcopy(self._config)
        return obj

    def __getstate__(self) -> dict:
        """
        Get the ObjectWithParameterCollection state for pickling.

        Returns
        -------
        state : dict
            The state dictionary.
        """
        _state = {"params": self.params.copy(), "_config": copy(self._config)}
        if "shared_memory" in _state["_config"]:
            _state["_config"]["shared_memory"] = {}
        return _state

    def __setstate__(self, state: dict) -> None:
        """
        Set the ObjectWithParameterCollection state from a pickled state.

        Parameters
        ----------
        state : dict
            The pickled state.
        """
        for _key, _value in state.items():
            setattr(self, _key, _value)

    def __hash__(self) -> int:
        """
        Get a hash value.

        The hash value is based on the associated ParameterCollection and
        additional data in the _config dictionary.

        Returns
        -------
        int
            The hash value.
        """
        _param_hash = hash(self.params)
        _config_hash = self.__hash_dict(self._config)
        return hash((_param_hash, _config_hash))

    def __hash_dict(self, item: dict) -> int:
        """
        Get a hash value for a dictionary.

        Parameters
        ----------
        item : dict
            The dictionary to hash.
        """
        if item == {}:
            return 0
        _config_keys = []
        _config_vals = []
        for _key, _val in item.items():
            _config_keys.append(hash(_key))
            try:
                if isinstance(_val, dict):
                    _hash = self.__hash_dict(_val)
                else:
                    if isinstance(_val, list):
                        _val = tuple(_val)
                    _hash = hash(_val)
                _config_vals.append(_hash)
            except TypeError:
                warnings.warn(f'Could not hash the dictionary value "{_val}".')
        return hash((tuple(_config_keys), tuple(_config_vals)))

    def copy(self) -> Self:
        """
        Get a copy of the object.

        Returns
        -------
        ObjectWithParameterCollection :
            The object's copy.
        """
        return copy(self)

    def deepcopy(self) -> Self:
        """
        Get a deepcopy of the object.

        Returns
        -------
        ObjectWithParameterCollection :
            The object's deepcopy.
        """
        return deepcopy(self)
