# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the SingletonContextObject
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SingletonContextObject"]


from copy import copy
from typing import Type

from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter_collection_mixin import ParameterCollectionMixIn


class SingletonContextObject:
    """
    Class which includes the necessary code to create classes only as Singletons.

    Implementations must inherit from the ObjectWithParameterCollection class.

    FOR THE CORRECT METHOD RESOLUTION ORDER, THE IMPLEMENTED CLASS *MUST*
    INHERIT FROM THE SingletonContextObject CLASS *FIRST*.
    """

    _instance = None
    _initialized = False
    non_context_class = ObjectWithParameterCollection

    @classmethod
    @property
    def instance(cls) -> Type:
        """
        Get the instance of the singleton object.

        Returns
        -------
        SingletonContextObject
            The instance of the singleton object.
        """
        return cls._instance

    def __new__(cls):
        """Create a new instance of the class if it does not exist yet."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if not isinstance(cls._instance, ParameterCollectionMixIn):
            raise TypeError("The class must inherit from ParameterCollectionMixIn.")
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.__class__._initialized = True
        self.non_context_class.__init__(self)

    def __copy__(self) -> object:
        """
        Return a copy of the non-context class instance.

        Returns
        -------
        obj :
            The copy of the non-context class with the same state.
        """
        obj = self.non_context_class()
        obj.params = self.params.copy()
        obj._config = copy(self._config)
        return obj
